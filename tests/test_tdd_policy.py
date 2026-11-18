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

    def test_red_uses_testing_quality_without_reimplementing_testing(self):
        skill = read("contexts/implementation/skills/test-driven-development/SKILL.md")
        uses = skill.split("## Uses", 1)[1].split("## Working State", 1)[0]
        self.assertNotIn("contexts/testing/", uses)  # cross-context quality guidance is not a Skill dependency
        self.assertIn("contexts/testing/rules/testing.md", skill)
        self.assertIn("canonical test-quality reference", skill)
        self.assertIn("observable assertions", skill)
        self.assertIn("test isolation", skill)
        self.assertIn("scenario traceability", skill)
        self.assertIn("without copying its procedure", skill)
        self.assertIn("Standards --> NeedHelp", skill)
        self.assertIn("NeedHelp -->|No| Red", skill)

    def test_optional_test_authoring_handoff_respects_red(self):
        skill = read("contexts/implementation/skills/test-driven-development/SKILL.md")
        self.assertIn("contexts/testing/skills/generate-tests/SKILL.md", skill)
        self.assertIn("NeedHelp -->|Yes| Delegate", skill)
        self.assertIn("Delegate --> Red", skill)
        self.assertIn("test-artifact design/authoring only", skill)
        self.assertIn("observed failure for the expected behavioral reason", skill)
        self.assertIn("standalone Testing workflow may report incomplete/failing verification", skill)
        self.assertIn("Testing does not own GREEN, REFACTOR", skill)
        self.assertIn("follow the native rule-driven path", skill)
        self.assertIn("only authorized test files", skill)

    def test_tdd_remains_implementation_owned(self):
        self.assertIn("| Implementation | `skills/test-driven-development/SKILL.md` | Skill |", read("ARCHITECTURE.md"))
        self.assertIn("test-driven-development/SKILL.md", read("contexts/implementation/agents/implementation-engineer.md"))
        self.assertIn("test-driven-development/SKILL.md", read("contexts/implementation/skills/implement-slice/SKILL.md"))
        self.assertIn("does not authorize unrelated production refactoring", read("contexts/testing/commands/generate-tests.md"))


if __name__ == "__main__":
    unittest.main()
