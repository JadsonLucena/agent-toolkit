"""Output-boundary selection and sensitive disclosure policy structural regressions."""

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def read(path):
    return (ROOT / path).read_text(encoding="utf-8")

class OutputProtectionTests(unittest.TestCase):
    def test_conditional_design_guidance_and_no_mandatory_presenter(self):
        skill = read("contexts/design/skills/design-solution/SKILL.md")
        ref = read("contexts/design/skills/design-solution/references/output-contracts-and-data-protection.md")
        self.assertIn("output contracts and data protection guidance", skill)
        self.assertIn("HTTP is **not** required", ref)
        self.assertIn("not** a universal", ref)
        self.assertIn("Presenter Versus Authorization", ref)
        self.assertIn("cannot grant access", ref)
        self.assertIn("## Classification, Minimization and Protection", ref)

    def test_privacy_policy_across_contexts(self):
        paths = [
            "contexts/requirements/rules/requirements.md",
            "contexts/design/rules/design.md",
            "contexts/implementation/skills/implement-slice/SKILL.md",
            "contexts/testing/rules/testing.md",
            "contexts/review/skills/review-change/references/output-data-protection-review.md",
        ]
        all_text = "\n".join(read(path) for path in paths)
        for expected in ("property-level", "masking", "Presenter", "logs", "authorized"):
            with self.subTest(term=expected):
                self.assertIn(expected.lower(), all_text.lower())

    def test_scenarios_cover_authorized_and_forbidden_disclosure(self):
        catalog = json.loads(read("evals/api/cases.json"))
        new = [c for c in catalog["cases"] if c["id"] in {"API-13", "API-14", "API-15", "API-16"}]
        self.assertEqual(4, len(new))
        for case in new:
            self.assertEqual(3, len(case["checks"]))
            self.assertEqual({"presence", "absence"}, {c["mode"] for c in case["checks"]})

if __name__ == "__main__":
    unittest.main()
