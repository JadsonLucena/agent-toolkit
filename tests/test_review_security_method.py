"""Structural regression checks for native, adapter-independent security review guidance.

These checks do not measure a model's actual vulnerability detection accuracy.
"""
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AGENT = ROOT / "contexts/review/agents/security-reviewer.md"
REVIEW_SKILL = ROOT / "contexts/review/skills/review-change/SKILL.md"
REFERENCE = ROOT / "contexts/review/skills/review-change/references/security-investigation.md"
SPECIALIST = ROOT / "contracts/review-specialist-evidence.md"
LEAD_EVIDENCE = ROOT / "contracts/review-evidence.md"


class SecurityReviewMethodTests(unittest.TestCase):
    def test_native_reference_is_linked_from_existing_review_flow(self):
        self.assertTrue(REFERENCE.is_file())
        self.assertIn("references/security-investigation.md", REVIEW_SKILL.read_text(encoding="utf-8"))
        self.assertIn("references/security-investigation.md", AGENT.read_text(encoding="utf-8"))

    def test_investigation_includes_counterevidence_and_multiple_causal_models(self):
        agent = AGENT.read_text(encoding="utf-8")
        reference = REFERENCE.read_text(encoding="utf-8")
        for topic in ("attacker", "trust boundary", "counterevidence", "source", "principal", "state"):
            with self.subTest(topic=topic):
                self.assertIn(topic, (agent + reference).lower())
        self.assertIn("No universal vulnerability checklist", agent)
        self.assertIn("not a mandatory checklist", reference)
        self.assertIn("not proof of exploitation", agent)

    def test_security_evidence_is_additive_to_shared_contract(self):
        specialist = SPECIALIST.read_text(encoding="utf-8")
        lead = LEAD_EVIDENCE.read_text(encoding="utf-8")
        self.assertIn("optional `security_context`", specialist)
        self.assertIn("`security_context` — optional", lead)
        self.assertIn("All specialists must confirm the same frozen target", specialist)
        self.assertIn("lead_confirmed", lead)

    def test_external_guidance_is_never_mandatory(self):
        agent = AGENT.read_text(encoding="utf-8")
        reference = REFERENCE.read_text(encoding="utf-8")
        self.assertIn("If the helper is unavailable", agent)
        self.assertIn("additional advisory context only", reference)
        self.assertIn("No individual specialist issues PASS/FAIL", reference)


if __name__ == "__main__":
    unittest.main()
