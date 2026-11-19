"""Explicitly opt-in SQLite FTS5 trigram search with native-first selection.

Never imports SQLite or opens an index in ordinary native searches. An index
is only created after explicit build approval; search can use an existing
current index when the native bounded scan is incomplete, or when explicitly
requested. Results remain untrusted search leads, never evidence of authority.
"""
from __future__ import annotations

import argparse
import json
import os
import stat
import subprocess
import tempfile
from contextlib import closing
from pathlib import Path

from adapters.context import native

MAX_INDEX_FILES = 8000
MAX_INDEX_BYTES = 32 * 1024 * 1024
MAX_DB_BYTES = 256 * 1024 * 1024
SCHEMA_VERSION = 2


class IndexError(ValueError):
    """Optional index is unavailable, stale or unsuitable for this request."""


def _sqlite():
    """Import only on an explicitly needed indexed operation."""
    try:
        import sqlite3
        with closing(sqlite3.connect(":memory:")) as check:
            check.execute("CREATE VIRTUAL TABLE probe USING fts5(text, tokenize='trigram')")
        return sqlite3
    except Exception:
        return None


def _scope_paths(root: Path, scopes: list[str]) -> tuple[list[Path], list[str]]:
    if not scopes:
        raise native.ContextError("explicit search scope required")
    paths = [native._safe_path(root, scope, directory=True) for scope in scopes]
    unique = sorted(set(paths))
    return unique, [p.relative_to(root).as_posix() for p in unique]


def _clean(root: Path) -> bool:
    """Index never claims current coverage over uncommitted tracked changes."""
    return not native._git(root, "status", "--porcelain", "--untracked-files=no")


def _check_index_flags(root: Path, scopes: list[str]) -> None:
    """Refuse Git bits that hide modified tracked files from git status."""
    try:
        result = subprocess.run(
            ["git", "ls-files", "-v", "-z", "--",
             *[f":(literal){scope}" for scope in scopes]],
            cwd=root, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, timeout=12, check=True,
        )
    except (subprocess.CalledProcessError, OSError, subprocess.TimeoutExpired) as exc:
        raise IndexError("cannot verify Git tracked-file flags") from exc
    if len(result.stdout) > 2 * 1024 * 1024:
        raise IndexError("Git flag inventory exceeds index budget")
    for entry in result.stdout.split(b"\x00"):
        if entry and not entry.startswith(b"H "):
            # 'h' = assume-unchanged, 'S' = skip-worktree.
            # Unknown markers cannot establish reliable freshness either.
            raise IndexError(
                "Git assume-unchanged/skip-worktree or unsupported index flags "
                "make indexed source freshness unverifiable"
            )


def _private_db(root: Path, db: Path, *, for_build: bool) -> Path:
    path = Path(db).expanduser()
    if not path.is_absolute():
        raise IndexError("index database path must be absolute")
    if not path.parent.is_dir() or path.parent.is_symlink():
        raise IndexError("index parent must be an existing private directory")
    if os.name == "posix" and stat.S_IMODE(path.parent.stat().st_mode) & 0o077:
        raise IndexError("index parent must be private (0700)")
    resolved = path.resolve()
    if resolved.is_relative_to(root):
        raise IndexError("index database must be outside the repository")
    if path.is_symlink():
        raise IndexError("index database cannot be a symlink")
    if path.exists():
        if not path.is_file() or path.stat().st_size > MAX_DB_BYTES:
            raise IndexError("index is invalid or exceeds size budget")
        if os.name == "posix" and stat.S_IMODE(path.stat().st_mode) & 0o077:
            raise IndexError("index database must be owner-only (0600)")
    elif not for_build:
        raise IndexError("no prebuilt index; automatic creation is forbidden")
    return path


def _indexable(path: Path) -> bool:
    name = path.name.lower()
    return not (
        name.startswith(".env") or "secret" in name or "credential" in name
        or name.endswith((".pem", ".key", ".p12", ".pfx", ".asc"))
    )


def _git_paths(root: Path, scopes: list[str]) -> list[str]:
    """Enumerate only exact approved directories, never wildcard pathspecs."""
    allowed = [native._safe_path(root, scope, directory=True) for scope in scopes]
    pathspecs = [f":(literal){scope}" for scope in scopes]
    try:
        output = subprocess.run(
            ["git", "ls-files", "-z", "--", *pathspecs], cwd=root,
            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, timeout=12, check=True,
        ).stdout
    except (subprocess.CalledProcessError, OSError, subprocess.TimeoutExpired) as exc:
        raise IndexError("unable to enumerate scoped Git files") from exc
    if len(output) > 2 * 1024 * 1024:
        raise IndexError("Git file inventory exceeds index budget")
    names = [os.fsdecode(p) for p in output.split(b"\x00") if p]
    if len(names) > MAX_INDEX_FILES:
        raise IndexError("too many scoped files; reduce index scope")
    for name in names:
        relative = Path(name)
        if relative.is_absolute() or ".." in relative.parts:
            raise IndexError("Git returned an invalid relative source path")
        # Membership is checked lexically here. The builder separately
        # rejects and counts symlinks, submodules, and other ineligible files.
        candidate = root / relative
        if not any(candidate.is_relative_to(scope) for scope in allowed):
            raise IndexError("Git inventory includes a path outside the approved literal scopes")
    return names


def build_index(repo: Path, scopes: list[str], db: Path, *, approved: bool = False) -> dict:
    """Explicit authorized local cache operation; never runs during search."""
    if not approved:
        raise IndexError("building a persistent code index requires explicit approval")
    root, head = native._repository(Path(repo))
    _, relative_scopes = _scope_paths(root, scopes)
    if not _clean(root):
        raise IndexError("tracked worktree is dirty; cannot build a pinned index")
    sqlite3 = _sqlite()
    if sqlite3 is None:
        return {"status": "unavailable", "backend": "native",
                "reason": "SQLite with FTS5 trigram is not installed"}
    path = _private_db(root, db, for_build=True)
    paths = _git_paths(root, relative_scopes)
    _check_index_flags(root, relative_scopes)
    fd, temp = tempfile.mkstemp(prefix=".fts5-", suffix=".sqlite3", dir=path.parent)
    os.close(fd)
    connection = None
    indexed, skipped, size = 0, 0, 0
    try:
        connection = sqlite3.connect(temp)
        connection.execute("CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
        connection.execute(
            "CREATE VIRTUAL TABLE sources USING fts5(" 
            "path UNINDEXED, content UNINDEXED, folded, tokenize='trigram')"
        )
        for item in paths:
            try:
                source = native._safe_path(root, item)
                if not _indexable(source) or source.stat().st_size > native.MAX_FILE_BYTES:
                    skipped += 1
                    continue
                fd_source = os.open(source, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
                with os.fdopen(fd_source, "rb") as stream:
                    raw = stream.read(native.MAX_FILE_BYTES + 1)
                if len(raw) > native.MAX_FILE_BYTES or b"\x00" in raw:
                    skipped += 1
                    continue
                content = raw.decode("utf-8")
            except (native.ContextError, OSError, UnicodeDecodeError):
                skipped += 1
                continue
            size += len(raw)
            if size > MAX_INDEX_BYTES:
                raise IndexError("source byte budget exceeded; reduce index scope")
            connection.execute(
                "INSERT INTO sources(path,content,folded) VALUES(?,?,?)",
                (item, content, content.casefold()),
            )
            indexed += 1
        if native._repository(root)[1] != head or not _clean(root):
            raise IndexError("source changed while building index")
        _check_index_flags(root, relative_scopes)
        values = {
            "repository": str(root), "head_sha": head,
            "scopes": json.dumps(relative_scopes), "indexed": str(indexed),
            "skipped": str(skipped),
        }
        connection.executemany("INSERT INTO meta(key,value) VALUES(?,?)", values.items())
        connection.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
        connection.commit()
        connection.close()
        connection = None
        if path.exists() and path.is_symlink():
            raise IndexError("index target changed into a symlink")
        os.replace(temp, path)
    finally:
        if connection is not None:
            connection.close()
        if os.path.exists(temp):
            os.unlink(temp)
    return {
        "status": "ready" if not skipped else "partial",
        "backend": "sqlite-fts5", "head_sha": head,
        "indexed": indexed, "skipped": skipped, "scopes": relative_scopes,
        "note": "Only explicitly scoped eligible text files are cached; not a full-repository audit.",
    }


def _indexed_search(
    repo: Path, query: str, scopes: list[str], db: Path, max_results: int
) -> dict:
    root, head = native._repository(Path(repo))
    requested, _ = _scope_paths(root, scopes)
    if not _clean(root):
        raise IndexError("dirty tracked worktree invalidates indexed retrieval")
    if len(query) < 3 or any(ch in query for ch in "\r\n\x00"):
        raise IndexError("trigram search requires at least 3 characters on one line")
    sqlite3 = _sqlite()
    if sqlite3 is None:
        raise IndexError("SQLite FTS5 trigram is unavailable")
    path = _private_db(root, db, for_build=False)
    try:
        with closing(sqlite3.connect(path.as_uri() + "?mode=ro", uri=True, timeout=3.0)) as conn:
            if conn.execute("PRAGMA user_version").fetchone()[0] != SCHEMA_VERSION:
                raise IndexError("unknown or incompatible index schema")
            values = dict(conn.execute("SELECT key,value FROM meta"))
            if values.get("repository") != str(root) or values.get("head_sha") != head:
                raise IndexError("index belongs to another repo or stale Git HEAD")
            saved = json.loads(values["scopes"])
            allowed = [native._safe_path(root, s, directory=True) for s in saved]
            if not all(any(q.is_relative_to(a) for a in allowed) for q in requested):
                raise IndexError("requested search scope exceeds approved indexed scope")
            _check_index_flags(root, saved)
            skipped = int(values["skipped"])
            phrase = '"' + query.casefold().replace('"', '""') + '"'
            matches = []
            truncated = False
            # FTS candidate retrieval; post-filter lines to retain native literal semantics.
            cursor = conn.execute(
                "SELECT path,content FROM sources WHERE folded MATCH ? ORDER BY path",
                (phrase,),
            )
            for relative, content in cursor:
                source = root / relative
                if not any(source.is_relative_to(q) for q in requested):
                    continue
                for number, line in enumerate(content.split("\n"), 1):
                    if query.casefold() in line.casefold():
                        matches.append({"ref": f"{relative}#L{number}", "preview": line[:200]})
                        if len(matches) >= max_results:
                            truncated = True
                            break
                if truncated:
                    break
            # Even a truncated result must be checked against current source state.
            if native._repository(root)[1] != head or not _clean(root):
                raise IndexError("source changed during index search")
            _check_index_flags(root, saved)
            return {
                "status": "truncated" if truncated else "incomplete" if skipped else "complete",
                "backend": "sqlite-fts5", "head_sha": head,
                "results": matches, "coverage": "partial" if skipped else "eligible-text",
                "note": "Search hits are leads, not complete evidence.",
            }
    except (sqlite3.Error, KeyError, ValueError, TypeError) as exc:
        if isinstance(exc, IndexError):
            raise
        raise IndexError("index cannot be safely read") from exc


def _supplement_native(previous: dict, indexed: dict, max_results: int) -> dict:
    """Never discard independently observed native hits for a partial scan."""
    combined = []
    seen = set()
    for record in [*previous.get("results", []), *indexed.get("results", [])]:
        if record["ref"] not in seen:
            seen.add(record["ref"])
            combined.append(record)
    overflow = len(combined) > max_results or indexed["status"] == "truncated"
    return {
        **indexed,
        "backend": "native+sqlite-fts5",
        "status": "truncated" if overflow else "incomplete",
        "results": combined[:max_results],
        "coverage": "partial",
        "native_hits_preserved": len(previous.get("results", [])),
        "native_skipped_files": previous.get("skipped_files", 0),
        "note": "Native and indexed hits are leads; incomplete scan coverage remains explicit.",
    }


def search(
    repo: Path, query: str, scopes: list[str], *,
    db: Path | None = None, mode: str = "auto", enable_optional: bool = False,
    max_results: int = native.MAX_RESULTS,
) -> dict:
    """Native always wins unless incomplete or caller explicitly selects indexed."""
    if mode not in {"auto", "native", "indexed"}:
        raise native.ContextError("unknown search mode")
    if not query or len(query) > 256 or not 1 <= max_results <= native.MAX_RESULTS:
        raise native.ContextError("invalid query or result limit")
    # No SQLite probing, DB inspection or index builds in the default path.
    if mode == "native" or (mode == "auto" and not enable_optional):
        result = native.search_sources(repo, query, scopes, max_results)
        return {**result, "backend": "native", "index_used": False}
    previous = None
    if mode == "auto":
        previous = native.search_sources(repo, query, scopes, max_results)
        if previous["status"] != "incomplete":
            return {**previous, "backend": "native", "index_used": False,
                    "selection_reason": "native_sufficient"}
    if db is None:
        reason = "no previously approved index path supplied"
    else:
        try:
            result = _indexed_search(repo, query, scopes, db, max_results)
            if previous is not None:
                result = _supplement_native(previous, result, max_results)
            return {**result, "index_used": True,
                    "selection_reason": "explicit" if mode == "indexed" else "native_incomplete"}
        except (IndexError, native.ContextError, OSError) as exc:
            reason = str(exc)
    result = previous if previous is not None else native.search_sources(
        repo, query, scopes, max_results
    )
    return {**result, "backend": "native", "index_used": False,
            "optional_index": "not_used", "fallback_reason": reason}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", type=Path, default=Path.cwd())
    ap.add_argument("--db", type=Path)
    ap.add_argument("--scope", action="append", default=[])
    ap.add_argument("--build", action="store_true", help="Create an explicitly approved local index")
    ap.add_argument("--approve-cache", action="store_true", help="Consent to persist scoped code text")
    ap.add_argument("--search")
    ap.add_argument("--mode", choices=("native", "auto", "indexed"), default="auto")
    ap.add_argument("--enable-optional", action="store_true",
                    help="Allow existing FTS5 only if native scan is incomplete")
    args = ap.parse_args()
    try:
        if args.build:
            if args.search is not None or args.db is None:
                raise IndexError("build requires --db and cannot be combined with --search")
            out = build_index(args.repo, args.scope, args.db, approved=args.approve_cache)
        else:
            if args.search is None:
                raise native.ContextError("provide --search or explicitly --build")
            out = search(args.repo, args.search, args.scope, db=args.db,
                         mode=args.mode, enable_optional=args.enable_optional)
        print(json.dumps(out, ensure_ascii=False, sort_keys=True))
        return 2 if out["status"] in ("blocked", "unavailable") else 0
    except (IndexError, native.ContextError, OSError, ValueError) as exc:
        print(json.dumps({"status": "blocked", "error": str(exc)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
