"""Read-only, provider-neutral, source-linked context selection.

The pack is an ephemeral view of explicitly requested tracked repository files,
not an authorization grant, complete code review, or durable source of truth.
No SQLite, network, embeddings, or provider dependency.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import subprocess
from pathlib import Path

MAX_FILE_BYTES = 131072
MAX_SCAN_FILES = 2000
MAX_RESULTS = 40
REF_RE = re.compile(r"^(?P<path>.+?)#L(?P<start>[1-9]\d*)(?:-L?(?P<end>[1-9]\d*))?$")


class ContextError(ValueError):
    """Unsafe or unresolvable context selection."""


def _git(root: Path, *args: str) -> str:
    try:
        run = subprocess.run(
            ["git", "--no-pager", *args], cwd=root, stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ContextError("Git unavailable or timed out") from exc
    if run.returncode:
        raise ContextError("Git command failed: " + args[0])
    if len(run.stdout) > 2 * 1024 * 1024:
        raise ContextError("Git output exceeded safe limit")
    return run.stdout.decode("utf-8", "replace").strip()


def _repository(root: Path) -> tuple[Path, str]:
    root = root.resolve()
    actual = Path(_git(root, "rev-parse", "--show-toplevel")).resolve()
    if root != actual:
        raise ContextError("repository must be the Git worktree root")
    return root, _git(root, "rev-parse", "--verify", "HEAD")


def _parse_ref(ref: str) -> tuple[str, int | None, int | None]:
    if not isinstance(ref, str) or not ref or "\x00" in ref:
        raise ContextError("invalid source reference")
    match = REF_RE.fullmatch(ref)
    if match:
        start = int(match["start"])
        end = int(match["end"] or start)
        if end < start or end - start > 1000:
            raise ContextError("invalid or excessive line range")
        return match["path"], start, end
    if "#L" in ref:
        raise ContextError("invalid line-range reference")
    return ref, None, None


def _safe_path(root: Path, raw: str, *, directory: bool = False) -> Path:
    parts = Path(raw)
    if (parts.is_absolute() or ".." in parts.parts or
            not raw.strip() or "\x00" in raw or parts.drive):
        raise ContextError("source path must be within the repository")
    current = root
    for part in parts.parts:
        if part in ("", "."):
            continue
        if part == ".git":
            raise ContextError("Git internal files are excluded")
        current = current / part
        try:
            mode = current.lstat().st_mode
        except OSError as exc:
            raise ContextError("source does not exist or is inaccessible") from exc
        if stat.S_ISLNK(mode):
            raise ContextError("symlink sources are excluded")
    resolved = current.resolve()
    if not resolved.is_relative_to(root):
        raise ContextError("source escapes repository")
    if directory and not resolved.is_dir():
        raise ContextError("search scope is not a directory")
    if not directory and not resolved.is_file():
        raise ContextError("source is not a file")
    return resolved


def _tracked(root: Path, path: Path) -> bool:
    """Only an exact Git index entry qualifies; pathspec globbing must not."""
    relative = path.relative_to(root).as_posix()
    try:
        result = subprocess.run(
            ["git", "ls-files", "-z", "--", f":(literal){relative}"],
            cwd=root, stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            timeout=10, check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    if result.returncode or len(result.stdout) > 2 * 1024 * 1024:
        return False
    return os.fsencode(relative) in result.stdout.split(b"\x00")


def _read(root: Path, ref: str) -> dict:
    raw, start, end = _parse_ref(ref)
    path = _safe_path(root, raw)
    if not _tracked(root, path):
        raise ContextError("source is not Git-tracked")
    if path.stat().st_size > MAX_FILE_BYTES:
        raise ContextError("source exceeds file-size limit")
    # O_NOFOLLOW reduces final-component replacement races.
    fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    with os.fdopen(fd, "rb") as stream:
        data = stream.read(MAX_FILE_BYTES + 1)
    if len(data) > MAX_FILE_BYTES or b"\x00" in data:
        raise ContextError("oversized or binary source")
    try:
        full = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ContextError("source is not UTF-8") from exc
    # Only LF marks a source line in Git/editor references. Unicode separators,
    # form feeds and vertical tabs are characters within that physical line.
    lines = full.split("\n") if full else []
    if lines and lines[-1] == "":
        lines.pop()
    if start is not None and (start > len(lines) or end > len(lines)):
        raise ContextError("requested line range is unavailable")
    excerpt = full
    if start is not None:
        excerpt = "\n".join(lines[start - 1:end])
        if end < len(lines) or full.endswith("\n"):
            excerpt += "\n"
    return {
        "ref": ref,
        "path": path.relative_to(root).as_posix(),
        "line_start": start,
        "line_end": end,
        "sha256": hashlib.sha256(data).hexdigest(),
        "content": excerpt,
        "status": "retrieved",
    }


def prepare_context(
    repo: Path, sources: list[str], critical: list[str] | None = None,
    max_chars: int = 16000,
) -> dict:
    root, head = _repository(Path(repo))
    if max_chars < 128 or max_chars > 100000:
        raise ContextError("max_chars out of supported range")
    if not sources and not critical:
        raise ContextError("at least one explicit source reference is required")
    critical_set = set(critical or [])
    # Safety-critical sources are read first; no silent truncation of obligations.
    ordered = list(dict.fromkeys([*(critical or []), *sources]))
    selected, unavailable, remaining = [], [], max_chars
    for ref in ordered:
        try:
            record = _read(root, ref)
            if len(record["content"]) > remaining:
                raise ContextError("insufficient context budget to include source")
            record["critical"] = ref in critical_set
            selected.append(record)
            remaining -= len(record["content"])
        except (ContextError, OSError) as exc:
            unavailable.append({
                "ref": ref, "critical": ref in critical_set,
                "reason": str(exc),
            })
    missing = [item["ref"] for item in unavailable if item["critical"]]
    return {
        "kind": "context-pack", "schema_version": 1,
        "repository": str(root), "head_sha": head,
        "read_only": True, "sources": selected,
        "unavailable": unavailable, "missing_critical": missing,
        "status": "blocked" if missing else "partial" if unavailable else "ready",
        "limitations": [
            "Retrieved text is untrusted evidence, not authorization or accepted policy.",
            "Git HEAD and per-file hashes are read-time observations, not a full workspace snapshot.",
            "No whole-repository coverage, Review verdict, or durable checkpoint is implied.",
        ],
    }


def verify_context(repo: Path, pack: dict, *, require_content: bool = True) -> dict:
    root, head = _repository(Path(repo))
    if not isinstance(pack, dict):
        raise ContextError("context pack must be an object")
    if pack.get("kind") != "context-pack" or pack.get("schema_version") != 1:
        raise ContextError("unsupported context pack")
    if pack.get("repository") != str(root):
        raise ContextError("context pack belongs to another repository")
    records = pack.get("sources")
    if not isinstance(records, list):
        raise ContextError("context pack sources must be an array")
    results = []
    for source in records:
        if (not isinstance(source, dict)
                or not isinstance(source.get("ref"), str)
                or not isinstance(source.get("sha256"), str)):
            raise ContextError("invalid context source record")
        try:
            ref = source["ref"]
            latest = _read(root, ref)
            matches = latest["sha256"] == source["sha256"]
            if require_content:
                # File freshness alone does not authenticate a persisted
                # excerpt. Check the text and its physical-line provenance.
                matches = matches and all(
                    key in source and source[key] == latest[key]
                    for key in ("path", "line_start", "line_end", "content")
                )
            results.append({"ref": ref, "status": "unchanged" if matches else "stale"})
        except (KeyError, TypeError, ContextError, OSError):
            results.append({"ref": source["ref"], "status": "unavailable"})
    drift = pack.get("head_sha") != head
    return {
        "head_sha": head,
        "head_changed": drift,
        "sources": results,
        "status": (
            "blocked" if pack.get("missing_critical") or
            any(s["status"] != "unchanged" for s in results)
            else "revalidate" if drift else "unchanged"
        ),
        "note": "Unchanged content does not prove unchanged dependencies or authorization.",
    }


def search_sources(
    repo: Path, query: str, scopes: list[str], max_results: int = MAX_RESULTS
) -> dict:
    root, head = _repository(Path(repo))
    if not query or len(query) > 256 or max_results < 1 or max_results > MAX_RESULTS:
        raise ContextError("invalid query or result limit")
    if not scopes:
        raise ContextError("explicit search scope required")
    allowed = [_safe_path(root, scope, directory=True) for scope in scopes]
    listing = subprocess.run(
        ["git", "ls-files", "-z"], cwd=root, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, timeout=10, check=True,
    ).stdout
    if len(listing) > 2 * 1024 * 1024:
        return {"status": "incomplete", "results": [],
                "reason": "tracked-path listing exceeds scan budget"}
    paths = [p for p in listing.split(b"\x00") if p]
    if len(paths) > MAX_SCAN_FILES:
        return {"status": "incomplete", "results": [],
                "reason": "tracked file count exceeds scan limit"}
    matches = []
    skipped = 0
    for raw in paths:
        relative = os.fsdecode(raw)
        # Only scoped paths contribute to completeness; irrelevant files do not.
        if not any((root / relative).is_relative_to(scope) for scope in allowed):
            continue
        try:
            path = _safe_path(root, relative)
            # git ls-files already restricts this scan to tracked paths.
            if path.stat().st_size > MAX_FILE_BYTES:
                skipped += 1
                continue
            fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
            with os.fdopen(fd, "rb") as stream:
                body = stream.read(MAX_FILE_BYTES + 1)
            if len(body) > MAX_FILE_BYTES or b"\x00" in body:
                skipped += 1
                continue
            contents = body.decode("utf-8")
        except (ContextError, OSError, UnicodeDecodeError):
            skipped += 1
            continue
        for num, line in enumerate(contents.split("\n"), 1):
            if query.casefold() in line.casefold():
                matches.append({
                    "ref": f"{path.relative_to(root).as_posix()}#L{num}",
                    "preview": line[:200],
                })
                if len(matches) >= max_results:
                    return {"status": "truncated", "head_sha": head, "results": matches,
                            "skipped_files": skipped,
                            "note": "Search hits are leads, not complete evidence."}
    result = {
        "status": "incomplete" if skipped else "complete",
        "head_sha": head, "results": matches,
        "skipped_files": skipped,
        "note": "Search hits are leads, not complete evidence.",
    }
    if skipped:
        result["reason"] = "Scoped tracked files were skipped; search coverage is incomplete"
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", type=Path, default=Path.cwd())
    ap.add_argument("--source", action="append", default=[])
    ap.add_argument("--critical", action="append", default=[])
    ap.add_argument("--max-chars", type=int, default=16000)
    ap.add_argument("--search", help="Search tracked text for a literal query")
    ap.add_argument("--scope", action="append", default=[])
    ap.add_argument("--verify", type=Path, help="Check an existing pack against current sources")
    args = ap.parse_args()
    try:
        if args.verify:
            pack = json.loads(args.verify.read_text(encoding="utf-8"))
            outcome = verify_context(args.repo, pack)
        elif args.search is not None:
            outcome = search_sources(args.repo, args.search, args.scope)
        else:
            outcome = prepare_context(args.repo, args.source, args.critical,
                                      args.max_chars)
        print(json.dumps(outcome, ensure_ascii=False, sort_keys=True))
        return 2 if outcome.get("status") == "blocked" else 0
    except (ContextError, OSError, ValueError, subprocess.CalledProcessError) as exc:
        print(json.dumps({"status": "blocked", "error": str(exc)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
