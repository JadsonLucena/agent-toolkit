#!/usr/bin/env python3
"""Portable review-context entrypoint with automatic optional OCR discovery.

Prepares a Git inventory plus supplementary OCR delegation data; it never
performs Code Review or confers PASS. A host agent consumes the JSON and
performs the full review under the canonical Review context.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from git_scope import git_inventory, GitScopeError


def ocr_adapter(**kwargs: Any) -> dict[str, Any]:
    """Load OCR code only in the explicitly permitted OCR-first branch."""
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ocr"))
    from delegate import adapter  # noqa: PLC0415

    return adapter(**kwargs)


def prepare_context(
    repo: Path, *, base: str | None = None, head: str | None = None,
    commit: str | None = None, base_branch: str | None = None,
    allow_ocr: bool = True, timeout: int = 30, output_language: str | None = None,
    review_profile: str = "advisory",
) -> dict[str, Any]:
    """Freeze Git scope independently of optional helpers and platform APIs."""
    if review_profile not in ("advisory", "gate"):
        raise ValueError("review_profile must be advisory or gate")
    if timeout < 1 or timeout > 120 or (commit is not None and not commit):
        raise ValueError("invalid timeout or empty commit")
    if bool(base) != bool(head) or (commit is not None and (base or head)):
        raise ValueError("supply either commit or from/to")
    if base_branch and (base or head or commit):
        raise ValueError("--base-branch cannot be combined with explicit scope")
    if output_language is not None and not re.fullmatch(
        r"[A-Za-z]{2,8}(?:-[A-Za-z0-9]{1,8})*", output_language,
    ):
        raise ValueError("invalid --output-language")
    repo = repo.resolve()
    inventory = git_inventory(
        repo=repo, timeout=timeout, from_ref=base, to_ref=head,
        commit_ref=commit, base_branch=base_branch,
    )
    if allow_ocr:
        helper = ocr_adapter(
            repo=repo, from_ref=base or base_branch,
            to_ref=head or ("HEAD" if base_branch else None),
            commit_ref=commit, ocr_bin="ocr", timeout=timeout,
        )
        helper_status = helper["status"]
    else:
        helper = {
            "status": "disabled", "ocr_reviewable_files": [],
            "ocr_excluded_files": [], "ocr_rule_groups": [],
            "ocr_unaccounted_files": [], "diagnostics": [],
        }
        helper_status = "disabled"
    groups = []
    for item in helper.get("ocr_rule_groups", []):
        if not isinstance(item, dict):
            continue
        group = dict(item)
        if str(group.get("source", "")).lower() == "system":
            group["generic"] = True
            group["binding"] = False
        groups.append(group)
    excluded = [
        {"path": item["path"], "reason": item.get("exclude_reason", "helper-filtered")}
        for item in helper.get("ocr_excluded_files", [])
        if isinstance(item, dict) and item.get("path") in inventory["changed_files"]
    ]
    return {
        "kind": "review-context", "schema_version": "1",
        "review_profile": review_profile,
        "repository": str(repo),
        "scope": {"base_ref": base, "head_ref": head,
                  "commit_ref": commit, "base_branch": base_branch},
        "target": inventory["target"], "mode": inventory["mode"],
        "changed_files": inventory["changed_files"],
        "review_required_files": inventory["changed_files"],
        "helper_excluded_requires_native_review": excluded,
        "warnings": inventory.get("warnings", []),
        "output_language": output_language,
        "optional_helpers": {"ocr": {
            "status": helper_status,
            "reviewable_files": helper.get("ocr_reviewable_files", []),
            "excluded_files": helper.get("ocr_excluded_files", []),
            "rule_groups": groups,
            "unaccounted_files": helper.get("ocr_unaccounted_files", []),
            "diagnostics": helper.get("diagnostics", []),
        }},
        "review_performed": False, "review_verdict": None,
    }

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", type=Path, default=Path.cwd())
    ap.add_argument("--from", dest="base")
    ap.add_argument("--to", dest="head")
    ap.add_argument("--commit")
    ap.add_argument("--base-branch")
    ap.add_argument("--no-ocr", action="store_true")
    ap.add_argument("--timeout", type=int, default=30)
    ap.add_argument("--output-language")
    ap.add_argument("--review-profile", choices=("advisory", "gate"), default="advisory")
    args = ap.parse_args(argv)
    try:
        payload = prepare_context(
            args.repo, base=args.base, head=args.head, commit=args.commit,
            base_branch=args.base_branch, allow_ocr=not args.no_ocr,
            timeout=args.timeout, output_language=args.output_language,
            review_profile=args.review_profile,
        )
    except (GitScopeError, ValueError, OSError) as exc:
        print(json.dumps({"kind": "review-context", "status": "blocked",
                          "diagnostics": [str(exc)], "review_performed": False,
                          "review_verdict": None}))
        return 2
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0

if __name__ == "__main__":
    sys.exit(main())
