"""Regression checks for documentation consistency review policy wiring.

These tests verify that the portable review instructions include the
documentation lens and expose it in normal execution/reporting. They do not
claim to execute an LLM reviewer or to prove documentation correctness.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

RULE = "contexts/review/rules/code-review.md"
WORKFLOW = "contexts/review/skills/review-change/skill.md"
LEAD = "contexts/review/agents/code-reviewer.md"
SPEC = "contexts/review/agents/specification-reviewer.md"
ARCH = "contexts/review/agents/architecture-reviewer.md"
REPORT = "contexts/review/templates/human-review-report.md"
CONTRACT = "contracts/review-evidence.md"


def source(path):
    return (ROOT / path).read_text(encoding="utf-8")


class DocumentationReviewPolicyTests(unittest.TestCase):
    def test_single_policy_covers_all_drift_cases(self):
        rule = source(RULE)
        self.assertEqual(1, rule.count("## Documentation Consistency and Drift"))
        policy = rule.split("## Documentation Consistency and Drift", 1)[1].split("\n## ", 1)[0]
        for term in ("missing", "outdated", "contradictory", "ambiguous", "duplicated",
                     "not-applicable", "consequence", "actual", "heuristic"):
            with self.subTest(term=term):
                self.assertIn(term, policy.lower())
        self.assertIn("unchanged documentation", policy.lower())

    def test_workflow_and_lead_require_documentation_assessment(self):
        for path in (WORKFLOW, LEAD):
            with self.subTest(path=path):
                text = source(path).lower()
                self.assertIn("documentation consistency", text)
                self.assertIn("contexts/review/rules/code-review.md", text)
        self.assertIn("documentation_assessment", source(CONTRACT))
        self.assertIn("## Documentation assessment", source(REPORT))

    def test_specialists_reference_policy_without_copying_heuristics(self):
        for path in (SPEC, ARCH):
            with self.subTest(path=path):
                text = source(path).lower()
                self.assertIn("documentation consistency", text)
                self.assertIn("contexts/review/rules/code-review.md", text)
                self.assertNotIn("## Documentation Consistency and Drift", text)

    def test_documentation_review_is_not_a_separate_agent_or_hard_gate(self):
        rule = source(RULE)
        self.assertIn("not automatic blockers", rule.lower())
        self.assertIn("documentation_assessment", source(CONTRACT))
        self.assertIn("review_profile", source(CONTRACT))


if __name__ == "__main__":
    unittest.main()
