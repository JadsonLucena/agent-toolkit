#!/usr/bin/env python3
"""Explicit GitHub PR creation guarded by current review and project checks.

This is an optional *GitHub runtime adapter*, not a canonical Git command.
Only --create authorizes a remote mutation. It cannot prevent PRs opened by
other GitHub clients; use platform permissions/protection for broader policy.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

REQUIRED_CHECKS = {"lint", "tests"}
MAX_EVIDENCE_BYTES = 2_000_000


class GateError(Exception):
    """A required pre-creation decision could not be verified."""


def invoke(argv: list[str], repo: Path, timeout: int = 300) -> str:
    try:
        result = subprocess.run(
            argv, cwd=repo, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, timeout=timeout, check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise GateError(f"{argv[0]} unavailable or timed out: {type(exc).__name__}") from exc
    if result.returncode:
        raise GateError(f"{argv[0]} failed (exit {result.returncode})")
    return result.stdout.decode("utf-8", "replace").strip()


def git(repo: Path, *args: str) -> str:
    return invoke(["git", "--no-pager", *args], repo, 30)


def commit(repo: Path, ref: str) -> str:
    if not ref or ref.startswith("-") or "\n" in ref or "\0" in ref:
        raise GateError("invalid Git ref")
    value = git(repo, "rev-parse", "--verify", "--end-of-options", f"{ref}^{{commit}}")
    if len(value) != 40 or any(c not in "0123456789abcdef" for c in value):
        raise GateError("could not establish full commit identity")
    return value


def load_json(path: Path) -> dict[str, Any]:
    if path.stat().st_size > MAX_EVIDENCE_BYTES:
        raise GateError("evidence/configuration file is too large")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise GateError("expected JSON object")
    return payload


def changed_paths(repo: Path, base: str, head: str) -> set[str]:
    merge_base = git(repo, "merge-base", base, head)
    out = subprocess.run(
        ["git", "--no-pager", "diff", "--no-ext-diff", "--no-textconv",
         "--no-renames", "--name-only", "-z", merge_base, head],
        cwd=repo, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False, timeout=30,
    )
    if out.returncode:
        raise GateError("cannot inventory PR diff")
    paths = {x.decode("utf-8", "surrogateescape") for x in out.stdout.split(b"\0") if x}
    if not paths:
        raise GateError("PR diff has no changes")
    return paths


def paths(items: Any, field: str) -> set[str]:
    if not isinstance(items, list):
        raise GateError(f"review evidence must include {field} array")
    selected: set[str] = set()
    for item in items:
        path = item if isinstance(item, str) else item.get("path") if isinstance(item, dict) else None
        if not isinstance(path, str) or not path or path in selected:
            raise GateError(f"invalid or duplicate review path in {field}")
        selected.add(path)
    return selected


def verify_evidence(evidence: dict[str, Any], *, base: str, head: str, actual: set[str]) -> None:
    # The independently issued JSON file is a portable *attestation*, not a
    # cryptographic identity proof. The operator must validate its provenance.
    target = evidence.get("target")
    if not isinstance(target, dict):
        raise GateError("review target missing")
    if target.get("base_sha") != base or target.get("head_sha") != head:
        raise GateError("review evidence bound to another head/base")
    if evidence.get("review_status") != "PASS" or evidence.get("coverage_status") != "complete":
        raise GateError("independent Code Review is not PASS with complete coverage")
    if evidence.get("reviewer_independent") is not True:
        raise GateError("missing affirmative independent-review attestation")
    reviewer = evidence.get("reviewer")
    if not isinstance(reviewer, str) or not reviewer.strip():
        raise GateError("reviewer identity/provenance missing")
    recorded = paths(evidence.get("changed_files"), "changed_files")
    reviewed = paths(evidence.get("reviewed_files"), "reviewed_files")
    if recorded != actual or not actual <= reviewed:
        raise GateError("review inventory or reviewed-file coverage does not match actual PR diff")
    if evidence.get("unreviewed_files") or evidence.get("blocking_findings") or evidence.get("unresolved_questions"):
        raise GateError("review has unresolved coverage, blockers or material questions")
    if evidence.get("limitations") and not evidence.get("limitations_accepted_by_policy"):
        raise GateError("material review limitations have no explicit policy disposition")


def read_checks(path: Path) -> dict[str, list[str]]:
    doc = load_json(path)
    checks = doc.get("checks")
    if not isinstance(checks, dict) or not REQUIRED_CHECKS <= checks.keys():
        raise GateError("project checks must provide lint and tests")
    out = {}
    for name, argv in checks.items():
        if not isinstance(name, str) or not isinstance(argv, list) or not argv or any(
            not isinstance(v, str) or not v or "\x00" in v for v in argv
        ):
            raise GateError(f"invalid argv for {name}")
        out[name] = argv
    return out


def guard(
    repo: Path, base_ref: str, head_ref: str, evidence_path: Path,
    checks_path: Path, *, remote: str = "origin", timeout: int = 300,
) -> dict[str, Any]:
    repo = repo.resolve()
    if Path(git(repo, "rev-parse", "--show-toplevel")).resolve() != repo:
        raise GateError("repository path must be its worktree root")
    base = commit(repo, base_ref)
    head = commit(repo, head_ref)
    if commit(repo, "HEAD") != head:
        raise GateError("must check out the exact proposed PR head")
    # Uncommitted files must never be mistaken for successful head verification.
    if git(repo, "status", "--porcelain=v1", "--untracked-files=all"):
        raise GateError("dirty worktree: checks would not validate the proposed head")
    remote_base = git(repo, "ls-remote", "--heads", remote, base_ref)
    if not any(row.split()[0] == base for row in remote_base.splitlines() if row.split()):
        raise GateError("published remote base is not the locally reviewed base")
    remote_heads = git(repo, "ls-remote", "--heads", remote, head_ref)
    if not any(row.split()[0] == head for row in remote_heads.splitlines() if row.split()):
        raise GateError("published remote branch is not the exact proposed head")
    actual = changed_paths(repo, base, head)
    try:
        evidence = load_json(evidence_path)
    except (OSError, ValueError) as exc:
        raise GateError(f"review evidence unreadable: {type(exc).__name__}") from exc
    verify_evidence(evidence, base=base, head=head, actual=actual)
    try:
        checks = read_checks(checks_path)
    except (OSError, ValueError) as exc:
        raise GateError(f"check manifest unreadable: {type(exc).__name__}") from exc
    completed = []
    for name, argv in checks.items():
        invoke(argv, repo, timeout)
        completed.append(name)
    # Check revision/freshness again after potentially slow test commands.
    if commit(repo, "HEAD") != head or git(repo, "status", "--porcelain=v1", "--untracked-files=all"):
        raise GateError("repository changed while verification was running")
    remote_heads = git(repo, "ls-remote", "--heads", remote, head_ref)
    if not any(row.split()[0] == head for row in remote_heads.splitlines() if row.split()):
        raise GateError("remote head changed during verification")
    if commit(repo, base_ref) != base:
        raise GateError("base changed during verification")
    remote_base = git(repo, "ls-remote", "--heads", remote, base_ref)
    if not any(row.split()[0] == base for row in remote_base.splitlines() if row.split()):
        raise GateError("remote base changed during verification")
    return {"base_sha": base, "head_sha": head, "changed_files": sorted(actual), "checks_passed": completed}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", type=Path, default=Path.cwd())
    ap.add_argument("--base", required=True)
    ap.add_argument("--head", required=True, help="local and remote branch name (not SHA)")
    ap.add_argument("--evidence", type=Path, required=True)
    ap.add_argument("--checks-file", type=Path, required=True)
    ap.add_argument("--timeout", type=int, default=300)
    ap.add_argument("--remote", default="origin")
    ap.add_argument("--create", action="store_true", help="explicitly authorize gh pr create")
    ap.add_argument("--title")
    ap.add_argument("--body-file", type=Path)
    ap.add_argument("--draft", action="store_true")
    args = ap.parse_args(argv)
    if args.timeout < 1 or args.timeout > 3600:
        ap.error("timeout must be between 1 and 3600 seconds")
    if args.create and (not args.title or args.body_file is None):
        ap.error("--create requires --title and --body-file")
    try:
        info = guard(args.repo, args.base, args.head, args.evidence, args.checks_file,
                     remote=args.remote, timeout=args.timeout)
        if args.create:
            cmd = ["gh", "pr", "create", "--base", args.base, "--head", args.head, "--title", args.title,
                   "--body-file", str(args.body_file.resolve())]
            if args.draft:
                cmd.append("--draft")
            url = invoke(cmd, args.repo.resolve(), args.timeout)
            info["created_pr_url"] = url
        print(json.dumps({"status": "passed", **info}, sort_keys=True))
        return 0
    except GateError as exc:
        print(json.dumps({"status": "blocked", "reason": str(exc)}))
        return 2


if __name__ == "__main__":
    sys.exit(main())
