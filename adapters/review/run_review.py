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
from git_scope import GitScopeError

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


def dispatch(
    context: dict[str, Any], *, repo: Path, reviewer_command: list[str],
    timeout: int = 300,
) -> dict[str, Any]:
    if not reviewer_command or not reviewer_command[0] or timeout < 1 or timeout > 3600:
        raise ReviewInvocationError("approved host reviewer command and bounded timeout are required")
    # Preparation already happened: the host reviewer cannot be invoked before
    # the full Git scope and optional OCR rule delegation are known.
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
        result = dispatch(context, repo=args.repo, reviewer_command=command, timeout=args.timeout)
    except (GitScopeError, ReviewInvocationError, ValueError, OSError) as exc:
        print(json.dumps({
            "kind": "review-invocation", "review_status": "INCOMPLETE",
            "reason": str(exc), "pre_pr_review_independence_verified": False,
        }))
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["review_status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
