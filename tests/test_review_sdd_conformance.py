"""SDD conformance belongs to the existing review verdict."""

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def doc(path):
    return (ROOT / path).read_text(encoding="utf-8")


class SddConformanceTests(unittest.TestCase):
    def test_rule_preserves_authority_and_unverified_evidence(self):
        policy = doc("contexts/review/rules/code-review.md").split("## Specification-Driven Conformance", 1)[1].split("## Documentation Consistency", 1)[0]
        for required in ("authoritative baseline", "unverified", "Change Boundary",
                         "decision-needed", "Code Review Lead", "single review"):
            self.assertIn(required, policy)

    def test_one_review_workflow_and_verdict(self):
        skill = doc("contexts/review/skills/review-change/SKILL.md")
        lead = doc("contexts/review/agents/code-reviewer.md")
        self.assertIn("Conformance --> VerifyFindings", skill)
        self.assertIn("one `PASS`, `FAIL`, or `INCOMPLETE`", lead)
        self.assertIn("Specification-Driven Conformance", doc("contexts/review/agents/specification-reviewer.md"))

    def test_optional_contract_does_not_replace_test_or_gate(self):
        contract = doc("contracts/review-evidence.md")
        record = contract.split("## Optional Specification Conformance Evidence", 1)[1].split("## Findings", 1)[0]
        for token in ("source_baseline_ref", "test_evidence_refs", "not-applicable", "supplements", "Git preflight"):
            self.assertIn(token, record)


if __name__ == "__main__":
    unittest.main()
