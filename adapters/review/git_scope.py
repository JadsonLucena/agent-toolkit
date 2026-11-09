"""Neutral Git change inventory shared by native review and optional helpers.

No OCR imports, OCR process discovery, or provider invocation exist here.
"""
from __future__ import annotations

import hashlib
import os
import stat
import subprocess
from pathlib import Path
from typing import Any

MAX_OUTPUT_BYTES = 8 * 1024 * 1024


class GitScopeError(Exception):
    """Git change inventory could not be established."""


def git(args: list[str], *, cwd: Path, timeout: int) -> bytes:
    try:
        result = subprocess.run(
            ["git", "--no-pager", *args], cwd=cwd, stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout, check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise GitScopeError(f"Git unavailable or timed out: {type(exc).__name__}") from exc
    if result.returncode:
        raise GitScopeError(f"git command failed ({result.returncode}): {args[0]}")
    if len(result.stdout) > MAX_OUTPUT_BYTES or len(result.stderr) > MAX_OUTPUT_BYTES:
        raise GitScopeError("Git inventory output exceeded size limit")
    return result.stdout


def workspace_fingerprint(repo: Path, timeout: int) -> str:
    """Hash HEAD, index, tracked worktree diff, and untracked bytes read-only.

    A workspace without a fingerprint cannot be a stable review target.
    No Git writes (including write-tree), OCR imports or symlink traversal.
    """
    digest = hashlib.sha256()
    for label, args in (
        (b"head", ["rev-parse", "--verify", "HEAD"]),
        (b"index", ["ls-files", "--stage", "-z"]),
        (b"status", ["status", "--porcelain=v1", "-z", "--untracked-files=all"]),
        (b"tracked", ["diff", "--no-ext-diff", "--no-textconv", "--binary", "HEAD"]),
    ):
        data = git(args, cwd=repo, timeout=timeout)
        digest.update(label + b"\x00" + len(data).to_bytes(8, "big") + data)
    untracked = sorted(x for x in git(
        ["ls-files", "--others", "--exclude-standard", "-z"],
        cwd=repo, timeout=timeout,
    ).split(b"\x00") if x)
    for raw in untracked:
        relative = os.fsdecode(raw)
        item = repo / relative
        try:
            mode = item.lstat().st_mode
            if stat.S_ISLNK(mode):
                payload = os.fsencode(os.readlink(item))
                tag = b"symlink"
            elif stat.S_ISREG(mode):
                # O_NOFOLLOW prevents replacing an untracked file with a
                # symlink to content outside the approved repository.
                fd = os.open(item, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
                try:
                    with os.fdopen(fd, "rb") as stream:
                        h = hashlib.sha256()
                        while chunk := stream.read(1024 * 1024):
                            h.update(chunk)
                        payload = h.digest()
                except BaseException:
                    raise
                tag = b"regular-sha256"
            else:
                raise GitScopeError("unsupported untracked workspace object")
        except OSError as exc:
            raise GitScopeError(f"cannot fingerprint untracked file: {type(exc).__name__}") from exc
        digest.update(b"untracked\x00" + raw + b"\x00" + tag + b"\x00" + payload)
    return digest.hexdigest()


def safe_ref(ref: str) -> str:
    if not ref or ref.startswith("-") or "\x00" in ref or "\n" in ref:
        raise GitScopeError("invalid Git ref")
    return ref


def git_commit(ref: str, repo: Path, timeout: int) -> str:
    return git(["rev-parse", "--verify", "--end-of-options", f"{safe_ref(ref)}^{{commit}}"], cwd=repo, timeout=timeout).decode().strip()


def git_inventory(*, repo: Path, timeout: int, from_ref: str | None, to_ref: str | None, commit_ref: str | None) -> dict[str, Any]:
    root = Path(git(["rev-parse", "--show-toplevel"], cwd=repo, timeout=timeout).decode().strip()).resolve()
    if root != repo.resolve():
        raise GitScopeError("--repo must name the Git worktree root")
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
            raise GitScopeError("could not resolve commit parents")
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
    if mode == "workspace":
        target["workspace_fingerprint_sha256"] = workspace_fingerprint(repo, timeout)
    return {"mode": mode, "target": target, "changed_files": sorted(set(names))}


