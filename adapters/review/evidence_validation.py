"""Portable Review evidence validation shared by subprocess and host-agent adapters.

This checks scope, completeness and verdict consistency. It does not prove
reviewer identity or isolation: the protected PR gate verifies those separately.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from git_scope import GitScopeError, git_inventory

MAX_EVIDENCE_BYTES = 4 * 1024 * 1024


class EvidenceError(Exception):
    """Missing, contradictory or stale Review evidence."""


def read_json(path: Path) -> dict[str, Any]:
    try:
        if path.stat().st_size > MAX_EVIDENCE_BYTES:
            raise EvidenceError("review evidence/context exceeds size limit")
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as exc:
        raise EvidenceError("cannot read review evidence/context JSON") from exc
    if not isinstance(value, dict):
        raise EvidenceError("review evidence/context must be a JSON object")
    return value


def review_paths(items: Any, name: str) -> set[str]:
    if not isinstance(items, list):
        raise EvidenceError(f"{name} is missing or is not an array")
    result: set[str] = set()
    for item in items:
        path = item if isinstance(item, str) else item.get("path") if isinstance(item, dict) else None
        if not isinstance(path, str) or not path or path in result:
            raise EvidenceError(f"{name} contains invalid or duplicate paths")
        result.add(path)
    return result


def assert_target_fresh(context: dict[str, Any], repo: Path) -> None:
    scope = context.get("scope")
    if not isinstance(scope, dict):
        raise EvidenceError("unfrozen review scope")
    if not isinstance(context.get("repository"), str) or Path(context["repository"]).resolve() != repo.resolve():
        raise EvidenceError("review context refers to a different repository")
    try:
        current = git_inventory(
            repo=repo.resolve(), timeout=30, from_ref=scope.get("base_ref"),
            to_ref=scope.get("head_ref"), commit_ref=scope.get("commit_ref"),
            base_branch=scope.get("base_branch"),
        )
    except (GitScopeError, OSError, ValueError) as exc:
        raise EvidenceError("cannot establish current Git target") from exc
    if current["target"] != context.get("target") or current["changed_files"] != context.get("changed_files"):
        raise EvidenceError("Git target or workspace fingerprint changed during review")


def validate_evidence(evidence: dict[str, Any], context: dict[str, Any], repo: Path) -> dict[str, Any]:
    """Same fail-closed validation for subprocess and agent-as-reviewer modes."""
    assert_target_fresh(context, repo)
    if not isinstance(evidence, dict):
        raise EvidenceError("reviewer evidence must be a JSON object")
    verdict = evidence.get("review_status")
    if verdict not in ("PASS", "FAIL", "INCOMPLETE"):
        raise EvidenceError("reviewer did not supply a valid review_status")
    if evidence.get("target") != context["target"]:
        raise EvidenceError("review result refers to a different base/head or scope")
    expected = review_paths(context["changed_files"], "bootstrap.changed_files")
    declared = review_paths(evidence.get("changed_files"), "review.changed_files")
    if declared != expected:
        raise EvidenceError("reviewer's changed-file inventory does not match bootstrap")
    reviewed = review_paths(evidence.get("reviewed_files"), "review.reviewed_files")
    unreviewed = review_paths(evidence.get("unreviewed_files"), "review.unreviewed_files")
    if not reviewed <= expected or not unreviewed <= expected:
        raise EvidenceError("reviewer declared out-of-scope files")
    profile = context.get("review_profile", "advisory")
    if profile not in ("advisory", "gate"):
        raise EvidenceError("unknown review profile")
    declared_profile = evidence.get("review_profile", profile if profile == "advisory" else None)
    if declared_profile != profile:
        raise EvidenceError("review_profile mismatches frozen review context")
    if verdict == "PASS" and profile == "gate" and evidence.get("reviewer_independent") is not True:
        raise EvidenceError("gate PASS requires affirmative reviewer independence")
    findings = evidence.get("findings", [])
    blockers = evidence.get("blocking_findings", [])
    if not isinstance(findings, list):
        raise EvidenceError("findings must be an array")
    if not isinstance(blockers, list):
        raise EvidenceError("blockers must be an array")
    for item in findings + blockers:
        if not isinstance(item, dict):
            raise EvidenceError("finding must be an object")
        likelihood = item.get("likelihood")
        if likelihood is not None and likelihood not in ("high", "medium", "low"):
            raise EvidenceError("likelihood must be high, medium or low")
        origin = item.get("origin")
        if origin is not None and origin not in (
            "introduced", "pre-existing", "amplified-pre-existing"
        ):
            raise EvidenceError("invalid finding origin")
        if origin == "amplified-pre-existing" and (
            not item.get("amplification_reason")
            or item.get("disposition") not in ("fix", "decision-needed")
        ):
            raise EvidenceError("amplified-pre-existing risk requires justification and fix/decision-needed")
    external = evidence.get("external_evidence", [])
    if not isinstance(external, list):
        raise EvidenceError("external_evidence must be an array")
    for item in external:
        if (not isinstance(item, dict) or not isinstance(item.get("repository"), str)
                or not item["repository"].strip() or not isinstance(item.get("sha"), str)
                or len(item["sha"]) not in (40, 64)
                or any(c not in "0123456789abcdefABCDEF" for c in item["sha"])
                or not isinstance(item.get("files"), list)
                or not item["files"]
                or not isinstance(item.get("claim_supported"), str)
                or not item["claim_supported"].strip()):
            raise EvidenceError("external_evidence needs repository, pinned SHA, files and claim_supported")
    blockers = evidence.get("blocking_findings", [])
    questions = evidence.get("unresolved_questions", [])
    if not isinstance(blockers, list) or not isinstance(questions, list):
        raise EvidenceError("blockers/questions must be arrays")
    material_questions = any(
        not isinstance(question, dict) or question.get("material") is not False
        for question in questions
    )
    if verdict == "FAIL" and any(item.get("lead_confirmed") is not True for item in blockers):
        raise EvidenceError("confirmed blocking finding requires lead_confirmed=true and direct source inspection")
    if verdict == "PASS":
        if (evidence.get("coverage_status") != "complete" or reviewed != expected
                or unreviewed or blockers or material_questions):
            raise EvidenceError("reviewer claimed PASS without complete native review evidence/coverage")
    if verdict == "INCOMPLETE" and blockers:
        raise EvidenceError("confirmed blockers take precedence as FAIL; retain unresolved questions")
    if verdict == "FAIL" and not blockers:
        raise EvidenceError("FAIL requires blocking findings")
    plan = context.get("team_plan")
    if plan is not None:
        if evidence.get("review_id") != plan.get("review_id") or evidence.get("risk_profile") != plan.get("risk_profile"):
            raise EvidenceError("reviewer omitted frozen team or risk identity")
        if verdict == "PASS":
            if profile == "gate" and (
                plan.get("lead_implemented_change") or evidence.get("reviewer_independent") is not True
            ):
                raise EvidenceError("implementer/self-review cannot claim an independent PASS")
            mode = evidence.get("execution_mode")
            if plan["execution_mode"] == "team-relayed":
                members = evidence.get("team_members")
                if not isinstance(members, list) or len(members) != len(plan["selected_roles"]):
                    raise EvidenceError("missing isolated specialist Task evidence")
                actual = {m.get("role") for m in members if isinstance(m, dict) and m.get("task_id")}
                if actual != set(plan["selected_roles"]):
                    raise EvidenceError("missing isolated specialist Task IDs")
                coordination = evidence.get("coordination")
                if not isinstance(coordination, dict):
                    raise EvidenceError("missing collaboration transport evidence")
                if mode == "team-live":
                    if not coordination.get("real_peer_delivery_observed") or not evidence.get("peer_threads"):
                        raise EvidenceError("team-live requires observed direct peer exchange")
                elif mode != "team-relayed" or coordination.get("transport") not in (
                    "Task+resume", "Task+new Task", "Task (no relay needed)",
                ):
                    raise EvidenceError("team-relayed lacks Task/relay provenance")
            elif mode != "native-solo":
                raise EvidenceError("reviewer claimed team without available Task support")
            if plan["risk_profile"] == "R3":
                verified = evidence.get("independent_verification")
                if not isinstance(verified, dict):
                    raise EvidenceError("R3 lacks source verification")
                if plan["execution_mode"] == "team-relayed":
                    if verified.get("mode") != "isolated-agent" or not verified.get("task_id"):
                        raise EvidenceError("R3 with Tasks requires isolated verifier")
                elif verified.get("mode") != "native-second-pass" or not verified.get("source_evidence"):
                    raise EvidenceError("R3 native review requires source-based second pass")
    # Reviewer-supplied helper metadata is never trusted as execution history.
    evidence = dict(evidence)
    evidence["review_profile"] = profile
    evidence["optional_helpers"] = context["optional_helpers"]
    ocr_status = context["optional_helpers"]["ocr"]["status"]
    evidence["review_preparation"] = {
        "mode": "native-only" if ocr_status == "disabled" else "ocr-first" if ocr_status == "available" else "native-fallback",
        "git_inventory_size": len(expected),
        "execution_adapter": context.get("preparation_adapter", "host-equivalent"),
    }
    assert_target_fresh(context, repo)
    return {
        "kind": "review-invocation", "review_status": verdict,
        "review_profile": profile,
        "review_label": f"{verdict} (advisory)" if profile == "advisory" else verdict,
        "review_evidence": evidence, "native_full_scope": sorted(expected),
        "pre_pr_review_independence_verified": False,
        "note": "A separate protected PR gate verifies signed reviewer identity and independence.",
    }
