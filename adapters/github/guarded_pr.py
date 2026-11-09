#!/usr/bin/env python3
"""Explicit GitHub PR creation guarded by signed review evidence and trusted checks.

This is an optional GitHub runtime adapter. The invoking deployment MUST
protect the external trust policy and reviewer signing keys. This adapter
cannot regulate unrelated GitHub clients or establish isolation by itself.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

REQUIRED_CHECKS = {"lint", "tests"}
MAX_EVIDENCE_BYTES = 2_000_000
SIGNATURE_NAMESPACE = "agent-toolkit-code-review"


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


def read_bytes(path: Path) -> bytes:
    try:
        if path.stat().st_size > MAX_EVIDENCE_BYTES:
            raise GateError("evidence or policy file exceeds size limit")
        return path.read_bytes()
    except OSError as exc:
        raise GateError(f"file unavailable: {type(exc).__name__}") from exc


def load_json(path: Path) -> dict[str, Any]:
    try:
        doc = json.loads(read_bytes(path))
    except (UnicodeDecodeError, ValueError) as exc:
        raise GateError("invalid JSON evidence or trust policy") from exc
    if not isinstance(doc, dict):
        raise GateError("expected JSON object")
    return doc


def changed_paths(repo: Path, base: str, head: str) -> set[str]:
    merge_base = git(repo, "merge-base", base, head)
    try:
        out = subprocess.run(
            ["git", "--no-pager", "diff", "--no-ext-diff", "--no-textconv",
             "--no-renames", "--name-only", "-z", merge_base, head],
            cwd=repo, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False, timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise GateError("could not inventory PR diff") from exc
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


def read_checks(document: dict[str, Any]) -> dict[str, list[str]]:
    checks = document.get("checks")
    if not isinstance(checks, dict) or not REQUIRED_CHECKS <= checks.keys():
        raise GateError("trusted project checks must provide lint and tests")
    out = {}
    for name, argv in checks.items():
        if not isinstance(name, str) or not isinstance(argv, list) or not argv or any(
            not isinstance(v, str) or not v or "\x00" in v for v in argv
        ):
            raise GateError(f"invalid trusted check argv for {name}")
        out[name] = argv
    return out


def external_path(path: Path, repo: Path, field: str) -> Path:
    resolved = path.resolve()
    if not resolved.is_absolute() or resolved == repo or repo in resolved.parents:
        raise GateError(f"{field} must be protected outside the target repository")
    return resolved


def load_trust_policy(path: Path, repo: Path, remote: str) -> tuple[dict[str, Any], dict[str, list[str]], bytes]:
    path = external_path(path, repo, "trust policy")
    original = read_bytes(path)
    try:
        policy = json.loads(original)
    except (UnicodeDecodeError, ValueError) as exc:
        raise GateError("invalid trusted policy JSON") from exc
    if not isinstance(policy, dict) or policy.get("schema_version") != 1:
        raise GateError("unsupported trusted policy schema")
    repository = policy.get("github_repository")
    if not isinstance(repository, str) or re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository) is None:
        raise GateError("trusted GitHub repository is missing or invalid")
    remote_url = policy.get("remote_url")
    if not isinstance(remote_url, str) or git(repo, "remote", "get-url", remote) != remote_url:
        raise GateError("Git remote does not match trusted repository origin")
    reviewers = policy.get("reviewers")
    if not isinstance(reviewers, list) or not reviewers or any(
        not isinstance(v, str) or not v.strip() or "\0" in v or "\n" in v for v in reviewers
    ):
        raise GateError("trusted policy must name authorized reviewers")
    allowed = policy.get("allowed_signers_file")
    if not isinstance(allowed, str) or not allowed:
        raise GateError("trusted policy must locate an allowed signers file")
    signer_file = external_path(Path(allowed), repo, "allowed signers")
    if not signer_file.is_file():
        raise GateError("allowed signers file unavailable")
    policy["allowed_signers_file"] = str(signer_file)
    checks = read_checks(policy)
    # The committed repository manifest is not itself trusted. Refuse a
    # different manifest rather than quietly overlooking project policy drift.
    manifest = repo / ".github" / "toolkit-pr-checks.json"
    if manifest.is_file() and read_checks(load_json(manifest)) != checks:
        raise GateError("repository check manifest differs from protected trust policy")
    return policy, checks, original


def verify_signature(
    evidence_path: Path, signature_path: Path, reviewer: str, allowed_signers_file: str,
    repo: Path,
) -> None:
    evidence = read_bytes(evidence_path)
    signature = read_bytes(signature_path)
    if not signature.startswith(b"-----BEGIN SSH SIGNATURE-----"):
        raise GateError("missing valid SSH-signature envelope")
    # ssh-keygen verifies a detached Ed25519/RSA SSHSIG signature over the
    # exact JSON bytes. Authorized keys live in the protected allowed-signers file.
    try:
        result = subprocess.run(
            ["ssh-keygen", "-Y", "verify", "-f", allowed_signers_file, "-I", reviewer,
             "-n", SIGNATURE_NAMESPACE, "-s", str(signature_path.resolve())],
            cwd=repo, input=evidence, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            check=False, timeout=20,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise GateError(f"SSH signature verification unavailable: {type(exc).__name__}") from exc
    if result.returncode:
        raise GateError("review evidence signature is invalid or signer is unauthorized")


def verify_evidence(
    evidence: dict[str, Any], *, base: str, head: str, actual: set[str],
    repository: str, reviewers: list[str], repo: Path,
) -> str:
    target = evidence.get("target")
    if not isinstance(target, dict):
        raise GateError("review target missing")
    if target.get("base_sha") != base or target.get("head_sha") != head:
        raise GateError("review evidence bound to another head/base")
    if evidence.get("repository") != repository:
        raise GateError("review evidence refers to another repository")
    if evidence.get("review_profile") != "gate":
        raise GateError("pre-PR gate requires explicitly signed review_profile=gate evidence")
    if evidence.get("review_status") != "PASS" or evidence.get("coverage_status") != "complete":
        raise GateError("independent Code Review is not PASS with complete coverage")
    if evidence.get("reviewer_independent") is not True:
        raise GateError("missing affirmative independent-review attestation")
    reviewer = evidence.get("reviewer")
    if not isinstance(reviewer, str) or reviewer not in reviewers:
        raise GateError("reviewer is not approved by trusted policy")
    # A matching Git author email is definitive self-review evidence. A
    # non-matching address alone is NOT proof of independence; protected
    # signing-key custody and reviewer authorization remain necessary.
    authors = {a.lower() for a in git(repo, "log", "--format=%ae", f"{base}..{head}").splitlines()}
    if reviewer.lower() in authors:
        raise GateError("reviewer is also a change author")
    recorded = paths(evidence.get("changed_files"), "changed_files")
    reviewed = paths(evidence.get("reviewed_files"), "reviewed_files")
    if recorded != actual or not actual <= reviewed:
        raise GateError("review inventory or reviewed-file coverage does not match actual PR diff")
    for field in ("unreviewed_files", "blocking_findings"):
        if evidence.get(field) != []:
            raise GateError(f"review has missing or unresolved {field} evidence")
    questions = evidence.get("unresolved_questions")
    if not isinstance(questions, list) or any(
        not isinstance(q, dict) or q.get("material") is not False for q in questions
    ):
        raise GateError("review has missing or unresolved material questions")
    if evidence.get("limitations") and not evidence.get("limitations_accepted_by_policy"):
        raise GateError("material review limitations have no explicit policy disposition")
    return reviewer


def remote_head(repo: Path, remote: str, branch: str, expected: str, what: str) -> None:
    refs = git(repo, "ls-remote", "--heads", remote, branch)
    if not any(row.split()[0] == expected for row in refs.splitlines() if row.split()):
        raise GateError(f"remote {what} does not match reviewed {what}")


def guard(
    repo: Path, base_ref: str, head_ref: str, evidence_path: Path,
    signature_path: Path, trust_policy_path: Path,
    *, remote: str = "origin", timeout: int = 300,
) -> dict[str, Any]:
    repo = repo.resolve()
    if Path(git(repo, "rev-parse", "--show-toplevel")).resolve() != repo:
        raise GateError("repository path must be its worktree root")
    policy, checks, original_policy = load_trust_policy(trust_policy_path, repo, remote)
    original_allowed_signers = read_bytes(Path(policy["allowed_signers_file"]))
    base = commit(repo, base_ref)
    head = commit(repo, head_ref)
    if commit(repo, "HEAD") != head:
        raise GateError("must check out the exact proposed PR head")
    if git(repo, "status", "--porcelain=v1", "--untracked-files=all"):
        raise GateError("dirty worktree: checks would not validate proposed head")
    remote_head(repo, remote, base_ref, base, "base")
    remote_head(repo, remote, head_ref, head, "head")
    actual = changed_paths(repo, base, head)
    evidence = load_json(evidence_path)
    reviewer = verify_evidence(
        evidence, base=base, head=head, actual=actual,
        repository=policy["github_repository"], reviewers=policy["reviewers"], repo=repo,
    )
    verify_signature(evidence_path, signature_path, reviewer, policy["allowed_signers_file"], repo)
    completed = []
    for name, argv in checks.items():
        invoke(argv, repo, timeout)
        completed.append(name)
    if commit(repo, "HEAD") != head or git(repo, "status", "--porcelain=v1", "--untracked-files=all"):
        raise GateError("repository changed during verification")
    remote_head(repo, remote, head_ref, head, "head")
    remote_head(repo, remote, base_ref, base, "base")
    if commit(repo, base_ref) != base:
        raise GateError("base changed during verification")
    if read_bytes(external_path(trust_policy_path, repo, "trust policy")) != original_policy:
        raise GateError("trusted policy changed during verification")
    if read_bytes(Path(policy["allowed_signers_file"])) != original_allowed_signers:
        raise GateError("trusted reviewer keys changed during verification")
    # Reverify signature if evidence or signer file could have changed during
    # long checks. The signed content and trusted keys must remain current.
    if evidence != load_json(evidence_path):
        raise GateError("review evidence changed during verification")
    verify_signature(evidence_path, signature_path, reviewer, policy["allowed_signers_file"], repo)
    return {
        "repository": policy["github_repository"], "reviewer": reviewer,
        "base_sha": base, "head_sha": head, "changed_files": sorted(actual),
        "checks_passed": completed, "signed_review_verified": True,
    }


def verify_created_pr(
    created_url: str, expected: dict[str, Any], base_ref: str, head_ref: str,
    title: str, draft: bool, repo: Path, timeout: int,
) -> dict[str, Any]:
    repo_name = expected["repository"]
    match = re.fullmatch(r"https://github\.com/([^/]+)/([^/]+)/pull/([0-9]+)", created_url.strip())
    if not match or f"{match.group(1)}/{match.group(2)}" != repo_name:
        raise GateError("created PR URL does not identify the trusted repository")
    number = int(match.group(3))
    raw = invoke(["gh", "api", f"repos/{repo_name}/pulls/{number}"], repo, timeout)
    try:
        pr = json.loads(raw)
        base, head = pr["base"], pr["head"]
        if (pr["number"] != number or pr["html_url"] != created_url.strip()
                or pr["state"] != "open" or pr["draft"] is not draft
                or pr["title"] != title
                or base["sha"] != expected["base_sha"] or head["sha"] != expected["head_sha"]
                or base["ref"] != base_ref or head["ref"] != head_ref
                or base["repo"]["full_name"] != repo_name
                or head["repo"]["full_name"] != repo_name):
            raise GateError("created PR remote identity, revision or state differs from intended values")
    except (ValueError, TypeError, KeyError) as exc:
        raise GateError("created PR response is invalid or incomplete") from exc
    return {"created_pr_url": created_url.strip(), "pr_number": number, "remote_verified": True}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", type=Path, default=Path.cwd())
    ap.add_argument("--base", required=True)
    ap.add_argument("--head", required=True, help="local and remote branch name")
    ap.add_argument("--evidence", type=Path, required=True)
    ap.add_argument("--signature", type=Path, required=True)
    ap.add_argument("--trust-policy", type=Path, required=True,
                    help="deployment-protected policy outside target repository")
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
        info = guard(args.repo, args.base, args.head, args.evidence, args.signature,
                     args.trust_policy, remote=args.remote, timeout=args.timeout)
    except GateError as exc:
        print(json.dumps({"status": "blocked", "reason": str(exc)}))
        return 2
    if args.create:
        cmd = ["gh", "pr", "create", "--base", args.base, "--head", args.head,
               "--title", args.title, "--body-file", str(args.body_file.resolve())]
        if args.draft:
            cmd.append("--draft")
        try:
            created_url = invoke(cmd, args.repo.resolve(), args.timeout)
        except GateError as exc:
            print(json.dumps({"status": "creation_failed_or_unknown", "reason": str(exc)}))
            return 3
        try:
            info.update(verify_created_pr(created_url, info, args.base, args.head,
                                          args.title, args.draft, args.repo.resolve(), args.timeout))
        except GateError as exc:
            print(json.dumps({"status": "created_unverified", "created_pr_url": created_url,
                              "reason": str(exc)}))
            return 3
    print(json.dumps({"status": "passed", **info}, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
