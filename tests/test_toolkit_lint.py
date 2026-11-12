"""Negative and positive regressions for structural architecture checks."""
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from toolkit_lint import lint_toolkit  # noqa: E402


class ToolkitLintTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        shutil.copytree(ROOT / "contexts", self.root / "contexts")
        shutil.copytree(ROOT / "contracts", self.root / "contracts")
        if (ROOT / "adapters").is_dir():
            shutil.copytree(ROOT / "adapters", self.root / "adapters",
                            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        for name in ("ARCHITECTURE.md", "README.md", "MIGRATION.md"):
            shutil.copy2(ROOT / name, self.root / name)

    def change(self, path, old, new):
        target = self.root / path
        text = target.read_text(encoding="utf-8")
        self.assertIn(old, text)
        target.write_text(text.replace(old, new, 1), encoding="utf-8")

    def assert_error(self, needle):
        errors = lint_toolkit(self.root)
        self.assertTrue(any(needle in error for error in errors), errors)

    def test_current_canonical_repository_passes(self):
        self.assertEqual([], lint_toolkit(self.root))

    def test_missing_optional_adapter_documentation_is_reported(self):
        (self.root / "adapters" / "ocr" / "README.md").unlink()
        self.assert_error("broken Markdown link adapters/ocr/README.md")

    def test_broken_canonical_reference(self):
        self.change(
            "contexts/requirements/skills/definition/SKILL.md",
            "contexts/requirements/skills/example-discovery/SKILL.md",
            "contexts/requirements/skills/never-existed/SKILL.md",
        )
        self.assert_error("broken reference")

    def test_skill_cannot_depend_on_command(self):
        self.change(
            "contexts/requirements/skills/definition/SKILL.md",
            "## Uses\n",
            "## Uses\n\n* Command: \x60contexts/requirements/commands/shape-change.md\x60\n",
        )
        self.assert_error("forbidden dependency Skill -> Command")

    def test_missing_command_section(self):
        self.change("contexts/git/commands/commit.md", "## Boundary\n", "## Scope\n")
        self.assert_error("invalid command shape")

    def test_duplicate_canonical_owner(self):
        target = self.root / "ARCHITECTURE.md"
        content = target.read_text(encoding="utf-8")
        line = "| Git | \x60rules/git.md\x60 | Rule |"
        match = next(row for row in content.splitlines() if row.startswith(line))
        target.write_text(content + "\n" + match + "\n", encoding="utf-8")
        self.assert_error("duplicate canonical ownership")

    def test_read_only_boundary_regression(self):
        self.change(
            "contexts/git/commands/plan-pull-requests.md",
            "read-only",
            "non-mutating",
        )
        self.change(
            "contexts/git/commands/plan-pull-requests.md",
            "read-only",
            "non-mutating",
        )
        self.assert_error("planning must remain read-only")

    def test_review_context_is_canonical(self):
        self.assertEqual([], lint_toolkit(self.root))
        self.assertTrue((self.root / "contexts/review/agents/code-reviewer.md").is_file())

    def test_review_command_requires_runtime_bootstrap(self):
        self.change(
            "contexts/review/commands/review-code.md",
            "Mandatory semantics; optional adapter",
            "Manual preparation optional",
        )
        self.assert_error("missing mandatory host-neutral review preparation")

    def test_no_ocr_override_is_not_optional_policy(self):
        self.change(
            "contexts/review/commands/review-code.md",
            "`--no-ocr` (or equivalent host-native setting)",
            "`--no-helper`",
        )
        self.assert_error("missing native-only --no-ocr override")

    def test_review_workflow_requires_context_before_analysis(self):
        self.change(
            "contexts/review/skills/review-change/SKILL.md",
            "Mandatory host-neutral preparation",
            "Optional, unordered preparation",
        )
        self.assert_error("review must bootstrap context before analysis")

    def test_review_command_cannot_become_mutating(self):
        self.change(
            "contexts/review/commands/review-code.md",
            "Invocation authorizes read-only inspection",
            "Invocation authorizes inspection",
        )
        self.assert_error("review invocation must remain read-only")

    def test_skill_requires_name_and_description(self):
        target = self.root / "contexts/git/skills/create-semantic-commits/SKILL.md"
        text = target.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\n"))
        target.write_text(text.split("---\n", 2)[-1], encoding="utf-8")
        self.assert_error("name and description frontmatter")

    def test_preimplementation_pr_strategy_rule_cannot_be_removed(self):
        self.change(
            "contexts/git/rules/pull-request.md",
            "before the first implementation mutation",
            "after all implementation is complete",
        )
        self.assert_error("missing pre-implementation PR strategy")

    def test_pr_skill_must_assess_strategy_before_mode(self):
        self.change(
            "contexts/git/skills/manage-pull-request/SKILL.md",
            "AssessStrategy[\"Pre-Implementation PR Strategy in pull-request.md\"]",
            "UnplannedShortcut[\"Skip PR strategy\"]",
        )
        self.assert_error("missing PR strategy assessment before mode selection")

    def test_git_agent_must_route_composite_pr_planning(self):
        self.change(
            "contexts/git/agents/git-engineer.md",
            "Apply **Pre-Implementation PR Strategy**",
            "Ignore **Pre-Implementation PR Strategy**",
        )
        self.assert_error("missing composite PR planning handoff")

    def test_ready_pr_does_not_require_signed_gate(self):
        self.change(
            "contexts/git/rules/pull-request.md",
            "not required for ready",
            "required for ready",
        )
        self.assert_error("signed gate must not be required for ready")

    def test_pr_creation_requires_independent_review(self):
        self.change(
            "contexts/git/commands/create-pull-request.md",
            "contexts/git/rules/pull-request.md",
            "optional analysis",
        )
        self.assert_error("missing pre-PR quality gate")

    def test_pr_creation_requires_lint(self):
        self.change(
            "contexts/git/commands/create-pull-request.md",
            "contexts/git/skills/manage-pull-request/SKILL.md",
            "optional procedure",
        )
        self.assert_error("missing pre-PR quality gate")

    def test_shared_gate_policy_is_required(self):
        self.change(
            "contexts/git/rules/git.md",
            "## Shared Quality-Gate Discovery and Evidence",
            "## Unshared Checks",
        )
        self.assert_error("missing shared quality-gate policy")

    def test_precommit_must_reference_shared_policy(self):
        self.change(
            "contexts/git/skills/create-semantic-commits/SKILL.md",
            "shared quality-gate discovery and evidence policy",
            "local ad-hoc verification",
        )
        self.assert_error("pre-commit must reuse shared quality-gate policy")

    def test_prepr_hook_discovery_cannot_be_removed(self):
        self.change(
            "contexts/git/skills/manage-pull-request/SKILL.md",
            "Pre-Creation Quality Gate",
            "local checklist",
        )
        self.assert_error("missing pre-PR check discovery or execution")

    def test_prepr_must_execute_missing_checks(self):
        self.change(
            "contexts/git/commands/create-pull-request.md",
            "Pre-Creation Quality Gate",
            "local checklist",
        )
        self.assert_error("missing pre-PR quality gate")

    def test_review_team_lead_cannot_drop_coordination(self):
        self.change(
            "contexts/review/agents/code-reviewer.md",
            "coordinate-review-team/SKILL.md",
            "omitted-coordination.md",
        )
        self.assert_error("missing team-lead coordination")

    def test_review_workflow_cannot_drop_collaboration_skill(self):
        self.change(
            "contexts/review/skills/review-change/SKILL.md",
            "coordinate-review-team/SKILL.md",
            "not-a-team-SKILL.md",
        )
        self.assert_error("missing collaborative review skill composition")

    def test_team_messaging_and_fallback_are_required(self):
        self.change(
            "contexts/review/skills/coordinate-review-team/SKILL.md",
            "## Collaboration Protocol",
            "## Absent Protocol",
        )
        self.assert_error("missing team collaboration protocol")

    def test_review_team_requires_r3_proportional_n(self):
        self.change(
            "contexts/review/skills/coordinate-review-team/SKILL.md",
            "R3 | 3–5 relevant roles",
            "R3 | unlimited roles",
        )
        self.assert_error("missing team collaboration, proportional N or relay policy")

    def test_review_team_requires_task_resume(self):
        self.change(
            "contexts/review/skills/coordinate-review-team/SKILL.md",
            "`Task+resume`",
            "`arbitrary sequential review`",
        )
        self.assert_error("missing team collaboration, proportional N or relay policy")

    def test_team_specialists_are_canonical(self):
        self.assertEqual([], lint_toolkit(self.root))
        specialist_paths = (
            "specification-reviewer", "correctness-reviewer", "security-reviewer",
            "reliability-reviewer", "testing-reviewer", "architecture-reviewer",
            "finding-verifier",
        )
        for name in specialist_paths:
            self.assertTrue((self.root / "contexts" / "review" / "agents" / f"{name}.md").is_file())

    def test_review_contract_cannot_be_removed_from_architecture(self):
        self.change(
            "ARCHITECTURE.md",
            "| Cross-context | `contracts/review-evidence.md` | Contract |",
            "| Removed | `contracts/review-evidence.md` | Contract |",
        )
        self.assert_error("missing ownership entry for contracts/review-evidence.md")

    def test_cycle_between_skills(self):
        self.change(
            "contexts/requirements/skills/example-discovery/SKILL.md",
            "## Uses\n",
            "## Uses\n\n* Skill: \x60contexts/requirements/skills/definition/SKILL.md\x60\n",
        )
        self.assert_error("cyclic Skill -> Skill")


if __name__ == "__main__":
    unittest.main()
