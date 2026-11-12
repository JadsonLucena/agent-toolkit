"""Regression of canonical conflict-resolution instructions (not a behavioral merge oracle)."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def source(path):
    return (ROOT / path).read_text(encoding="utf-8")


class MergeResolutionPolicyTests(unittest.TestCase):
    def test_architecture_owns_command_and_skill(self):
        architecture = source("ARCHITECTURE.md")
        self.assertIn("| Git | `skills/resolve-merge-conflicts/SKILL.md` | Skill |", architecture)
        self.assertIn("| Git | `commands/resolve-conflicts.md` | Command |", architecture)

    def test_three_way_and_marker_free_interference_are_required(self):
        policy = source("contexts/git/rules/git.md")
        skill = source("contexts/git/skills/resolve-merge-conflicts/SKILL.md")
        for phrase in ("common ancestor", "stage 2", "stage 3", "rebase/cherry-pick",
                       "semantic interference without conflict markers"):
            self.assertIn(phrase, policy)
        self.assertIn("base, ours and theirs", skill)
        self.assertIn("marker-free semantic interference", skill)

    def test_strategy_taxonomy_and_decision_escalation(self):
        policy = source("contexts/git/rules/git.md")
        for name in ("ACCEPT_OURS", "ACCEPT_THEIRS", "COMBINE_BOTH",
                     "PARTIAL_COMBINATION", "SYNTHESIZE_NEW", "DEFER_DECISION"):
            self.assertIn(name, policy)
        self.assertIn("decision-needed", policy)
        self.assertIn("interaction tests", policy)

    def test_default_read_only_scoped_write_and_no_implicit_continuation(self):
        command = source("contexts/git/commands/resolve-conflicts.md")
        skill = source("contexts/git/skills/resolve-merge-conflicts/SKILL.md")
        for phrase in ("read-only", "explicit", "Staging", "continuing"):
            self.assertIn(phrase.lower(), command.lower())
        self.assertIn("no implicit continue/commit/push", skill)
        self.assertIn("do not abort it without authorization", skill)

    def test_agent_and_branch_workflow_route_to_one_skill(self):
        target = "contexts/git/skills/resolve-merge-conflicts/SKILL.md"
        self.assertIn(target, source("contexts/git/skills/manage-branch-work/SKILL.md"))
        self.assertIn(target, source("contexts/git/agents/git-engineer.md"))
        self.assertIn("ConflictSkill", source("contexts/git/agents/git-engineer.md"))

    def test_native_without_provider_and_exact_evidence(self):
        skill = source("contexts/git/skills/resolve-merge-conflicts/SKILL.md")
        self.assertIn("without external merge tools", skill)
        self.assertIn("not-run", skill)
        self.assertIn("test-evidence.md", skill)


if __name__ == "__main__":
    unittest.main()

