#!/usr/bin/env python3
"""Structural fitness checks for Agent Toolkit canonical artifacts.

No external dependencies. This checks observable structure, not semantic truth
or the safety of a real agent runtime.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
PATH_REF = re.compile(r"\x60((?:contexts|contracts)/[A-Za-z0-9_./-]+\.md)\x60")
MATRIX_ROW = re.compile(
    r"^\|\s*(Requirements|Design|Debugging|Implementation|Delivery|Testing|Review|Git|Cross-context)\s*\|\s*"
    r"\x60([^\x60]+)\x60\s*\|\s*(Rule|Skill|Command|Agent|Contract)\s*\|",
    re.MULTILINE,
)
MD_LINK = re.compile(r"\[[^\]]+\]\(([^)\s]+)\)")
COMMAND_SECTIONS = ("Intent", "Invocation", "Uses", "Inputs", "Output", "Boundary")
SKILL_FRONTMATTER = re.compile(
    r'\A---\r?\nname: (?P<name>[a-z0-9]+(?:-[a-z0-9]+)*)\r?\n'
    r'description: "(?P<description>[^"\n]+)"\r?\n---\r?\n',
)

# Portable frontmatter on Agents and canonical Rules exposed through the optional Cursor plugin.
FRONTMATTER = re.compile(r"\A---\r?\n.*?\r?\n---\r?\n", re.DOTALL)
AGENT_FRONTMATTER = re.compile(
    r'\A---\r?\nname: (?P<name>[a-z0-9]+(?:-[a-z0-9]+)*)\r?\n'
    r'description: "(?P<description>[^"\r\n]+)"\r?\n---\r?\n'
)
COMMAND_FRONTMATTER = AGENT_FRONTMATTER  # Same portable name/description shape; distinct invocation semantics.
CURSOR_RULE_FRONTMATTER = re.compile(
    r'\A---\r?\ndescription: "(?P<description>[^"\r\n]+)"\r?\n'
    r'alwaysApply: false\r?\n---\r?\n'
)
CURSOR_COMPONENTS = {"skills": "Skill", "commands": "Command", "agents": "Agent", "rules": "Rule"}


def classify(path: Path) -> tuple[str, str] | None:
    parts = path.parts
    if len(parts) == 2 and parts[0] == "contracts" and parts[1].endswith(".md"):
        return "Contract", "Cross-context"
    if len(parts) < 4 or parts[0] != "contexts":
        return None
    context = parts[1].capitalize()
    if context not in ("Requirements", "Design", "Debugging", "Implementation", "Delivery", "Testing", "Review", "Git"):
        return None
    if len(parts) == 4 and parts[3].endswith(".md"):
        kind = {"rules": "Rule", "agents": "Agent", "commands": "Command"}.get(parts[2])
        return (kind, context) if kind else None
    if len(parts) == 5 and parts[2] == "skills" and parts[4] == "SKILL.md":
        return "Skill", context
    return None


def section(content: str, name: str) -> str:
    match = re.search(
        r"(?ms)^## " + re.escape(name) + r"[ \t]*\n(.*?)(?=^## |\Z)",
        content,
    )
    return match.group(1) if match else ""




def lint_cursor_plugin(root: Path, discovered: dict[str, tuple[str, str]]) -> list[str]:
    """Check optional Cursor component references; cannot validate host execution."""
    manifest_path = root / ".cursor-plugin" / "plugin.json"
    if not manifest_path.exists():
        return []
    errors: list[str] = []
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (ValueError, OSError) as exc:
        return [f".cursor-plugin/plugin.json: invalid JSON: {exc}"]
    if not isinstance(manifest, dict) or manifest.get("name") != "agent-toolkit":
        return [".cursor-plugin/plugin.json: invalid plugin name or structure"]

    # Import from Disk reads a marketplace; source "." resolves to this
    # repository root containing the single canonical plugin manifest.
    marketplace = None
    marketplace_file = root / ".cursor-plugin" / "marketplace.json"
    if not marketplace_file.is_file():
        errors.append(".cursor-plugin/marketplace.json: required for folder marketplace import")
    else:
        try:
            marketplace = json.loads(marketplace_file.read_text(encoding="utf-8"))
        except (ValueError, OSError) as exc:
            errors.append(f".cursor-plugin/marketplace.json: invalid JSON: {exc}")
        else:
            if (not isinstance(marketplace, dict)
                    or marketplace.get("name") != "agent-toolkit"
                    or not isinstance(marketplace.get("plugins"), list)
                    or len(marketplace["plugins"]) != 1
                    or not isinstance(marketplace["plugins"][0], dict)
                    or marketplace["plugins"][0].get("name") != manifest["name"]
                    or marketplace["plugins"][0].get("source") != "."):
                errors.append(".cursor-plugin/marketplace.json: expected one root plugin with source '.'")
            # Cursor's documented marketplace format includes owner.name.
            owner = marketplace.get("owner") if isinstance(marketplace, dict) else None
            if (not isinstance(owner, dict)
                    or not isinstance(owner.get("name"), str)
                    or not owner["name"].strip()):
                errors.append(".cursor-plugin/marketplace.json: owner.name must be a non-empty string")

    # The marketplace and plugin are separate catalog surfaces for the same
    # canonical capability. Keep their public descriptions consistent.
    if (isinstance(marketplace, dict)
            and isinstance(marketplace.get("plugins"), list)
            and len(marketplace["plugins"]) == 1
            and isinstance(marketplace["plugins"][0], dict)
            and marketplace["plugins"][0].get("description") != manifest.get("description")):
        errors.append(".cursor-plugin/marketplace.json: plugin description must match plugin.json")

    allowed = {"name", "description", *CURSOR_COMPONENTS}
    if set(manifest) - allowed:
        errors.append(".cursor-plugin/plugin.json: unexpected plugin fields")
    if not isinstance(manifest.get("description"), str) or not manifest["description"].strip():
        errors.append(".cursor-plugin/plugin.json: missing description")

    for component, kind in CURSOR_COMPONENTS.items():
        paths = manifest.get(component)
        if not isinstance(paths, list) or not paths:
            errors.append(f".cursor-plugin/plugin.json: {component} requires a list of paths")
            continue
        resolved: set[str] = set()
        for raw in paths:
            if (not isinstance(raw, str) or not raw.startswith("./")
                    or ".." in PurePosixPath(raw).parts or "\\" in raw):
                errors.append(f".cursor-plugin/plugin.json: unsafe plugin path {raw!r}")
                continue
            relative = PurePosixPath(raw[2:])
            if not relative.parts:
                errors.append(f".cursor-plugin/plugin.json: unsafe plugin path {raw!r}")
                continue
            entry = root.joinpath(*relative.parts)
            if entry.is_dir() and component == "skills":
                candidates = list(entry.glob("*/SKILL.md"))
            elif entry.is_dir():
                # Cursor 3.29.15 treats array elements for Agents/Commands
                # as files; directory items are silently skipped by the host.
                errors.append(f".cursor-plugin/plugin.json: {component} requires explicit file paths: {raw}")
                continue
            elif entry.is_file():
                candidates = [entry]
            else:
                errors.append(f".cursor-plugin/plugin.json: missing plugin path {raw}")
                continue
            if not candidates:
                errors.append(f".cursor-plugin/plugin.json: empty plugin path {raw}")
            for candidate in candidates:
                rel = candidate.relative_to(root).as_posix()
                if rel in resolved:
                    errors.append(f".cursor-plugin/plugin.json: duplicate {component} artifact {rel}")
                resolved.add(rel)
                if (discovered.get(rel, (None, None))[0] != kind
                        and not (component == "skills" and rel == ".agents/skills/security-audit/SKILL.md")):
                    errors.append(f".cursor-plugin/plugin.json: noncanonical {component} artifact {rel}")
        expected = {p for p, (artifact_kind, _) in discovered.items() if artifact_kind == kind}
        if component == "skills":
            expected.add(".agents/skills/security-audit/SKILL.md")
        if resolved != expected:
            errors.append(f".cursor-plugin/plugin.json: {component} coverage mismatch"
                          f" (missing={sorted(expected - resolved)}, extra={sorted(resolved - expected)})")
        if component == "rules":
            # Plugin rule discovery is observed; contextual activation still requires Cursor E2E evidence.
            for rel in sorted(resolved):
                rule = root / rel
                if (rule.is_file() and not CURSOR_RULE_FRONTMATTER.match(
                        rule.read_text(encoding="utf-8"))):
                    errors.append(f"{rel}: invalid Cursor Rule frontmatter")
        if component == "agents":
            names: set[str] = set()
            for rel in sorted(resolved):
                file = root / rel
                if not file.is_file():
                    continue
                match = AGENT_FRONTMATTER.match(file.read_text(encoding="utf-8"))
                if not match or match.group("name") != file.stem:
                    errors.append(f"{rel}: invalid portable Agent name/description frontmatter")
                elif match.group("name") in names:
                    errors.append(f"{rel}: duplicate Agent name {match.group('name')}")
                else:
                    names.add(match.group("name"))

    # Metadata is a discovery/routing contract, not authority or evidence
    # that the Cursor host invoked the advertised procedure.
    seen_descriptions: dict[str, str] = {}
    seen_public_names: dict[tuple[str, str], str] = {}
    for rel, (kind, _) in sorted(discovered.items()):
        if kind not in {"Skill", "Agent", "Rule", "Command"}:
            continue
        if kind in {"Skill", "Agent", "Command"}:
            public_name = (Path(rel).parent.name if kind == "Skill"
                           else Path(rel).stem)
            key = (kind, public_name)
            if key in seen_public_names:
                errors.append(f"{rel}: duplicate {kind} public name {public_name} "
                              f"(also {seen_public_names[key]})")
            seen_public_names[key] = rel
        content = (root / rel).read_text(encoding="utf-8")
        pattern = {"Skill": SKILL_FRONTMATTER,
                   "Agent": AGENT_FRONTMATTER,
                   "Command": COMMAND_FRONTMATTER,
                   "Rule": CURSOR_RULE_FRONTMATTER}[kind]
        match = pattern.match(content)
        if match is None:
            if kind == "Command":
                errors.append(f"{rel}: missing portable Command name/description frontmatter")
            continue  # Other shape errors are reported by existing artifact checks.
        if kind == "Command" and match.group("name") != Path(rel).stem:
            errors.append(f"{rel}: invalid portable Command name (must match filename)")
        description = match.group("description").strip()
        if not 50 <= len(description) <= 260:
            errors.append(f"{rel}: metadata description must have 50-260 meaningful characters")
        normalized = re.sub(r"\s+", " ", description).casefold()
        if normalized in seen_descriptions:
            errors.append(f"{rel}: duplicate metadata description (also {seen_descriptions[normalized]})")
        seen_descriptions[normalized] = rel
    return errors


def lint_toolkit(root: Path) -> list[str]:
    root = root.resolve()
    errors: list[str] = []
    if not (root / "AGENTS.md").is_file():
        errors.append("AGENTS.md: missing repository agent instructions")
    architecture = root / "ARCHITECTURE.md"
    if not architecture.is_file():
        return ["ARCHITECTURE.md: missing canonical artifact matrix"]

    discovered: dict[str, tuple[str, str]] = {}
    for folder in ("contexts", "contracts"):
        base = root / folder
        if not base.is_dir():
            errors.append(f"{folder}/: missing canonical directory")
            continue
        for path in base.rglob("*.md"):
            rel = path.relative_to(root)
            kind = classify(rel)
            if kind is None:
                # Review templates are supporting documentation, not a new
                # canonical artifact kind. All Markdown links still get checked.
                if (len(rel.parts) == 4 and rel.parts[:3] ==
                        ("contexts", "review", "templates") and rel.suffix == ".md"):
                    continue
                # Supporting Skill references are lazily loaded and noncanonical.
                # Only directly linked files under an owning canonical Skill's
                # references/ directory are exempt from the artifact matrix.
                if (len(rel.parts) == 6 and rel.parts[0] == "contexts"
                        and rel.parts[2] == "skills"
                        and rel.parts[4] == "references"
                        and rel.suffix == ".md"):
                    owner = root.joinpath(*rel.parts[:4], "SKILL.md")
                    if owner.is_file() and classify(owner.relative_to(root)):
                        owner_text = owner.read_text(encoding="utf-8")
                        relative_ref = f"references/{rel.parts[5]}"
                        if f"({relative_ref})" in owner_text:
                            continue
                        errors.append(f"{rel}: unlinked supporting Skill reference")
                        continue
                errors.append(f"{rel}: invalid canonical artifact location")
            else:
                discovered[rel.as_posix()] = kind

    matrix: dict[str, tuple[str, str]] = {}
    for context, relative, kind in MATRIX_ROW.findall(architecture.read_text(encoding="utf-8")):
        full = relative if context == "Cross-context" else f"contexts/{context.lower()}/{relative}"
        if full in matrix:
            errors.append(f"ARCHITECTURE.md: duplicate canonical ownership of {full}")
        matrix[full] = (kind, context)
    for path, expected in discovered.items():
        if path not in matrix:
            errors.append(f"ARCHITECTURE.md: missing ownership entry for {path}")
        elif matrix[path] != expected:
            errors.append(f"ARCHITECTURE.md: incorrect owner/type for {path}")
    for path in matrix.keys() - discovered.keys():
        errors.append(f"ARCHITECTURE.md: ownership entry points to missing artifact {path}")

    skill_graph: dict[str, set[str]] = {}
    docs = [p for p in root.rglob("*.md") if ".git" not in p.parts]
    for path in docs:
        rel = path.relative_to(root).as_posix()
        content = path.read_text(encoding="utf-8")
        frontmatter = FRONTMATTER.match(content)
        title_source = content[frontmatter.end():] if frontmatter else content
        if not title_source.lstrip().startswith("# "):
            errors.append(f"{rel}: expected a level-one title")
        for ref in PATH_REF.findall(content):
            if ".." in Path(ref).parts or not (root / ref).is_file():
                errors.append(f"{rel}: broken reference {ref}")
        for link in MD_LINK.findall(content):
            if link.startswith(("http://", "https://", "mailto:", "#")):
                continue
            destination = link.split("#", 1)[0]
            if destination and not (path.parent / destination).exists():
                errors.append(f"{rel}: broken Markdown link {link}")

        info = discovered.get(rel)
        if info is None:
            continue
        kind, context = info
        headings = re.findall(r"(?m)^## (.+?)\s*$", content)
        if kind == "Command":
            positions = [headings.index(h) if h in headings else -1 for h in COMMAND_SECTIONS]
            if any(i < 0 for i in positions) or positions != sorted(positions):
                errors.append(f"{rel}: invalid command shape (expected ordered {COMMAND_SECTIONS})")
            for required in ("Invocation", "Boundary"):
                if not section(content, required).strip():
                    errors.append(f"{rel}: empty or missing {required} boundary section")
        elif kind == "Skill":
            frontmatter = SKILL_FRONTMATTER.match(content)
            directory = Path(rel).parent.name
            if frontmatter is None:
                errors.append(f"{rel}: skill must start with name and description frontmatter")
            elif frontmatter.group("name") != directory:
                errors.append(f"{rel}: skill name must match directory {directory}")
            for required in ("Purpose", "Uses", "Workflow", "Output"):
                if required not in headings or not section(content, required).strip():
                    errors.append(f"{rel}: skill missing {required} section")
            workflow = section(content, "Workflow")
            if "```mermaid" not in workflow and "state model" not in workflow.lower():
                errors.append(f"{rel}: workflow must be one diagram or follow its state model")
            # Skills can invoke other Skills from their Workflow section too.
            for target in PATH_REF.findall(content):
                if target != rel and classify(Path(target)) == ("Skill", context):
                    skill_graph.setdefault(rel, set()).add(target)

        if kind in ("Rule", "Skill"):
            # Commands are public invocation entry points, not dependencies of
            # Rules or Skills. Scan the *entire* body, not only ## Uses.
            # Match only actual canonical aliases, not URLs or filesystem paths.
            command_aliases = {
                f"/{PurePosixPath(target).parts[1]}/{PurePosixPath(target).stem}"
                for target, (target_kind, _) in discovered.items()
                if target_kind == "Command"
            }
            slash_refs = re.findall(
                r"(?<![A-Za-z0-9_./-])/[a-z][a-z0-9-]*/[a-z][a-z0-9-]*(?![A-Za-z0-9_/-])",
                content,
            )
            for invocation in set(slash_refs) & command_aliases:
                errors.append(f"{rel}: forbidden internal dependency on Command {invocation}")

        if rel in (
            "contexts/git/skills/manage-pull-request/SKILL.md",
            "contexts/git/commands/create-pull-request.md",
        ):
            if re.search(r"(?i)\bindependent\s+(?:code[- ]review|review)\s+(?:verdict|record|evidence)", content):
                errors.append(f"{rel}: advisory Code Review cannot be called independent")

        uses = section(content, "Uses")
        for target in PATH_REF.findall(uses):
            target_info = discovered.get(target)
            if target_info is None:
                continue
            target_kind, target_context = target_info
            allowed = {
                "Rule": {"Rule"},
                "Skill": {"Rule", "Skill", "Contract"},
                "Agent": {"Rule", "Skill", "Contract"},
                "Command": {"Rule", "Skill", "Agent", "Contract"},
                "Contract": set(),
            }
            if target_kind not in allowed[kind]:
                errors.append(f"{rel}: forbidden dependency {kind} -> {target_kind} ({target})")
            if kind in ("Rule", "Skill") and target_kind in ("Rule", "Skill") and context != target_context:
                errors.append(f"{rel}: cross-context internal dependency on {target}")
            if kind == "Skill" and target_kind == "Skill":
                skill_graph.setdefault(rel, set()).add(target)

        # Lexical regression checks are deliberately narrow: not a security proof.
        authority = (section(content, "Invocation") + section(content, "Boundary")).lower()
        if rel == "contexts/git/commands/create-pull-request.md":
            for word in ("push", "merg", "auto-merge", "releas"):
                if word not in authority:
                    errors.append(f"{rel}: missing PR authorization exclusion for {word}")
            if "does not authorize" not in authority:
                errors.append(f"{rel}: missing explicit non-authorization statement")
        if rel == "contexts/git/commands/create-pull-request.md":
            invocation = section(content, "Invocation").lower()
            for token in (
                "contexts/git/rules/pull-request.md",
                "contexts/git/skills/manage-pull-request/skill.md",
                "pre-creation quality gate",
            ):
                if token not in invocation:
                    errors.append(f"{rel}: missing pre-PR quality gate for {token}")
        if rel == "contexts/review/agents/code-reviewer.md":
            if "coordinate-review-team/SKILL.md" not in section(content, "Uses"):
                errors.append(f"{rel}: missing team-lead coordination: canonical Uses entry")
            for phrase in ("peer-to-peer messages", "review lead"):
                if phrase not in content.lower():
                    errors.append(f"{rel}: missing team-lead coordination: {phrase}")
        if rel == "contexts/review/skills/review-change/SKILL.md":
            if "coordinate-review-team/SKILL.md" not in section(content, "Uses"):
                errors.append(f"{rel}: missing collaborative review skill composition")
        if rel == "contexts/review/skills/coordinate-review-team/SKILL.md":
            if not section(content, "Collaboration Protocol").strip():
                errors.append(f"{rel}: missing team collaboration protocol")
            for phrase in ("peer-to-peer", "team-relayed", "native-solo", "challenge", "one `pass`",
                           "r2", "2–4", "r3", "3–5", "task", "task+resume",
                           "before any spawn", "n_justification", "finding-verifier"):
                if phrase not in content.lower():
                    errors.append(f"{rel}: missing team collaboration, proportional N or relay policy: {phrase}")
        if rel == "contexts/review/commands/review-code.md":
            if (
                "invocation authorizes read-only inspection" not in section(content, "Invocation").lower()
                or "read-only" not in section(content, "Boundary").lower()
            ):
                errors.append(f"{rel}: review invocation must remain read-only")
            if "does not authorize" not in authority:
                errors.append(f"{rel}: review command must forbid out-of-scope mutations")
            if "mandatory semantics; optional adapter" not in section(content, "Invocation").lower():
                errors.append(f"{rel}: missing mandatory host-neutral review preparation")
            if "--no-ocr" not in section(content, "Inputs").lower():
                errors.append(f"{rel}: missing native-only --no-ocr override")
        if rel == "contexts/review/skills/review-change/SKILL.md":
            if "mandatory host-neutral preparation" not in section(content, "Workflow").lower():
                errors.append(f"{rel}: review must bootstrap context before analysis")
        # Narrow policy-drift guards, not proof that a runtime actually runs checks.
        if rel == "contexts/git/rules/pull-request.md":
            strategy = section(content, "Pre-Implementation PR Strategy").lower()
            for phrase in ("before the first implementation mutation", "single coherent pr",
                           "independent prs", "stacked prs", "one increment", "read-only"):
                if phrase not in strategy:
                    errors.append(f"{rel}: missing pre-implementation PR strategy: {phrase}")
            lowered = content.lower()
            if "review_profile=advisory" not in lowered:
                errors.append(f"{rel}: ready review record must accept advisory")
            if "not required for ready" not in lowered:
                errors.append(f"{rel}: signed gate must not be required for ready")
            if "not-applicable" not in lowered:
                errors.append(f"{rel}: missing gate attestation must be not-applicable")
            if "an advisory pass never qualifies as ready" in lowered or "advisory `pass` never makes a pr ready" in lowered:
                errors.append(f"{rel}: advisory review must remain eligible for ready")
        if rel == "contexts/git/rules/git.md":
            for heading in ("Shared Quality-Gate Discovery and Evidence", "Pre-Commit Verification", "Pre-Pull-Request Verification"):
                if not section(content, heading).strip():
                    errors.append(f"{rel}: missing shared quality-gate policy: {heading}")
            for phrase in ("effective automation", "execute missing checks", "coverage is conditional"):
                if phrase not in content.lower():
                    errors.append(f"{rel}: missing quality-gate invariant: {phrase}")
        if rel == "contexts/git/skills/create-semantic-commits/SKILL.md":
            if "shared quality-gate discovery and evidence policy" not in content.lower():
                errors.append(f"{rel}: pre-commit must reuse shared quality-gate policy")
        if rel == "contexts/git/skills/manage-pull-request/SKILL.md":
            workflow = section(content, "Workflow").lower()
            if ("assessstrategy" not in workflow or "pre-implementation pr strategy" not in workflow
                    or workflow.index("assessstrategy") > workflow.index("selectmode")):
                errors.append(f"{rel}: missing PR strategy assessment before mode selection")
            for phrase in ("pre-creation quality gate", "shared quality-gate discovery and evidence"):
                if phrase not in workflow:
                    errors.append(f"{rel}: missing pre-PR check discovery or execution: {phrase}")
            if "contexts/git/rules/git.md" not in content or "contexts/git/rules/pull-request.md" not in content:
                errors.append(f"{rel}: missing pre-PR check discovery or execution: rule reference")
        if rel == "contexts/git/agents/git-engineer.md":
            responsibilities = section(content, "Responsibilities").lower()
            if ("apply **pre-implementation pr strategy**" not in responsibilities or
                    "manage-pull-request" not in responsibilities or
                    "plan" not in responsibilities):
                errors.append(f"{rel}: missing composite PR planning handoff")
        if rel == "contexts/git/commands/plan-pull-requests.md" and "read-only" not in authority:
            errors.append(f"{rel}: planning must remain read-only")
        if rel == "contexts/requirements/commands/validate-requirements.md" and (
            "does not authorize modifying" not in authority
        ):
            errors.append(f"{rel}: validation must not authorize specification mutation")

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> None:
        if node in visiting:
            errors.append(f"{node}: cyclic Skill -> Skill dependency")
            return
        if node in visited:
            return
        visiting.add(node)
        for child in sorted(skill_graph.get(node, ())):
            visit(child)
        visiting.remove(node)
        visited.add(node)

    for skill in sorted(skill_graph):
        visit(skill)
    errors.extend(lint_cursor_plugin(root, discovered))
    return sorted(set(errors))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="toolkit repository root")
    args = parser.parse_args()
    errors = lint_toolkit(args.root)
    for error in errors:
        print("ERROR:", error)
    print(f"Toolkit lint: {len(errors)} error(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
