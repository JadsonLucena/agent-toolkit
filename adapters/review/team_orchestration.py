"""Provider-neutral, risk-sized Review Task coordination.

A hosting IDE supplies REAL isolated Task calls, resume calls, and (where
supported) a trusted direct-message audit feed. This module does not spawn
models by itself and never manufactures an independent PASS.
"""
from __future__ import annotations

import asyncio
import uuid
from pathlib import Path
from typing import Any, Protocol

from git_scope import GitScopeError, git_inventory

# Stable semantic concerns, with one specialist per distinct investigation.
CONCERN_ROLES = {
    "contract": "specification-reviewer",
    "correctness": "correctness-reviewer",
    "security": "security-reviewer",
    "reliability": "reliability-reviewer",
    "testing": "testing-reviewer",
    "architecture": "architecture-reviewer",
}
BOUNDS = {"R0": (0, 0), "R1": (0, 1), "R2": (2, 4), "R3": (3, 5)}
REQUEST_KINDS = {"question", "challenge", "escalation"}
SUPPORTED_KINDS = REQUEST_KINDS | {"observation", "response", "resolution"}
MAX_RELAY_REQUESTS = 30
AGENT_DIR = Path(__file__).resolve().parents[2] / "contexts" / "review" / "agents"


class TeamPlanningError(Exception):
    """Cannot truthfully allocate or verify the requested review team."""


class TaskRuntime(Protocol):
    """Implemented by an *approved* host with isolated Task/subagent support.

    task_batch must submit ALL supplied roles during the same host turn.
    resume targets an existing isolated agent ID, not a sibling agent or
    a lead-authored substitute.
    """
    async def task_batch(self, requests: list[dict[str, Any]]) -> list[dict[str, Any]]: ...
    async def resume(self, task_id: str, message: dict[str, Any]) -> dict[str, Any]: ...
    async def direct_message_audit(self, review_id: str) -> list[dict[str, Any]]: ...


def freeze(
    context: dict[str, Any], repo: Path, *, risk_profile: str,
    concerns: list[str], task_available: bool, isolated_tasks: bool,
    direct_peer_supported: bool = False, lead_implemented_change: bool = False,
    review_id: str | None = None,
) -> dict[str, Any]:
    """Freeze target and assign bounded lenses BEFORE any Task call."""
    if risk_profile not in BOUNDS:
        raise TeamPlanningError("risk_profile must be R0, R1, R2 or R3")
    if not isinstance(concerns, list) or any(c not in CONCERN_ROLES for c in concerns):
        raise TeamPlanningError("concerns must use six known semantic names")
    if len(set(concerns)) != len(concerns):
        raise TeamPlanningError("duplicate concerns cannot justify extra specialists")
    if not isinstance(context.get("changed_files"), list) or not context["changed_files"]:
        raise TeamPlanningError("complete non-empty Git change inventory required")
    if not isinstance(context.get("target"), dict) or not isinstance(context.get("scope"), dict):
        raise TeamPlanningError("resolved target and exact Git scope required")
    if not isinstance(context.get("repository"), str) or Path(context["repository"]).resolve() != repo.resolve():
        raise TeamPlanningError("repository identity mismatch")
    scope = context["scope"]
    try:
        fresh = git_inventory(
            repo=repo.resolve(), timeout=30, from_ref=scope.get("base_ref"),
            to_ref=scope.get("head_ref"), commit_ref=scope.get("commit_ref"),
        )
    except (GitScopeError, OSError) as exc:
        raise TeamPlanningError("cannot freeze current Git target") from exc
    if fresh["target"] != context["target"] or fresh["changed_files"] != context["changed_files"]:
        raise TeamPlanningError("Git target changed between preparation and team planning")
    if context["mode"] == "workspace" and not context["target"].get("workspace_fingerprint_sha256"):
        raise TeamPlanningError("workspace fingerprint missing")
    minimum, maximum = BOUNDS[risk_profile]
    selected = concerns[:maximum] if risk_profile != "R0" else []
    if risk_profile in ("R2", "R3") and task_available and isolated_tasks and len(selected) < minimum:
        raise TeamPlanningError(f"{risk_profile} needs {minimum}-{maximum} distinct concerns, not one all-purpose Task")
    if risk_profile == "R1" and not concerns:
        selected = []
    # R0/R1 without a distinct concern are deliberate native-solo choices.
    use_team = bool(task_available and isolated_tasks and selected)
    if risk_profile in ("R2", "R3") and task_available and isolated_tasks:
        use_team = True
    if not use_team:
        selected = []
    omitted = {CONCERN_ROLES[k]: (
        "Task/isolated subagents unavailable" if not use_team else "outside proportional N cap"
    ) for k in concerns[len(selected):]}
    omitted.update({role: "no distinct concern in diff" for k, role in CONCERN_ROLES.items() if k not in concerns})
    mode = "team-relayed" if use_team else "native-solo"
    return {
        "review_id": review_id or uuid.uuid4().hex,
        "repository": str(repo.resolve()), "target": dict(fresh["target"]),
        "scope": dict(scope), "mode": context["mode"],
        "changed_files": list(fresh["changed_files"]), "risk_profile": risk_profile,
        "selected_roles": [CONCERN_ROLES[c] for c in selected],
        "role_assignments": {
            CONCERN_ROLES[c]: {"concern": c, "reason": f"diff concern: {c}"}
            for c in selected
        },
        "omitted_roles": omitted,
        "capabilities": {
            "task_available": bool(task_available), "isolated_tasks": bool(isolated_tasks),
            "direct_peer_supported": bool(direct_peer_supported),
        },
        "execution_mode": mode,
        "lead_implemented_change": bool(lead_implemented_change),
        "verifier_required": risk_profile == "R3",
        "n_justification": {
            "distinct_concerns": list(concerns),
            "selected": len(selected), "minimum": minimum, "maximum": maximum,
            "lead_counts_as_lens": False,
        },
    }


def _check_target(reply: dict[str, Any], plan: dict[str, Any]) -> None:
    if reply.get("review_id") != plan["review_id"]:
        raise TeamPlanningError("agent returned a different review_id")
    if reply.get("repository") != plan["repository"] or reply.get("target") != plan["target"]:
        raise TeamPlanningError("agent returned a stale or different target")
    if "review_status" in reply or "verdict" in reply:
        raise TeamPlanningError("specialists cannot declare PASS/FAIL")


def _paths(paths: Any, inventory: set[str]) -> list[str]:
    if not isinstance(paths, list) or any(not isinstance(p, str) or p not in inventory for p in paths):
        raise TeamPlanningError("specialist coverage includes an unknown or invalid path")
    if len(paths) != len(set(paths)):
        raise TeamPlanningError("duplicate reviewed path")
    return paths


def _agent_prompt(role: str) -> str:
    path = AGENT_DIR / f"{role}.md"
    if role not in set(CONCERN_ROLES.values()) | {"finding-verifier"}:
        raise TeamPlanningError("unknown specialist")
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise TeamPlanningError(f"cannot read agent file: {role}") from exc


def _assignment(plan: dict[str, Any], role: str, *, purpose: str, findings: Any = None) -> dict[str, Any]:
    return {
        "role": role, "agent_file": f"contexts/review/agents/{role}.md",
        "agent_prompt": _agent_prompt(role), "purpose": purpose,
        "review_id": plan["review_id"], "repository": plan["repository"],
        "target": dict(plan["target"]), "risk_profile": plan["risk_profile"],
        "changed_files": list(plan["changed_files"]),
        "read_only": True, "findings_to_falsify": findings,
        "instructions": "Inspect actual source and return candidate findings, covered files and uncertainty. No verdict.",
    }


def _validate_first_pass(replies: list[dict[str, Any]], plan: dict[str, Any]) -> dict[str, dict[str, Any]]:
    roles = plan["selected_roles"]
    if not isinstance(replies, list) or len(replies) != len(roles):
        raise TeamPlanningError("first Task batch returned missing/extra specialists")
    grouped = {}
    seen_ids = set()
    inventory = set(plan["changed_files"])
    for reply in replies:
        if not isinstance(reply, dict):
            raise TeamPlanningError("invalid Task response")
        _check_target(reply, plan)
        role = reply.get("role")
        task_id = reply.get("task_id")
        if role not in roles or role in grouped or not isinstance(task_id, str) or not task_id or task_id in seen_ids:
            raise TeamPlanningError("nonisolated, duplicate or unexpected specialist Task ID")
        _paths(reply.get("reviewed_files"), inventory)
        for field in ("candidate_findings", "uncertainties", "relay_requests"):
            if not isinstance(reply.get(field), list):
                raise TeamPlanningError(f"specialist omitted {field} array")
        if len(reply["relay_requests"]) > MAX_RELAY_REQUESTS:
            raise TeamPlanningError("too many peer requests")
        grouped[role] = reply
        seen_ids.add(task_id)
    return grouped


def _relay_payload(
    plan: dict[str, Any], sender: str, recipient: str,
    kind: str, subject: str, evidence_refs: list[str],
    *, requested_action: str | None, thread_id: str, message_id: str,
    response_to: str | None = None,
) -> dict[str, Any]:
    return {
        "review_id": plan["review_id"], "target_head_sha": plan["target"]["head_sha"],
        "target_base_sha": plan["target"].get("base_sha"),
        "workspace_fingerprint": plan["target"].get("workspace_fingerprint_sha256"),
        "message_id": message_id, "thread_id": thread_id,
        "sender_role": sender, "recipient_role": recipient,
        "kind": kind, "subject": subject, "evidence_refs": list(evidence_refs),
        "requested_action": requested_action, "response_to": response_to,
        "status": "relayed-by-lead", "transport": "Task+resume",
    }


def _valid_message_reply(reply: Any, plan: dict[str, Any], role: str, kind: str) -> None:
    if not isinstance(reply, dict) or reply.get("kind") != kind or reply.get("role") != role:
        raise TeamPlanningError("wrong or missing relayed peer reply")
    _check_target(reply, plan)
    if not isinstance(reply.get("subject"), str) or not reply["subject"].strip():
        raise TeamPlanningError("peer reply lacks subject")
    refs = reply.get("evidence_refs")
    if not isinstance(refs, list) or not refs or any(not isinstance(x, str) or not x for x in refs):
        raise TeamPlanningError("peer reply lacks source evidence")


async def _relay(plan: dict[str, Any], grouped: dict[str, dict[str, Any]], host: TaskRuntime) -> tuple[list[dict], list[str]]:
    ledger: list[dict] = []
    unresolved: list[str] = []
    pending = [(role, req) for role, reply in grouped.items() for req in reply["relay_requests"]]
    if len(pending) > MAX_RELAY_REQUESTS:
        raise TeamPlanningError("peer relay budget exceeded")
    for sender, request in pending:
        if not isinstance(request, dict) or request.get("kind") not in REQUEST_KINDS:
            raise TeamPlanningError("invalid cross-specialist request")
        recipient = request.get("recipient_role")
        if recipient not in grouped or recipient == sender:
            raise TeamPlanningError("relay target must be an activated different specialist")
        subject, action, refs = (request.get("subject"), request.get("requested_action"), request.get("evidence_refs"))
        if (not isinstance(subject, str) or not subject.strip() or not isinstance(action, str)
                or not action.strip() or not isinstance(refs, list) or not refs
                or any(not isinstance(x, str) or not x for x in refs)):
            raise TeamPlanningError("relay lacks bounded subject/action/source references")
        thread = uuid.uuid4().hex
        req_id = uuid.uuid4().hex
        msg = _relay_payload(plan, sender, recipient, request["kind"], subject, refs,
                             requested_action=action, thread_id=thread, message_id=req_id)
        ledger.append(msg)
        try:
            response = await host.resume(grouped[recipient]["task_id"], msg)
            _valid_message_reply(response, plan, recipient, "response")
            resp_id = uuid.uuid4().hex
            answer = _relay_payload(plan, recipient, sender, "response", response["subject"],
                                    response["evidence_refs"], requested_action=None,
                                    thread_id=thread, message_id=resp_id, response_to=req_id)
            ledger.append(answer)
            resolved = await host.resume(grouped[sender]["task_id"], answer)
            _valid_message_reply(resolved, plan, sender, "resolution")
            ledger.append(_relay_payload(plan, sender, recipient, "resolution", resolved["subject"],
                                         resolved["evidence_refs"], requested_action=None,
                                         thread_id=thread, message_id=uuid.uuid4().hex,
                                         response_to=resp_id))
        except Exception as exc:
            unresolved.append(f"thread {thread}: peer relay incomplete ({type(exc).__name__})")
    return ledger, unresolved


def _direct_exchange_observed(events: Any, grouped: dict[str, dict], review_id: str) -> bool:
    """Host-observed audit, never model-generated claims or in-process queues."""
    if not isinstance(events, list):
        return False
    ids = {v["task_id"] for v in grouped.values()}
    requests: dict[str, dict] = {}
    for event in events:
        if not isinstance(event, dict) or event.get("review_id") != review_id:
            continue
        if event.get("via") != "direct-peer" or event.get("status") != "delivered":
            continue
        src, dst, tid = event.get("sender_task_id"), event.get("recipient_task_id"), event.get("thread_id")
        if src not in ids or dst not in ids or src == dst or not isinstance(tid, str):
            continue
        refs = event.get("evidence_refs")
        if (not isinstance(refs, list) or not refs
                or any(not isinstance(ref, str) or ":" not in ref for ref in refs)):
            continue
        if not isinstance(event.get("subject"), str) or not event["subject"].strip():
            continue
        if event.get("kind") in ("challenge", "question"):
            requests[tid] = event
        if event.get("kind") == "response" and tid in requests:
            prior = requests[tid]
            if src == prior["recipient_task_id"] and dst == prior["sender_task_id"]:
                return True
    return False


async def execute(
    plan: dict[str, Any], host: TaskRuntime | None,
    *, independent_lead: bool = False,
) -> dict[str, Any]:
    """Execute selected specialists with an approved Task-capable host.

    This returns *candidate evidence* only, not a final review verdict.
    The lead must do an independent full-file reconciliation afterward.
    """
    roles = plan["selected_roles"]
    grouped: dict[str, dict] = {}
    ledger: list[dict] = []
    unresolved: list[str] = []
    execution_mode = plan["execution_mode"]
    if execution_mode == "team-relayed":
        if host is None:
            raise TeamPlanningError("Task capability advertised but no host supplied")
        # One batch: host must issue sibling Task calls in the same turn.
        asks = [
            _assignment(plan, role, purpose=plan["role_assignments"][role]["reason"])
            for role in roles
        ]
        grouped = _validate_first_pass(await host.task_batch(asks), plan)
        if plan["capabilities"]["direct_peer_supported"]:
            try:
                observed = await host.direct_message_audit(plan["review_id"])
            except (OSError, AttributeError, NotImplementedError):
                observed = []
            if _direct_exchange_observed(observed, grouped, plan["review_id"]):
                execution_mode = "team-live"
                # Record bounded, provider-observed transport metadata only;
                # never copy entire model transcripts or secret-bearing bodies.
                keys = ("review_id", "thread_id", "message_id", "kind", "status",
                        "sender_task_id", "recipient_task_id", "via", "evidence_refs")
                ledger = [{k: e[k] for k in keys if k in e}
                          for e in observed if isinstance(e, dict)
                          and e.get("review_id") == plan["review_id"]
                          and e.get("via") == "direct-peer"
                          and e.get("status") == "delivered"][:MAX_RELAY_REQUESTS]
        if execution_mode != "team-live":
            ledger, unresolved = await _relay(plan, grouped, host)
    material = any(v["candidate_findings"] for v in grouped.values())
    verifier_needed = plan["verifier_required"] or (
        plan["risk_profile"] == "R2" and material
    ) or (plan["risk_profile"] == "R1" and material)
    verifier: dict[str, Any] | None = None
    verification = {"mode": "not-required"}
    if verifier_needed:
        if host is None or not plan["capabilities"]["isolated_tasks"]:
            # The lead must still execute and document a separate falsification
            # pass. Merely selecting this fallback does NOT count as verified.
            verification = {"mode": "native-second-pass", "independent": False, "completed": False}
        else:
            # Verifier receives raw findings but must inspect sources, not votes.
            request = _assignment(plan, "finding-verifier",
                                  purpose="independent source falsification",
                                  findings=[f for item in grouped.values() for f in item["candidate_findings"]])
            response = await host.task_batch([request])
            if len(response) != 1 or not isinstance(response[0], dict):
                raise TeamPlanningError("isolated verifier did not return a result")
            verifier = response[0]
            _check_target(verifier, plan)
            if (verifier.get("role") != "finding-verifier"
                    or verifier.get("task_id") in {v["task_id"] for v in grouped.values()}
                    or not verifier.get("task_id")
                    or verifier.get("verification_method") != "source-inspection"
                    or not isinstance(verifier.get("inspected_files"), list)
                    or not verifier.get("inspected_files")
                    or not isinstance(verifier.get("verified_findings"), list)):
                raise TeamPlanningError("verifier was not independently isolated or source-based")
            _paths(verifier["inspected_files"], set(plan["changed_files"]))
            verification = {"mode": "isolated-agent", "independent": True,
                            "task_id": verifier["task_id"], "inspected_files": verifier["inspected_files"]}
    return {
        "review_id": plan["review_id"], "repository": plan["repository"],
        "target": plan["target"], "scope": plan["scope"],
        "changed_files": plan["changed_files"], "risk_profile": plan["risk_profile"],
        "execution_mode": execution_mode,
        "team_members": [
            {"role": role, "task_id": grouped[role]["task_id"],
             "reason": plan["role_assignments"][role]["reason"]}
            for role in roles
        ],
        "coordination": {
            "transport": (
                "Task+resume" if ledger and execution_mode == "team-relayed"
                else "Task (no relay needed)" if execution_mode == "team-relayed"
                else "observed direct-peer audit" if execution_mode == "team-live" else "none"
            ),
            "real_peer_delivery_observed": execution_mode == "team-live",
        },
        "peer_threads": ledger, "unresolved_questions": unresolved,
        "independent_verification": verification,
        "n_justification": {**plan["n_justification"], "omitted_roles": plan["omitted_roles"]},
        "specialist_coverage": sorted({p for reply in grouped.values() for p in reply["reviewed_files"]}),
        "raw_findings": [f for reply in grouped.values() for f in reply["candidate_findings"]],
        "specialist_uncertainties": [u for reply in grouped.values() for u in reply["uncertainties"]],
        "verifier": verifier,
        "lead_implemented_change": plan["lead_implemented_change"],
        "review_status": None,  # Lead only; consensus cannot approve.
    }


def finalize(
    result: dict[str, Any], context: dict[str, Any], repo: Path,
    *, lead_reviewed_files: list[str], lead_independent: bool,
    verified_blockers: list[Any], unresolved_material: list[Any],
    native_second_pass_evidence: list[str] | None = None,
    finding_dispositions: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Fail-closed independent lead decision after all files are reconciled."""
    try:
        scope = context["scope"]
        fresh = git_inventory(repo=repo.resolve(), timeout=30,
                              from_ref=scope.get("base_ref"), to_ref=scope.get("head_ref"),
                              commit_ref=scope.get("commit_ref"))
        same = fresh["target"] == context["target"] and fresh["changed_files"] == context["changed_files"]
    except (GitScopeError, OSError):
        same = False
    required = set(result["changed_files"])
    covered = set(lead_reviewed_files)
    if len(covered) != len(lead_reviewed_files) or not covered <= required:
        raise TeamPlanningError("lead declared duplicate or out-of-scope file coverage")
    reasons = list(result["unresolved_questions"]) + list(unresolved_material)
    if not same:
        reasons.append("reviewed Git target/fingerprint changed")
    if covered != required:
        reasons.append("lead did not reconcile complete Git file inventory")
    if result["specialist_uncertainties"]:
        reasons.append("specialist uncertainty requires lead disposition")
    raw = result.get("raw_findings", [])
    if raw:
        # Candidates cannot disappear merely because peers agree or a
        # verifier was spawned. Require an explicit lead disposition for each.
        if not isinstance(finding_dispositions, dict):
            reasons.append("candidate findings lack explicit lead dispositions")
        else:
            ids = {f.get("finding_id") for f in raw if isinstance(f, dict)}
            if (None in ids or len(ids) != len(raw)
                    or ids != set(finding_dispositions)
                    or any(v not in ("confirmed", "refuted", "deferred")
                           for v in finding_dispositions.values())):
                reasons.append("candidate finding disposition coverage incomplete")
    if not lead_independent or result["lead_implemented_change"]:
        reasons.append("lead independence from implementation not established")
    if result["risk_profile"] == "R3" and result["independent_verification"]["mode"] != "isolated-agent" \
            and result["team_members"]:
        reasons.append("R3 requires isolated finding-verifier with subagents available")
    if result["independent_verification"]["mode"] == "native-second-pass":
        if not native_second_pass_evidence:
            reasons.append("native falsification pass lacks inspected-source evidence")
        else:
            result = {
                **result, "independent_verification": {
                    "mode": "native-second-pass", "independent": False, "completed": True,
                    "source_evidence": list(native_second_pass_evidence),
                },
            }
    if verified_blockers:
        verdict = "FAIL" if not reasons else "INCOMPLETE"
    else:
        verdict = "INCOMPLETE" if reasons else "PASS"
    return {
        **result, "review_status": verdict,
        "coverage_status": "complete" if covered == required else "partial",
        "reviewed_files": sorted(covered),
        "blocking_findings": list(verified_blockers),
        "unresolved_questions": reasons,
        "reviewer_independent": bool(lead_independent and not result["lead_implemented_change"]),
    }
