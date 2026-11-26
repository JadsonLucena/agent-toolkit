"""Structural fixtures for conditional collection-query selection; not behavioral agent proof."""

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class CollectionQueryGuidanceTests(unittest.TestCase):
    def test_requirement_discovery_does_not_prescribe_a_strategy(self):
        text = (ROOT / "contexts/requirements/rules/requirements.md").read_text(encoding="utf-8")
        self.assertIn("For a collection-access need", text)
        self.assertIn("without prescribing", text)

    def test_design_reference_is_conditional_and_explains_keyset_limits(self):
        skill = (ROOT / "contexts/design/skills/design-solution/SKILL.md").read_text(encoding="utf-8")
        guide = (ROOT / "contexts/design/skills/design-solution/references/collection-query-design.md").read_text(encoding="utf-8")
        self.assertIn("For a collection-query change", skill)
        for term in ("Keyset / seek", "deterministic total order", "snapshot isolation", "AIP-158", "fields", "cursor"):
            self.assertIn(term, guide)


if __name__ == "__main__":
    unittest.main()
