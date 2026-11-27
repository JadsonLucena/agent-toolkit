"""Structural regression fixtures for relational modeling guidance (not agent-behavior proof)."""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from requirements_evals import evaluate, load_catalog  # noqa: E402


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


class RelationalDataGuidanceTests(unittest.TestCase):
    def test_conditional_design_reference_and_existing_handoff(self):
        skill = read("contexts/design/skills/design-solution/SKILL.md")
        guide = read("contexts/design/skills/design-solution/references/relational-data-design.md")
        rule = read("contexts/design/rules/design.md")
        self.assertIn("For a relational schema or derived read-model change", skill)
        self.assertIn("references/relational-data-design.md", skill)
        self.assertIn("Relational Data and Derived Read Models", rule)
        self.assertIn("contracts/design-evidence.md", guide)
        for phrase in (
            "candidate keys", "lossless join", "dependency preservation",
            "3NF", "BCNF", "4NF", "5NF", "REFRESH MATERIALIZED VIEW",
            "CONCURRENTLY", "indexed views", "incremental", "Never mechanically",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase.lower(), guide.lower())
        self.assertIn("not a mandatory normalization ceremony", guide)
        self.assertIn("do not select BCNF universally", guide.lower())
        self.assertNotIn("must use CQRS", guide)

    def test_ownership_and_scope_preservation(self):
        requirements = read("contexts/requirements/rules/requirements.md")
        review = read("contexts/review/rules/code-review.md")
        self.assertIn("business-significant functional dependencies", requirements)
        self.assertIn("without prescribing a physical schema", requirements)
        self.assertIn("When relational schema or derived read-model changes are material", review)
        self.assertIn("Do not enforce a preferred normal form", review)

    def test_catalog_is_valid_and_unobserved_runs_are_incomplete(self):
        catalog = load_catalog(ROOT / "evals/data/cases.json")
        self.assertEqual(10, len(catalog["cases"]))
        self.assertEqual(10, len({c["id"] for c in catalog["cases"]}))
        self.assertTrue(all(len(c["checks"]) == 3 for c in catalog["cases"]))
        self.assertTrue(any("materialized" in c["scenario"].lower() for c in catalog["cases"]))
        self.assertTrue(any("BCNF" in c["scenario"] for c in catalog["cases"]))
        result = evaluate(catalog, {"version": 1, "assessments": []}, ROOT / "evals/data")
        self.assertEqual("INCOMPLETE", result["status"])
        self.assertEqual(10, result["incomplete"])


if __name__ == "__main__":
    unittest.main()
