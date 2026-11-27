#!/usr/bin/env python3
"""Static coverage check for the optional Claude-format plugin.

This does not run Claude Code, VS Code, or Copilot. No host behavior is attested.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
COMPONENTS = ("skills", "commands", "agents")
ALLOWED_KEYS = {
    "name", "displayName", "version", "description", "author", "repository",
    "license", "keywords", *COMPONENTS,
}
SEMVER = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")
NAME = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
FRONTMATTER_NAME = re.compile(r"\A---\r?\nname: ([a-z][a-z0-9]*(?:-[a-z0-9]+)*)\r?\n")


def canonical_files(root: Path, kind: str) -> set[str]:
    pattern = {
        "skills": "contexts/*/skills/*/SKILL.md",
        "commands": "contexts/*/commands/*.md",
        "agents": "contexts/*/agents/*.md",
    }[kind]
    return {path.relative_to(root).as_posix() for path in root.glob(pattern)}


def lint_claude_plugin(root: Path) -> list[str]:
    """Validate a single root-installable package with direct canonical references."""
    root = root.resolve()
    path = root / ".claude-plugin/plugin.json"
    if not path.is_file():
        return [".claude-plugin/plugin.json: manifest is missing"]
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, OSError) as exc:
        return [f".claude-plugin/plugin.json: invalid JSON: {exc}"]
    if not isinstance(manifest, dict):
        return [".claude-plugin/plugin.json: expected an object"]

    errors: list[str] = []
    if manifest.get("name") != "agent-toolkit":
        errors.append(".claude-plugin/plugin.json: unexpected plugin name")
    if not isinstance(manifest.get("version"), str) or not SEMVER.fullmatch(manifest["version"]):
        errors.append(".claude-plugin/plugin.json: version must be explicit SemVer for strict validation")
    if set(manifest) - ALLOWED_KEYS:
        errors.append(".claude-plugin/plugin.json: unsupported manifest fields")
    if (not isinstance(manifest.get("description"), str)
            or not manifest["description"].strip()):
        errors.append(".claude-plugin/plugin.json: missing description")
    if (not isinstance(manifest.get("author"), dict)
            or not isinstance(manifest["author"].get("name"), str)
            or not manifest["author"]["name"].strip()):
        errors.append(".claude-plugin/plugin.json: missing author.name")

    cursor_manifest_path = root / ".cursor-plugin/plugin.json"
    if cursor_manifest_path.is_file():
        try:
            cursor = json.loads(cursor_manifest_path.read_text(encoding="utf-8"))
            if manifest.get("description") != cursor.get("description"):
                errors.append(".claude-plugin/plugin.json: public descriptions must match Cursor")
        except (ValueError, OSError) as exc:
            errors.append(f".cursor-plugin/plugin.json: invalid JSON: {exc}")

    for kind in COMPONENTS:
        raw_paths = manifest.get(kind)
        if not isinstance(raw_paths, list) or not raw_paths:
            errors.append(f".claude-plugin/plugin.json: {kind} requires nonempty path list")
            continue
        found: set[str] = set()
        for raw in raw_paths:
            if (not isinstance(raw, str) or not raw.startswith("./")
                    or raw in {"./", "."} or "\\" in raw
                    or ".." in PurePosixPath(raw).parts):
                errors.append(f".claude-plugin/plugin.json: unsafe {kind} path {raw!r}")
                continue
            entry = (root / raw[2:]).resolve()
            if not entry.is_relative_to(root):
                errors.append(f".claude-plugin/plugin.json: escaping {kind} path {raw!r}")
                continue
            if kind == "skills" and entry.is_dir():
                paths = list(entry.glob("*/SKILL.md"))
                if not paths:
                    errors.append(f".claude-plugin/plugin.json: empty skills directory {raw}")
            elif kind != "skills" and entry.is_file() and entry.suffix == ".md":
                paths = [entry]
            else:
                errors.append(f".claude-plugin/plugin.json: invalid {kind} path {raw}")
                continue
            for candidate in paths:
                if not candidate.is_file() or not candidate.resolve().is_relative_to(root):
                    errors.append(f".claude-plugin/plugin.json: unsafe referenced artifact {candidate}")
                    continue
                rel = candidate.relative_to(root).as_posix()
                if rel in found:
                    errors.append(f".claude-plugin/plugin.json: duplicate {kind} artifact {rel}")
                found.add(rel)
                match = FRONTMATTER_NAME.match(candidate.read_text(encoding="utf-8"))
                name = candidate.parent.name if kind == "skills" else candidate.stem
                if not NAME.fullmatch(name) or not match or match.group(1) != name:
                    errors.append(f".claude-plugin/plugin.json: invalid {kind} identity {rel}")
        expected = canonical_files(root, kind)
        if found != expected:
            errors.append(f".claude-plugin/plugin.json: {kind} coverage mismatch "
                          f"(missing={sorted(expected - found)}, extra={sorted(found - expected)})")
    return sorted(set(errors))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    errors = lint_claude_plugin(args.root)
    for error in errors:
        print(error)
    print(f"Claude plugin static validation: {len(errors)} error(s); HOST NOT TESTED")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
