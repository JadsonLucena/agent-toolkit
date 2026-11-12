"""Structural policy checks for the optional TDD inner loop."""

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


class TddPolicyTests(unittest.TestCase):
    def test_red_green_refactor_and_stop_conditions(self):
        rule = read("contexts/implementation/rules/implementation.md")
        skill = read("contexts/implementation/skills/test-driven-development/SKILL.md")
        for token in ("expected behavioral reason", "GREEN:", "REFACTOR:", "not a prerequisite"):
            self.assertIn(token, rule)
        for token in ("name: test-driven-development", "## Workflow", "## Stop Conditions",
                      "Record phase results", "RED", "GREEN", "REFACTOR"):
            self.assertIn(token, skill)

    def test_tdd_remains_implementation_owned(self):
        self.assertIn("| Implementation | `skills/test-driven-development/SKILL.md` | Skill |", read("ARCHITECTURE.md"))
        self.assertIn("test-driven-development/SKILL.md", read("contexts/implementation/agents/implementation-engineer.md"))
        self.assertIn("test-driven-development/SKILL.md", read("contexts/implementation/skills/implement-slice/SKILL.md"))
        self.assertIn("does not authorize unrelated production refactoring", read("contexts/testing/commands/generate-tests.md"))


if __name__ == "__main__":
    unittest.main()
