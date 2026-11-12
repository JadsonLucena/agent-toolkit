"""Policy regressions for optional strategic and domain discovery in elicitation.

Structural tests verify canonical ownership and evaluation coverage, not agent
behavior. Run evals/requirements cases with an actual agent host and reviewed
transcripts before making empirical behavior claims.
"""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RULE = ROOT / "contexts/requirements/rules/requirements.md"
SKILL = ROOT / "contexts/requirements/skills/elicitation/SKILL.md"
CONTRACT = ROOT / "contracts/requirements.md"
CASES = ROOT / "evals/requirements/cases.json"


class StrategicDomainDiscoveryPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rule = RULE.read_text(encoding="utf-8")
        cls.skill = SKILL.read_text(encoding="utf-8")
        cls.contract = CONTRACT.read_text(encoding="utf-8")
        cls.cases = {c["id"]: c for c in json.loads(CASES.read_text(encoding="utf-8"))["cases"]}

    def test_methods_are_conditional_not_a_new_pipeline(self):
        selection = self.skill.split("### Contextual investigation selection", 1)[1].split(
            "### Decision-frontier interview protocol", 1
        )[0]
        for technique in (
            "Impact Mapping", "EventStorming", "Opportunity Solution Tree",
            "CATWOE", "Goal Question Metric (GQM)", "STPA-informed",
            "Cynefin", "Kepner-Tregoe", "No specialized technique"
        ):
            with self.subTest(technique=technique):
                self.assertIn(technique, selection)
        self.assertIn("Select only an approach", selection)
        self.assertIn("no new artifact is required", selection)
        self.assertIn("only when each resolves a distinct material uncertainty", selection)

    def test_existing_frontier_and_authority_constraints_survive(self):
        diagram = self.skill.split("stateDiagram-v2", 1)[1].split("```", 1)[0]
        for edge in ("Discover --> SelectInvestigation",
                     "SelectInvestigation --> Investigate",
                     "ResolveFacts --> SelectQuestionFrontier",
                     "Clarify --> MapDecisionDependencies"):
            self.assertIn(edge, diagram)
        for guardrail in ("not a completed STPA analysis", "cannot manufacture consensus",
                          "not an approved requirement", "do not invent baselines"):
            self.assertIn(guardrail, self.rule)

    def test_no_new_contract_or_false_workshop_assertion(self):
        self.assertIn("events", self.contract.lower())
        self.assertIn("success_metrics", self.contract)
        self.assertIn("candidate_solutions", self.contract)
        self.assertIn("stakeholders", self.contract)
        self.assertIn("do not claim a workshop happened", self.skill)
        self.assertIn("Do not imply that interviews, workshops", self.skill)

    def test_new_evals_cover_each_method_and_anti_ceremony(self):
        for case_id in (f"EL-{n:02d}" for n in range(11, 19)):
            with self.subTest(case_id=case_id):
                case = self.cases[case_id]
                self.assertEqual("/requirements/elicit-requirements", case["command"])
                self.assertEqual({"presence", "absence"}, {c["mode"] for c in case["checks"]})
                self.assertTrue(all(c["criterion"] for c in case["checks"]))
        self.assertIn("no actual EventStorming workshop", self.cases["EL-12"]["input"])
        self.assertIn("no measurements", self.cases["EL-15"]["input"].lower())
        self.assertIn("no material unknowns", self.cases["EL-17"]["input"])


if __name__ == "__main__":
    unittest.main()
