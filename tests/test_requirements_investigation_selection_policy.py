"""Structural regressions for conditional Requirements investigation techniques.

These tests check policy wiring, not agent reasoning. Behavioral results require
independent transcript review using evals/requirements/cases.json.
"""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RULE = ROOT / "contexts/requirements/rules/requirements.md"
TAILORING = ROOT / "contexts/requirements/rules/tailoring.md"
ELICITATION = ROOT / "contexts/requirements/skills/elicitation/SKILL.md"
AGENT = ROOT / "contexts/requirements/agents/requirements-elicitor.md"
CASES = ROOT / "evals/requirements/cases.json"


class InvestigationSelectionPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rule = RULE.read_text(encoding="utf-8")
        cls.tailoring = TAILORING.read_text(encoding="utf-8")
        cls.skill = ELICITATION.read_text(encoding="utf-8")
        cls.agent = AGENT.read_text(encoding="utf-8")

    def test_selection_precedes_investigation_and_preserves_question_frontier(self):
        diagram = self.skill.split("stateDiagram-v2", 1)[1].split("```", 1)[0]
        self.assertIn("Discover --> SelectInvestigation", diagram)
        self.assertIn("SelectInvestigation --> Investigate", diagram)
        self.assertIn("Investigate --> MapDecisionDependencies", diagram)
        self.assertIn("ResolveFacts --> SelectQuestionFrontier", diagram)

    def test_techniques_are_conditional_and_non_authorizing(self):
        selection = self.skill.split("### Contextual investigation selection", 1)[1].split("### Decision-frontier", 1)[0]
        for term in ("Fishbone", "five whys", "First principles", "MECE", "Decision matrix",
                     "cost-benefit", "Pre-mortem", "Hypothesis testing", "No specialized technique"):
            with self.subTest(term=term):
                self.assertIn(term, selection)
        self.assertIn("not a checklist", selection)
        self.assertIn("does not authorize execution", selection)
        self.assertIn("Fishbone (Ishikawa) or five whys", selection)
        self.assertIn("Decision matrix or cost-benefit reasoning", selection)
        self.assertIn("using no named technique is a valid default", self.tailoring)
        self.assertIn("conditional techniques", self.agent)

    def test_provenance_and_causal_guardrails_are_rules_not_method_claims(self):
        rule = self.rule.split("## Problem Investigation and Decision Evidence", 1)[1].split(
            "## Change Boundary and Scope Drift", 1
        )[0]
        for guardrail in ("does not prove causation", "disconfirming evidence",
                          "do not fabricate numeric scores", "proposed experiment",
                          "critical guarantees", "stakeholder decision"):
            with self.subTest(guardrail=guardrail):
                self.assertIn(guardrail, rule)

    def test_evals_cover_selection_as_well_as_no_selection(self):
        entries = json.loads(CASES.read_text(encoding="utf-8"))["cases"]
        scenarios = {case["id"]: case for case in entries}
        self.assertTrue({f"EL-{i:02d}" for i in range(5, 11)}.issubset(scenarios))
        for i in range(5, 11):
            case = scenarios[f"EL-{i:02d}"]
            self.assertEqual(case["command"], "/requirements/elicit-requirements")
            self.assertTrue(any(check["mode"] == "presence" for check in case["checks"]))
            self.assertTrue(any(check["mode"] == "absence" for check in case["checks"]))


if __name__ == "__main__":
    unittest.main()
