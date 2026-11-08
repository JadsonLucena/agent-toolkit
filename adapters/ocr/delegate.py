#!/usr/bin/env python3
"""Optional, read-only OpenCodeReview delegation bridge.

The output is *scaffolding*, never review evidence or an approval. No network
or LLM calls are performed by this bridge. OCR's delegate subcommands do not
use OCR's LLM; a locally installed CLI is required to use those subcommands.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

MAX_OUTPUT_BYTES = 8 * 1024 * 1024
BATCH_SIZE = 40
SUPPORTED_SCHEMA = "1"


class AdapterError(Exception):
    """A helper cannot provide trustworthy structured scaffolding."""


def invoke(args: list[str], *, cwd: Path, timeout: int) -> subprocess.CompletedProcess[bytes]:
    """Use argv only; never interpolate file paths, refs or OCR rules in a shell."""
    try:
        completed = subprocess.run(
            args, cwd=cwd, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, timeout=timeout, check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise AdapterError(f"command unavailable or timed out: {type(exc).__name__}") from exc
    if len(completed.stdout) > MAX_OUTPUT_BYTES or len(completed.stderr) > MAX_OUTPUT_BYTES:
        raise AdapterError("helper output exceeded size limit")
    return completed


def git(args: list[str], *, cwd: Path, timeout: int) -> bytes:
    result = invoke(["git", "--no-pager", *args], cwd=cwd, timeout=timeout)
    if result.returncode != 0:
        # stderr is untrusted and can contain repository content; avoid echoing it.
        raise AdapterError(f"git command failed ({result.returncode}): {args[0]}")
    return result.stdout


def decode_json(result: subprocess.CompletedProcess[bytes], command: str) -> dict[str, Any]:
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", errors="replace").lower()
        if "unknown flag" in detail and "--format" in detail:
            raise AdapterError("ocr CLI does not support JSON --format; requires OCR >= 1.9.0")
        raise AdapterError(f"ocr {command} failed with exit code {result.returncode}")
    try:
        parsed = json.loads(result.stdout.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AdapterError(f"ocr {command} did not produce valid JSON") from exc
    if not isinstance(parsed, dict) or parsed.get("schema_version") != SUPPORTED_SCHEMA:
        raise AdapterError(f"ocr {command} has unsupported JSON schema version")
    return parsed


def safe_ref(ref: str) -> str:
    if not ref or ref.startswith("-") or "\x00" in ref or "\n" in ref:
        raise AdapterError("invalid Git ref")
    return ref


def git_commit(ref: str, repo: Path, timeout: int) -> str:
    return git(["rev-parse", "--verify", "--end-of-options", f"{safe_ref(ref)}^{{commit}}"], cwd=repo, timeout=timeout).decode().strip()


def git_inventory(*, repo: Path, timeout: int, from_ref: str | None, to_ref: str | None, commit_ref: str | None) -> dict[str, Any]:
    root = Path(git(["rev-parse", "--show-toplevel"], cwd=repo, timeout=timeout).decode().strip()).resolve()
    if root != repo.resolve():
        raise AdapterError("--repo must name the Git worktree root")
    head = git_commit("HEAD", repo, timeout)
    mode = "workspace"
    target: dict[str, Any] = {"head_sha": head, "base_sha": None, "merge_base_sha": None}
    if commit_ref:
        mode = "commit"
        commit = git_commit(commit_ref, repo, timeout)
        # diff-tree without -m/-c omits merge commit changes. Review changes
        # introduced relative to the first parent (standard PR merge semantics).
        parents = git(["rev-list", "--parents", "-n", "1", commit], cwd=repo, timeout=timeout).decode("ascii").split()
        if not parents or parents[0] != commit:
            raise AdapterError("could not resolve commit parents")
        if len(parents) > 1:
            raw = git([
                "diff", "--no-ext-diff", "--no-textconv", "--no-renames",
                "--name-only", "-z", parents[1], commit,
            ], cwd=repo, timeout=timeout)
        else:
            raw = git([
                "diff-tree", "--root", "--no-renames", "--no-commit-id",
                "--name-only", "-r", "-z", commit,
            ], cwd=repo, timeout=timeout)
        target["head_sha"] = commit
        target["first_parent_sha"] = parents[1] if len(parents) > 1 else None
        target["merge_commit"] = len(parents) > 2
    elif from_ref and to_ref:
        mode = "range"
        base = git_commit(from_ref, repo, timeout)
        tip = git_commit(to_ref, repo, timeout)
        merge_base = git(["merge-base", base, tip], cwd=repo, timeout=timeout).decode().strip()
        target = {"head_sha": tip, "base_sha": base, "merge_base_sha": merge_base}
        raw = git(["diff", "--no-ext-diff", "--no-textconv", "--no-renames", "--name-only", "-z", merge_base, tip], cwd=repo, timeout=timeout)
    else:
        # Compare the worktree to HEAD, including the index. Disable rename
        # detection so both old and new paths are present in the native scope.
        raw = git([
            "diff", "--no-ext-diff", "--no-textconv", "--no-renames",
            "--name-only", "-z", "HEAD",
        ], cwd=repo, timeout=timeout)
        raw += git(["ls-files", "--others", "--exclude-standard", "-z"], cwd=repo, timeout=timeout)
    names = [x.decode("utf-8", errors="surrogateescape") for x in raw.split(b"\x00") if x]
    target["workspace_unpinned"] = mode == "workspace"
    return {"mode": mode, "target": target, "changed_files": sorted(set(names))}


def valid_path(path: Any) -> bool:
    if not isinstance(path, str) or not path or "\x00" in path or "\\" in path:
        return False
    normalized = Path(path)
    return not normalized.is_absolute() and ".." not in normalized.parts


def parse_preview(data: dict[str, Any], *, mode: str, target: dict[str, Any], repo: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if not isinstance(data.get("repository"), str) or not data["repository"] or Path(data["repository"]).resolve() != repo.resolve():
        raise AdapterError("ocr preview repository does not match the inspected Git worktree")
    if data.get("mode") != mode:
        raise AdapterError("ocr preview mode does not match Git target")
    if mode == "range":
        if data.get("from") != target["base_sha"] or data.get("to") != target["head_sha"]:
            raise AdapterError("ocr preview refs do not match resolved Git target")
        if data.get("merge_base") and data["merge_base"] != target["merge_base_sha"]:
            raise AdapterError("ocr preview merge base does not match Git")
    if mode == "commit" and data.get("commit") != target["head_sha"]:
        raise AdapterError("ocr commit preview does not match resolved Git target")
    lists = []
    for key in ("reviewable_files", "excluded_files"):
        entries = data.get(key)
        if not isinstance(entries, list):
            raise AdapterError(f"ocr preview missing {key} array")
        for entry in entries:
            if not isinstance(entry, dict) or not valid_path(entry.get("path")):
                raise AdapterError(f"ocr preview has invalid path in {key}")
        lists.append(entries)
    return lists[0], lists[1]


def parse_rules(data: dict[str, Any], requested: list[str]) -> list[dict[str, Any]]:
    groups = data.get("groups")
    if not isinstance(groups, list):
        raise AdapterError("ocr rule response missing groups array")
    allowed = set(requested)
    for group in groups:
        if not isinstance(group, dict) or not isinstance(group.get("rule"), str) or not isinstance(group.get("files"), list):
            raise AdapterError("ocr rule group has invalid structure")
        for path in group["files"]:
            if not valid_path(path) or path not in allowed:
                raise AdapterError("ocr rule group returned an unexpected path")
    return groups


def adapter(*, repo: Path, ocr_bin: str = "ocr", from_ref: str | None = None,
            to_ref: str | None = None, commit_ref: str | None = None, timeout: int = 30) -> dict[str, Any]:
    if timeout < 1 or timeout > 120:
        raise ValueError("timeout must be between 1 and 120 seconds")
    if commit_ref is not None and not commit_ref:
        raise ValueError("--commit requires a ref")
    if bool(from_ref) != bool(to_ref) or (commit_ref is not None and (from_ref or to_ref)):
        raise ValueError("supply either --commit or both --from and --to")
    repo = repo.resolve()
    inventory = git_inventory(repo=repo, timeout=timeout, from_ref=from_ref, to_ref=to_ref, commit_ref=commit_ref)
    mode, target = inventory["mode"], inventory["target"]
    result: dict[str, Any] = {
        "adapter": "alibaba-ocr-delegate", "status": "unavailable", "mode": mode,
        "repository": str(repo), "target": target,
        "git_changed_files": inventory["changed_files"],
        "native_review_required_files": inventory["changed_files"],
        "ocr_reviewable_files": [], "ocr_excluded_files": [], "ocr_rule_groups": [],
        "ocr_unaccounted_files": inventory["changed_files"], "ocr_unknown_files": [],
        "ocr_rule_gaps": [], "diagnostics": [],
        "review_performed": False, "review_verdict": None,
    }
    executable = shutil.which(ocr_bin)
    if not executable:
        result["diagnostics"].append("OCR not installed; native review remains required and independent")
        return result
    argv = [executable, "delegate", "preview", "--format", "json", "--repo", str(repo)]
    if mode == "range":
        argv += ["--from", target["base_sha"], "--to", target["head_sha"]]
    elif mode == "commit":
        argv += ["--commit", target["head_sha"]]
    try:
        preview = decode_json(invoke(argv, cwd=repo, timeout=timeout), "delegate preview")
        reviewable, excluded = parse_preview(preview, mode=mode, target=target, repo=repo)
        allowed = set(inventory["changed_files"])
        preview_paths = {e["path"] for e in [*reviewable, *excluded]}
        unknown = sorted(preview_paths - allowed)
        unaccounted = sorted(allowed - preview_paths)
        result["ocr_reviewable_files"] = reviewable
        result["ocr_excluded_files"] = excluded
        result["ocr_unknown_files"] = unknown
        result["ocr_unaccounted_files"] = unaccounted
        if unknown:
            result["diagnostics"].append("OCR mentioned files outside the independently inspected Git change inventory")
        if unaccounted:
            result["diagnostics"].append("OCR did not account for every Git changed file; all remain in native review scope")
        rule_paths = sorted({e["path"] for e in reviewable if not e["path"].startswith("-") and e["path"] in allowed})
        skipped = sorted({e["path"] for e in reviewable if e["path"].startswith("-")})
        if skipped:
            result["diagnostics"].append("Paths starting with '-' were not passed to OCR rule resolution")
        groups: list[dict[str, Any]] = []
        for start in range(0, len(rule_paths), BATCH_SIZE):
            chunk = rule_paths[start:start + BATCH_SIZE]
            rule_command = [executable, "delegate", "rule", "--format", "json", "--repo", str(repo), *chunk]
            response = decode_json(invoke(rule_command, cwd=repo, timeout=timeout), "delegate rule")
            groups.extend(parse_rules(response, chunk))
        covered_rules = {file for g in groups for file in g["files"]}
        result["ocr_rule_groups"] = groups
        result["ocr_rule_gaps"] = sorted(set(rule_paths) - covered_rules | set(skipped))
        if result["ocr_rule_gaps"]:
            result["diagnostics"].append("OCR returned no resolved rules for some reviewable paths")
        result["status"] = "available"
    except AdapterError as exc:
        result["status"] = "unsupported" if "requires OCR >= " in str(exc) or "unsupported JSON schema" in str(exc) else "failed"
        result["diagnostics"].append(str(exc))
        # Partial OCR output is untrusted when the operation fails. The independent
        # git inventory remains intact and native review must still cover it.
        result["ocr_rule_groups"] = []
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--from", dest="from_ref")
    parser.add_argument("--to", dest="to_ref")
    parser.add_argument("--commit", dest="commit_ref")
    parser.add_argument("--ocr-bin", default="ocr", help="Explicitly trusted local OCR executable")
    parser.add_argument("--timeout", type=int, default=30)
    args = parser.parse_args(argv)
    try:
        payload = adapter(repo=args.repo, ocr_bin=args.ocr_bin, from_ref=args.from_ref,
                          to_ref=args.to_ref, commit_ref=args.commit_ref, timeout=args.timeout)
    except (AdapterError, ValueError) as exc:
        print(json.dumps({"adapter": "alibaba-ocr-delegate", "status": "blocked", "diagnostics": [str(exc)],
                          "review_performed": False, "review_verdict": None}))
        return 2
    print(json.dumps(payload, ensure_ascii=True, sort_keys=True))
    # Helper failure is not a native-review failure: the machine-readable status
    # must still be inspected. Nonzero only means even the Git target was unsafe.
    return 0


if __name__ == "__main__":
    sys.exit(main())
