#!/usr/bin/env python3
"""Portable review-context entrypoint with automatic optional OCR discovery.

Prepares a Git inventory plus supplementary OCR delegation data; it never
performs Code Review or confers PASS. A host agent consumes the JSON and
performs the full review under the canonical Review context.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ocr"))
from delegate import adapter as ocr_adapter, AdapterError  # noqa: E402


def prepare_context(
    repo: Path, *, base: str | None = None, head: str | None = None,
    commit: str | None = None, allow_ocr: bool = True, timeout: int = 30,
) -> dict[str, Any]:
    # Delegation mode never calls a provider LLM. OCR is allowed only by the
    # host policy; without approval use the same Git-native inventory path.
    helper = ocr_adapter(
        repo=repo, from_ref=base, to_ref=head, commit_ref=commit,
        ocr_bin="ocr" if allow_ocr else "__agent_toolkit_ocr_disabled__",
        timeout=timeout,
    )
    return {
        "kind": "review-context", "schema_version": "1",
        "target": helper["target"], "mode": helper["mode"],
        "changed_files": helper["git_changed_files"],
        "review_required_files": helper["native_review_required_files"],
        "optional_helpers": {
            "ocr": {
                "status": "disabled" if not allow_ocr else helper["status"],
                "reviewable_files": helper["ocr_reviewable_files"],
                "excluded_files": helper["ocr_excluded_files"],
                "rule_groups": helper["ocr_rule_groups"],
                "unaccounted_files": helper["ocr_unaccounted_files"],
                "diagnostics": helper["diagnostics"],
            }
        },
        "review_performed": False, "review_verdict": None,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", type=Path, default=Path.cwd())
    ap.add_argument("--from", dest="base")
    ap.add_argument("--to", dest="head")
    ap.add_argument("--commit")
    ap.add_argument("--no-ocr", action="store_true")
    ap.add_argument("--timeout", type=int, default=30)
    args = ap.parse_args(argv)
    try:
        payload = prepare_context(
            args.repo, base=args.base, head=args.head,
            commit=args.commit, allow_ocr=not args.no_ocr, timeout=args.timeout,
        )
    except (AdapterError, ValueError, OSError) as exc:
        print(json.dumps({"kind": "review-context", "status": "blocked",
                          "diagnostics": [str(exc)], "review_performed": False,
                          "review_verdict": None}))
        return 2
    print(json.dumps(payload, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
