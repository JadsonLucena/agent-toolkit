#!/usr/bin/env python3
"""Host entrypoint for /review/review-code: OCR-first preparation, then review.

The provider-approved reviewer command receives the complete JSON context on
stdin. This entrypoint is not a model and cannot independently perform a review.
No shell, installation, Git write or remote PR operation is performed here.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from prepare_context import prepare_context
from git_scope import GitScopeError, git_inventory
from team_orchestration import TeamPlanningError, freeze

MAX_RESULT_BYTES = 4 * 1024 * 1024


class ReviewInvocationError(Exception):
    """Cannot safely dispatch or reconcile a review."""


def review_paths(items: Any, name: str) -> set[str]:
    if not isinstance(items, list):
        raise ReviewInvocationError(f"{name} is missing or is not an array")
    result: set[str] = set()
    for item in items:
        value = item if isinstance(item, str) else item.get("path") if isinstance(item, dict) else None
        if not isinstance(value, str) or not value or value in result:
            raise ReviewInvocationError(f"{name} contains invalid or duplicate paths")
        result.add(value)
    return result


def assert_target_fresh(context: dict[str, Any], repo: Path) -> None:
    scope = context.get("scope")
    if not isinstance(scope, dict):
        raise ReviewInvocationError("unfrozen review scope")
    current = git_inventory(
        repo=repo.resolve(), timeout=30, from_ref=scope.get("base_ref"),
        to_ref=scope.get("head_ref"), commit_ref=scope.get("commit_ref"),
    )
    if current["target"] != context["target"] or current["changed_files"] != context["changed_files"]:
        raise ReviewInvocationError("Git target or workspace fingerprint changed during review")


def dispatch(
    context: dict[str, Any], *, repo: Path, reviewer_command: list[str],
    timeout: int = 300,
) -> dict[str, Any]:
    if not reviewer_command or not reviewer_command[0] or timeout < 1 or timeout > 3600:
        raise ReviewInvocationError("approved host reviewer command and bounded timeout are required")
    # Preparation and, where requested, risk/team planning happen before any
    # host reviewer may spawn subagents.
    assert_target_fresh(context, repo)
    request = json.dumps(context, ensure_ascii=False).encode("utf-8")
    try:
        result = subprocess.run(
            reviewer_command, cwd=repo.resolve(), input=request,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ReviewInvocationError(f"reviewer unavailable or timed out: {type(exc).__name__}") from exc
    if len(result.stdout) > MAX_RESULT_BYTES:
        raise ReviewInvocationError("reviewer result exceeds size limit")
    if result.returncode:
        raise ReviewInvocationError(f"reviewer failed with exit code {result.returncode}")
    try:
        evidence = json.loads(result.stdout.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as exc:
        raise ReviewInvocationError("reviewer returned invalid JSON evidence") from exc
    if not isinstance(evidence, dict):
        raise ReviewInvocationError("reviewer result must be a JSON object")
    verdict = evidence.get("review_status")
    if verdict not in ("PASS", "FAIL", "INCOMPLETE"):
        raise ReviewInvocationError("reviewer did not supply a valid review_status")
    target = evidence.get("target")
    if target != context["target"]:
        raise ReviewInvocationError("review result refers to a different base/head or scope")
    expected = review_paths(context["changed_files"], "bootstrap.changed_files")
    declared = review_paths(evidence.get("changed_files"), "review.changed_files")
    if declared != expected:
        raise ReviewInvocationError("reviewer's changed-file inventory does not match bootstrap")
    reviewed = review_paths(evidence.get("reviewed_files"), "review.reviewed_files")
    not_reviewed = review_paths(evidence.get("unreviewed_files"), "review.unreviewed_files")
    if verdict == "PASS":
        if (evidence.get("coverage_status") != "complete" or not expected <= reviewed
                or not_reviewed or evidence.get("blocking_findings") or evidence.get("unresolved_questions")):
            raise ReviewInvocationError("reviewer claimed PASS without complete native review evidence")
    plan = context.get("team_plan")
    if plan is not None:
        if evidence.get("review_id") != plan["review_id"] or evidence.get("risk_profile") != plan["risk_profile"]:
            raise ReviewInvocationError("reviewer omitted frozen team or risk identity")
        if verdict == "PASS":
            if plan["lead_implemented_change"] or evidence.get("reviewer_independent") is not True:
                raise ReviewInvocationError("implementer/self-review cannot claim independent PASS")
            if plan["execution_mode"] == "team-relayed":
                members = evidence.get("team_members")
                if (not isinstance(members, list)
                        or {m.get("role") for m in members if isinstance(m, dict)}
                        != set(plan["selected_roles"])
                        or not all(isinstance(m, dict) and m.get("task_id") for m in members)):
                    raise ReviewInvocationError("missing isolated specialist Task evidence")
                observed_mode = evidence.get("execution_mode")
                if observed_mode not in ("team-relayed", "team-live"):
                    raise ReviewInvocationError("subagents available but reviewer claimed native-solo")
                coordination = evidence.get("coordination")
                if not isinstance(coordination, dict):
                    raise ReviewInvocationError("missing real collaboration transport evidence")
                if observed_mode == "team-live":
                    if not coordination.get("real_peer_delivery_observed") or not evidence.get("peer_threads"):
                        raise ReviewInvocationError("team-live without observed direct peer delivery")
                else:
                    if coordination.get("transport") not in ("Task+resume", "Task+new Task", "Task (no relay needed)"):
                        raise ReviewInvocationError("team-relayed without Task+resume provenance")
            elif evidence.get("execution_mode") != "native-solo":
                raise ReviewInvocationError("reviewer fabricated team without runtime capability")
            if plan["risk_profile"] == "R3":
                verification = evidence.get("independent_verification")
                if not isinstance(verification, dict):
                    raise ReviewInvocationError("R3 lacks independent verification evidence")
                if plan["execution_mode"] == "team-relayed":
                    if verification.get("mode") != "isolated-agent" or not verification.get("task_id"):
                        raise ReviewInvocationError("R3 with Task requires isolated finding-verifier")
                elif verification.get("mode") != "native-second-pass" or not verification.get("source_evidence"):
                    raise ReviewInvocationError("R3 native fallback requires source-based second pass")
    # Review evidence is valid only for the same source snapshot at completion.
    assert_target_fresh(context, repo)
    # Never trust a reviewer to rewrite helper execution history.
    evidence["optional_helpers"] = context["optional_helpers"]
    evidence["review_preparation"] = {
        "mode": "ocr-first" if context["optional_helpers"]["ocr"]["status"] == "available" else "native-fallback",
        "git_inventory_size": len(expected),
    }
    if context["optional_helpers"]["ocr"]["status"] == "disabled":
        evidence["review_preparation"]["mode"] = "native-only"
    return {
        "kind": "review-invocation", "review_status": verdict,
        "review_evidence": evidence,
        "native_full_scope": sorted(expected),
        "pre_pr_review_independence_verified": False,
        "note": "Independent reviewer identity and signed evidence must be verified by the separate PR gate.",
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", type=Path, default=Path.cwd())
    ap.add_argument("--from", dest="base")
    ap.add_argument("--to", dest="head")
    ap.add_argument("--commit")
    ap.add_argument("--no-ocr", action="store_true")
    ap.add_argument("--timeout", type=int, default=300)
    ap.add_argument("--ocr-timeout", type=int, default=30)
    ap.add_argument("--risk-profile", choices=("R0", "R1", "R2", "R3"))
    ap.add_argument("--concern", action="append", default=[])
    ap.add_argument("--task-capable", action="store_true")
    ap.add_argument("--isolated-subagents", action="store_true")
    ap.add_argument("--direct-peer-supported", action="store_true")
    ap.add_argument("--lead-implemented-change", action="store_true")
    ap.add_argument("reviewer_command", nargs=argparse.REMAINDER,
                    help="-- <approved-host-reviewer-executable> [args...]")
    args = ap.parse_args(argv)
    command = args.reviewer_command
    if command and command[0] == "--":
        command = command[1:]
    try:
        # Ordering is mandatory; --no-ocr prevents importing or executing OCR.
        context = prepare_context(
            args.repo, base=args.base, head=args.head, commit=args.commit,
            allow_ocr=not args.no_ocr, timeout=args.ocr_timeout,
        )
        if args.task_capable and not args.risk_profile:
            raise TeamPlanningError("risk_profile must be classified before Task spawn")
        if args.risk_profile is not None:
            context["team_plan"] = freeze(
                context, args.repo, risk_profile=args.risk_profile,
                concerns=args.concern, task_available=args.task_capable,
                isolated_tasks=args.isolated_subagents or args.task_capable,
                direct_peer_supported=args.direct_peer_supported,
                lead_implemented_change=args.lead_implemented_change,
            )
        result = dispatch(context, repo=args.repo, reviewer_command=command, timeout=args.timeout)
    except (GitScopeError, TeamPlanningError, ReviewInvocationError, ValueError, OSError) as exc:
        print(json.dumps({
            "kind": "review-invocation", "review_status": "INCOMPLETE",
            "reason": str(exc), "pre_pr_review_independence_verified": False,
        }))
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["review_status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
