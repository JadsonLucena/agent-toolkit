"""Structural policy regressions for risk-proportionate decision-frontier elicitation.

These checks do not execute an LLM; actual agent behavior requires runtime evals.
"""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "contexts/requirements/skills/elicitation/SKILL.md"


class DecisionFrontierPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.content = SKILL.read_text(encoding="utf-8")
        cls.workflow = cls.content.split("## Workflow", 1)[1].split("## Output", 1)[0]

    def test_decisions_and_facts_precede_frontier_questions(self):
        diagram = self.content.split("```mermaid", 1)[1].split("```", 1)[0]
        self.assertIn("Investigate --> MapDecisionDependencies", diagram)
        self.assertIn("MapDecisionDependencies --> ResolveFacts", diagram)
        self.assertIn("ResolveFacts --> SelectQuestionFrontier", diagram)
        self.assertIn("Clarify --> MapDecisionDependencies", diagram)

    def test_frontier_does_not_batch_dependent_questions(self):
        self.assertIn("Two questions may share a round only if", self.workflow)
        self.assertIn("prerequisite facts and decisions are settled", self.workflow)
        self.assertIn("Prioritize pivots", self.workflow)

    def test_agent_cannot_substitute_business_authority(self):
        self.assertIn("not a fact the agent may infer", self.workflow)
        self.assertIn("wait for authorized confirmation", self.workflow)
        self.assertIn("provenance", self.workflow)

    def test_interview_is_risk_proportionate_and_converges(self):
        self.assertIn("Do not manufacture a full decision tree", self.workflow)
        self.assertIn("Stop on sufficiency", self.workflow)
        self.assertIn("missing critical guarantee", self.workflow)
        self.assertIn("deferred branches", self.workflow)


if __name__ == "__main__":
    unittest.main()
