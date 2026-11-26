"""Policy wiring for evidence-based structural work across requirements and design.

These are static regression checks, not host behavioral evaluation evidence.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


class RefactoringDiscoveryDesignTests(unittest.TestCase):
    def test_technical_debt_can_be_planned_without_invented_user_value(self):
        req = read("contexts/requirements/rules/requirements.md")
        backlog = read("contexts/requirements/rules/backlog.md")
        self.assertIn("## Structural Engineering Needs and Semantic Preservation", req)
        self.assertIn("not automatically as a new user feature", req)
        self.assertIn("## Structural and Enabling Work", backlog)
        self.assertIn("Do not invent a user-facing feature", backlog)

    def test_requirements_quality_review_remains_read_only(self):
        skill = read("contexts/requirements/skills/requirements-validation/SKILL.md")
        self.assertIn("an engineering observation, not automatically a requirements-quality defect", skill)
        self.assertIn("Validation is read-only", skill)
        self.assertIn("not authorization to change acceptance semantics", skill)

    def test_design_strategy_selection_is_conditional(self):
        design = read("contexts/design/rules/design.md")
        skill = read("contexts/design/skills/design-solution/SKILL.md")
        self.assertIn("## Refactoring Strategy Selection", design)
        self.assertIn("information leakage", design)
        self.assertIn("do not confer mutation or requirements authority", design)
        self.assertIn("references/refactoring-options.md", skill)

    def test_reference_preserves_modernization_risk(self):
        ref = read("contexts/design/skills/design-solution/references/refactoring-options.md")
        for expected in ("Branch by Abstraction", "Parallel Change",
                         "Strangler Fig", "irreversible effects",
                         "design-evidence contract"):
            with self.subTest(expected=expected):
                self.assertIn(expected, ref)


if __name__ == "__main__":
    unittest.main()
