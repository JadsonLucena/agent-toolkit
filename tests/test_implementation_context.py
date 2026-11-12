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

    def test_context_registered_in_linter_and_matrix(self):
        self.assertIn("| Implementation | `rules/implementation.md` | Rule |", doc("ARCHITECTURE.md"))
        self.assertIn('"Implementation"', doc("scripts/toolkit_lint.py"))


if __name__ == "__main__":
    unittest.main()
