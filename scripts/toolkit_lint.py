#!/usr/bin/env python3
"""Structural fitness checks for Agent Toolkit canonical artifacts.

No external dependencies. This checks observable structure, not semantic truth
or the safety of a real agent runtime.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH_REF = re.compile(r"\x60((?:contexts|contracts)/[A-Za-z0-9_./-]+\.md)\x60")
MATRIX_ROW = re.compile(
    r"^\|\s*(Requirements|Testing|Review|Git|Cross-context)\s*\|\s*"
    r"\x60([^\x60]+)\x60\s*\|\s*(Rule|Skill|Command|Agent|Contract)\s*\|",
    re.MULTILINE,
)
MD_LINK = re.compile(r"\[[^\]]+\]\(([^)\s]+)\)")
COMMAND_SECTIONS = ("Intent", "Invocation", "Uses", "Inputs", "Output", "Boundary")
SKILL_FRONTMATTER = re.compile(
    r'\A---\r?\nname: (?P<name>[a-z0-9]+(?:-[a-z0-9]+)*)\r?\n'
    r'description: "(?P<description>[^"\n]+)"\r?\n---\r?\n',
)


def classify(path: Path) -> tuple[str, str] | None:
    parts = path.parts
    if len(parts) == 2 and parts[0] == "contracts" and parts[1].endswith(".md"):
        return "Contract", "Cross-context"
    if len(parts) < 4 or parts[0] != "contexts":
        return None
    context = parts[1].capitalize()
    if context not in ("Requirements", "Testing", "Review", "Git"):
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


def lint_toolkit(root: Path) -> list[str]:
    root = root.resolve()
    errors: list[str] = []
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
        title_source = content
        if path.name == "SKILL.md":
            frontmatter = SKILL_FRONTMATTER.match(content)
            if frontmatter is not None:
                title_source = content[frontmatter.end():]
        if not title_source.lstrip().startswith("# "):
            errors.append(f"{rel}: expected a level-one title")
        # MIGRATION.md intentionally records superseded paths: they are history,
        # not active artifact references.
        if path.name != "MIGRATION.md":
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
