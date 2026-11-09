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
from team_orchestration import TeamPlanningError, freeze, CONCERN_CHOICES
from evidence_validation import EvidenceError, read_json, validate_evidence, assert_target_fresh, review_paths

MAX_RESULT_BYTES = 4 * 1024 * 1024


class ReviewInvocationError(Exception):
    """Cannot safely dispatch or reconcile a review."""


def dispatch(
    context: dict[str, Any], *, repo: Path, reviewer_command: list[str],
    timeout: int = 300,
) -> dict[str, Any]:
    """The subprocess reviewer is only one optional host runtime adapter."""
    if not reviewer_command or not reviewer_command[0] or timeout < 1 or timeout > 3600:
        raise ReviewInvocationError("approved host reviewer command and bounded timeout are required")
    assert_target_fresh(context, repo)
    request = json.dumps(context, ensure_ascii=False).encode("utf-8")
    try:
        process = subprocess.run(
            reviewer_command, cwd=repo.resolve(), input=request,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ReviewInvocationError(f"reviewer unavailable or timed out: {type(exc).__name__}") from exc
    if len(process.stdout) > MAX_RESULT_BYTES:
        raise ReviewInvocationError("reviewer result exceeds size limit")
    if process.returncode:
        raise ReviewInvocationError(f"reviewer failed with exit code {process.returncode}")
    try:
        evidence = json.loads(process.stdout.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as exc:
        raise ReviewInvocationError("reviewer returned invalid JSON evidence") from exc
    try:
        return validate_evidence(evidence, context, repo)
    except EvidenceError as exc:
        raise ReviewInvocationError(str(exc)) from exc

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", type=Path, default=Path.cwd())
    ap.add_argument("--from", dest="base")
    ap.add_argument("--to", dest="head")
    ap.add_argument("--commit")
    ap.add_argument("--base-branch", help="local or cached remote-tracking base; never fetches")
    ap.add_argument("--no-ocr", action="store_true")
    ap.add_argument("--timeout", type=int, default=300)
    ap.add_argument("--ocr-timeout", type=int, default=30)
    ap.add_argument("--risk-profile", choices=("R0", "R1", "R2", "R3"))
    ap.add_argument("--concern", action="append", choices=sorted(CONCERN_CHOICES), default=[],
                    help="valid concerns: " + ", ".join(sorted(CONCERN_CHOICES)))
    ap.add_argument("--task-capable", action="store_true")
    ap.add_argument("--isolated-subagents", action="store_true")
    ap.add_argument("--direct-peer-supported", action="store_true")
    ap.add_argument("--lead-implemented-change", action="store_true")
    ap.add_argument("--output-language", help="human report language, e.g. pt-BR")
    phase = ap.add_mutually_exclusive_group()
    phase.add_argument("--prepare-only", action="store_true",
                       help="prepare frozen scope for host-native agent reviewer")
    phase.add_argument("--validate-evidence", type=Path,
                       help="validate external Review evidence using frozen context")
    ap.add_argument("--context", type=Path, help="frozen JSON context from --prepare-only")
    ap.add_argument("--out", type=Path, help="context JSON output outside checkout")
    ap.add_argument("reviewer_command", nargs=argparse.REMAINDER,
                    help="-- <approved-reviewer> (optional subprocess adapter)")
    args = ap.parse_args(argv)
    command = args.reviewer_command
    if command and command[0] == "--":
        command = command[1:]
    if args.base_branch and (args.base or args.head or args.commit):
        ap.error("--base-branch is exclusive with --from/--to/--commit")
    if args.prepare_only and (not args.out or args.context or command):
        ap.error("--prepare-only requires --out, without a subprocess reviewer")
    if args.validate_evidence and (not args.context or args.out or command):
        ap.error("--validate-evidence requires --context without --out/reviewer command")
    if not args.prepare_only and not args.validate_evidence and not command:
        ap.error("supply a reviewer command or use --prepare-only")
    try:
        if args.validate_evidence:
            context = read_json(args.context)
            evidence = read_json(args.validate_evidence)
            result = validate_evidence(evidence, context, args.repo)
        else:
            context = prepare_context(
                args.repo, base=args.base, head=args.head, commit=args.commit,
                base_branch=args.base_branch, allow_ocr=not args.no_ocr,
                timeout=args.ocr_timeout, output_language=args.output_language,
            )
            context["preparation_adapter"] = "python-reference"
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
            if args.prepare_only:
                assert_target_fresh(context, args.repo)
                output = args.out.resolve()
                checkout = args.repo.resolve()
                if output == checkout or checkout in output.parents:
                    raise ReviewInvocationError("--out must be outside the reviewed repository")
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_text(
                    json.dumps(context, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
                    encoding="utf-8",
                )
                print(json.dumps({
                    "status": "prepared", "context": str(output),
                    "target": context["target"],
                    "review_id": context.get("team_plan", {}).get("review_id"),
                }))
                return 0
            result = dispatch(context, repo=args.repo, reviewer_command=command, timeout=args.timeout)
    except (GitScopeError, TeamPlanningError, ReviewInvocationError,
            EvidenceError, ValueError, OSError) as exc:
        print(json.dumps({
            "kind": "review-invocation", "review_status": "INCOMPLETE",
            "reason": str(exc), "pre_pr_review_independence_verified": False,
        }))
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["review_status"] == "PASS" else 1

if __name__ == "__main__":
    sys.exit(main())
