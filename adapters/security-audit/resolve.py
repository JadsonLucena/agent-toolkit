#!/usr/bin/env python3
"""Read-only, offline resolver for the approved Cloudflare audit skill."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

TOOLKIT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ROOT = TOOLKIT_ROOT / ".agents/skills/security-audit"
LOCK_PATH = TOOLKIT_ROOT / "skills-lock.json"
EXPECTED_SOURCE = "cloudflare/security-audit-skill"
EXPECTED_SKILL_PATH = "skills/security-audit/SKILL.md"

# Non-exhaustive investigation hints, not coverage or vulnerability findings.
REFERENCE_HINTS = (
    ("AI-AND-LLM.md", r"agent|prompt|llm|model|mcp|tool.call|ai[_/-]"),
    ("WEB-PROTOCOL-AND-AUTH.md", r"auth|oauth|jwt|session|cookie|http|route|api|csrf|proxy"),
    ("SUPPLY-CHAIN-AND-RELEASE.md", r"dependency|package|lock|github|workflow|build|release|plugin|ci[/_.-]"),
    ("DATA-ISOLATION-AND-LIFECYCLE.md", r"tenant|privacy|personal|data|storage|cache|export|backup|migration"),
    ("CLOUD-AND-DEPLOYMENT.md", r"cloud|infra|iam|deploy|docker|kubernetes|terraform|container"),
    ("PROTOCOLS-RPC-AND-MESSAGING.md", r"rpc|queue|broker|message|event|webhook|grpc"),
    ("RESOURCE-EXHAUSTION-AND-AVAILABILITY.md", r"quota|rate.limit|memory|timeout|worker|availability|dos"),
    ("CLIENT-SIDE.md", r"browser|frontend|client|dom|react|vue|script"),
    ("MEMORY-SAFETY-AND-BINARY.md", r"unsafe|native|binary|kernel|ffi|pointer"),
    ("DESKTOP-MOBILE-AND-LOCAL-IPC.md", r"desktop|mobile|ipc|webview|deep.link"),
)


class UnapprovedSkill(ValueError):
    """Installed files do not match approved upstream content."""


def _approved_lock(lock_path: Path) -> dict[str, str]:
    if lock_path.is_symlink():
        raise UnapprovedSkill("skills lock must not be a symlink")
    data = json.loads(lock_path.read_text(encoding="utf-8"))
    entry = data["skills"]["security-audit"]
    if (data.get("version") != 2
            or entry.get("source") != EXPECTED_SOURCE
            or entry.get("sourceType") != "github"
            or entry.get("skillPath") != EXPECTED_SKILL_PATH
            or not re.fullmatch(r"[0-9a-f]{40}", str(entry.get("commit", "")))
            or not re.fullmatch(r"[0-9a-f]{64}", str(entry.get("computedHash", "")))):
        raise UnapprovedSkill("invalid approved skill lock entry")
    return entry


def content_hash(root: Path) -> str:
    """Skills CLI v2 hash: relative path, NUL, content byte length, NUL, content."""
    if root.is_symlink() or not root.is_dir():
        raise UnapprovedSkill("skill root is not a regular directory")
    digest = hashlib.sha256()
    files: list[tuple[str, Path]] = []
    for path in root.rglob("*"):
        rel = path.relative_to(root)
        if path.is_symlink():
            raise UnapprovedSkill("symlinks are not permitted in approved skill")
        if any(part in {".git", "__pycache__", "__pypackages__"} for part in rel.parts):
            continue
        if path.is_dir() or path.name == "metadata.json":
            continue
        if not path.is_file():
            raise UnapprovedSkill("nonregular skill entry")
        files.append((rel.as_posix(), path))
    for name, path in sorted(files, key=lambda item: item[0].encode("utf-8")):
        raw = path.read_bytes()
        if b"\0" not in raw:
            raw = raw.replace(b"\r\n", b"\n")
        digest.update(name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(str(len(raw)).encode("ascii"))
        digest.update(b"\0")
        digest.update(raw)
    return digest.hexdigest()


def adapter(
    *, changed_files: list[Any] | None = None, concerns: list[str] | None = None,
    skill_root: Path | None = None, enabled: bool = True,
    lock_path: Path = LOCK_PATH,
) -> dict[str, Any]:
    """Return scoped, non-authoritative reference hints; never execute vendor code."""
    result: dict[str, Any] = {
        "status": "disabled" if not enabled else "unavailable",
        "mode": "guidance", "selected_references": [], "diagnostics": [],
        "review_performed": False, "review_verdict": None,
    }
    if not enabled:
        return result
    root = Path(skill_root) if skill_root is not None else DEFAULT_ROOT
    root = root.expanduser()
    if not root.exists():
        result["diagnostics"].append("approved local skill is absent")
        return result
    try:
        entry = _approved_lock(lock_path)
        if content_hash(root) != entry["computedHash"]:
            raise UnapprovedSkill("installed skill content does not match approved lock hash")
        if not (root / "SKILL.md").is_file():
            raise UnapprovedSkill("SKILL.md missing")
        result["status"] = "available"
        result["source"] = {
            "repository": EXPECTED_SOURCE, "commit": entry["commit"],
            "content_sha256": entry["computedHash"],
        }
        result["skill_root"] = str(root.resolve())
        values = [str(item.get("path", "")) if isinstance(item, dict) else str(item)
                  for item in (changed_files or [])]
        values.extend(str(item) for item in (concerns or []))
        haystack = "\n".join(values).lower()
        result["selected_references"] = [
            {"path": name, "reason": "matched bounded security concern"}
            for name, pattern in REFERENCE_HINTS
            if re.search(pattern, haystack) and (root / name).is_file()
        ]
    except (OSError, ValueError, KeyError, TypeError) as exc:
        result["status"] = "rejected"
        result["diagnostics"].append(f"approved skill verification failed: {type(exc).__name__}: {exc}")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--security-audit-root", type=Path)
    parser.add_argument("--no-security-audit", action="store_true")
    parser.add_argument("--changed-file", action="append", default=[])
    parser.add_argument("--concern", action="append", default=[])
    args = parser.parse_args()
    result = adapter(
        changed_files=args.changed_file, concerns=args.concern,
        skill_root=args.security_audit_root, enabled=not args.no_security_audit,
    )
    print(json.dumps(result, sort_keys=True, ensure_ascii=False))
    return 1 if result["status"] == "rejected" else 0


if __name__ == "__main__":
    raise SystemExit(main())
