"""Guard native and specialist correctness investigation ownership."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


class CorrectnessReviewPolicyTests(unittest.TestCase):
    def test_specialist_uses_contract_to_counterexample_method(self):
        agent = read("contexts/review/agents/correctness-reviewer.md")
        self.assertIn("Establish the applicable behavioral obligation", agent)
        self.assertIn("Attempt to falsify", agent)
        self.assertIn("expected-versus-observed", agent)
        self.assertIn("never invent requirements", agent)
        self.assertIn("review-specialist-evidence.md", agent)

    def test_native_lead_has_same_conditional_investigation_reference(self):
        path = "contexts/review/skills/review-change/references/correctness-review.md"
        self.assertTrue((ROOT / path).is_file())
        self.assertIn(path, read("contexts/review/agents/code-reviewer.md"))
        self.assertIn(path, read("contexts/review/agents/correctness-reviewer.md"))
        self.assertIn("references/correctness-review.md", read("contexts/review/skills/review-change/SKILL.md"))
        self.assertIn("native-solo", read("contexts/review/agents/code-reviewer.md"))

    def test_reference_selects_probes_without_automatic_findings(self):
        ref = read("contexts/review/skills/review-change/references/correctness-review.md")
        for phrase in ("Boundary and cardinality", "Boolean decisions", "Null, absent",
                       "Numeric correctness", "State and sequence", "Time and intervals",
                       "Behavioral preservation", "Seek disconfirmation"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, ref)
        self.assertIn("Not a defect", ref)
        self.assertIn("not an invented business rule", ref)
        self.assertIn("Neither is a second gate", ref)

    def test_specialist_does_not_claim_lead_verdict_or_mutating_authority(self):
        agent = read("contexts/review/agents/correctness-reviewer.md")
        self.assertIn("Do not declare a review `PASS`", agent)
        self.assertIn("Read-only; no implementation edits", agent)
        self.assertIn("Do not require the presence of Agent Teams", agent)


if __name__ == "__main__":
    unittest.main()
