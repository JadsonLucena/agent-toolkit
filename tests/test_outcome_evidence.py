"""Outcome handoff must not claim deployment or business efficacy."""

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


def doc(path):
    return (ROOT / path).read_text(encoding="utf-8")


class OutcomeEvidenceTests(unittest.TestCase):
    def test_never_equates_pr_or_review_with_observed_outcome(self):
        contract = doc("contracts/outcome-evidence.md")
        for token in ("deployment_status", "observation_status", "pending",
                      "inconclusive", "causal attribution", "Review PASS"):
            self.assertIn(token, contract)

    def test_no_outcome_runtime_or_unauthorized_action(self):
        contract = doc("contracts/outcome-evidence.md")
        self.assertIn("does not authorize production access", contract)
        self.assertIn("Proposed actions do not authorize execution", contract)
        self.assertIn("not a deployment workflow", contract)

    def test_delivery_consumes_portable_handoff(self):
        self.assertIn("contracts/outcome-evidence.md", doc("contexts/delivery/rules/delivery.md"))
        self.assertIn("contracts/outcome-evidence.md", doc("contexts/delivery/commands/deliver-change.md"))
        self.assertIn("| Cross-context | `contracts/outcome-evidence.md` | Contract |", doc("ARCHITECTURE.md"))


if __name__ == "__main__":
    unittest.main()
