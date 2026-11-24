"""Structural regressions for safe native Implementation authority."""

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


def doc(path):
    return (ROOT / path).read_text(encoding="utf-8")


class ImplementationContextTests(unittest.TestCase):
    def test_command_grants_code_edit_but_not_remote_operations(self):
        command = doc("contexts/implementation/commands/implement-slice.md")
        self.assertIn("production and related test edits", command)
        for forbidden in ("push", "PR creation", "merge", "deployment"):
            self.assertIn(forbidden, command)

    def test_skill_references_owner_and_observed_checks(self):
        skill = doc("contexts/implementation/skills/implement-slice/SKILL.md")
        for required in ("name: implement-slice", "```mermaid", "test-evidence.md", "observed results", "Stop Conditions"):
            self.assertIn(required, skill)

    def test_implementation_does_not_redefine_requirements_or_review(self):
        rule = doc("contexts/implementation/rules/implementation.md")
        self.assertIn("do not invent product policy", rule)
        self.assertIn("Git revert does not reverse external outcomes", rule)
        self.assertIn("Review remains read-only and independently owned", rule)

    def test_composite_pr_plan_precedes_mutation(self):
        skill = doc("contexts/implementation/skills/implement-slice/SKILL.md")
        self.assertLess(skill.index('PlanPR["Git Engineer'), skill.index('Change["Apply minimal'))
        self.assertIn("read-only `plan` mode", skill)
        self.assertIn("PR Boundary", skill)

    def test_commit_handoff_requires_confirmation_before_next_intention(self):
        skill = doc("contexts/implementation/skills/implement-slice/SKILL.md")
        agent = doc("contexts/implementation/agents/implementation-engineer.md")
        self.assertIn('Commit --> CommitVerified', skill)
        self.assertIn('CommitVerified -->|Yes| More', skill)
        self.assertIn('CommitVerified -->|No, failed or unavailable| Block', skill)
        self.assertIn("create-semantic-commits/SKILL.md", skill)
        self.assertIn("observed commit SHA", agent)

    def test_uncommitted_work_does_not_advance_silently(self):
        skill = doc("contexts/implementation/skills/implement-slice/SKILL.md")
        self.assertIn('CommitAuthority -->|Explicitly denied| Uncommitted', skill)
        self.assertIn('CommitAuthority -->|Unknown| Block', skill)
        self.assertIn('Continuation -->|No| DoneUncommitted', skill)
        self.assertIn("explicit safe-continuation authorization", skill)

    def test_commit_authority_inherited_without_repeated_phrase(self):
        command = doc("contexts/implementation/commands/implement-slice.md")
        rule = doc("contexts/implementation/rules/implementation.md")
        skill = doc("contexts/implementation/skills/implement-slice/SKILL.md")
        git_rule = doc("contexts/git/rules/semantic-commit.md")
        self.assertIn("plan need not repeat commit permission", command)
        self.assertIn("plan's silence about commits is not denial", rule)
        self.assertIn("silence about local commits is not a prohibition", git_rule)
        self.assertIn('ScopeGate -->|No or unclear| Block', skill)
        self.assertIn("ResolveCommit --> Strategy", skill)
        self.assertIn('CommitAuthority -->|Explicitly denied| Uncommitted', skill)
        self.assertIn('CommitAuthority -->|Unknown| Block', skill)
        self.assertNotIn('CommitAuthority -->|No| Uncommitted', skill)

    def test_implementation_ends_before_review_and_pr_publication(self):
        skill = doc("contexts/implementation/skills/implement-slice/SKILL.md")
        agent = doc("contexts/implementation/agents/implementation-engineer.md")
        command = doc("contexts/implementation/commands/implement-slice.md")
        self.assertIn("separate Integration stage", skill)
        self.assertIn("do not initiate independent Code Review", skill)
        self.assertIn("do not perform independent review, PR publication or merge", agent)
        self.assertIn("subsequent Integration-stage operations", command)

    def test_context_registered_in_linter_and_matrix(self):
        self.assertIn("| Implementation | `rules/implementation.md` | Rule |", doc("ARCHITECTURE.md"))
        self.assertIn('"Implementation"', doc("scripts/toolkit_lint.py"))


if __name__ == "__main__":
    unittest.main()
