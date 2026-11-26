"""Static coverage of conditional HTTP API handoffs; host behavior needs real evals."""

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class HttpApiLifecycleTests(unittest.TestCase):
    def test_implementation_consumes_design_not_a_new_policy(self):
        text = (ROOT / "contexts/implementation/skills/implement-slice/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("HTTP API Contract Realization (Conditional)", text)
        self.assertIn("contracts/design-evidence.md", text)
        self.assertIn("existing TDD and verification flow", text)

    def test_testing_uses_behavioral_counterexamples(self):
        text = (ROOT / "contexts/testing/rules/testing.md").read_text(encoding="utf-8")
        self.assertIn("HTTP API Contract Tests (Conditional)", text)
        self.assertIn("equal keys", text)
        self.assertIn("in-memory test cannot establish", text)

    def test_review_uses_one_conditional_reference(self):
        skill = (ROOT / "contexts/review/skills/review-change/SKILL.md").read_text(encoding="utf-8")
        ref = (ROOT / "contexts/review/skills/review-change/references/http-api-review.md").read_text(encoding="utf-8")
        self.assertIn("references/http-api-review.md", skill)
        self.assertIn("not a second review gate", ref)
        self.assertIn("no finding", ref)
        self.assertIn("contracts/review-evidence.md", ref)


if __name__ == "__main__":
    unittest.main()
