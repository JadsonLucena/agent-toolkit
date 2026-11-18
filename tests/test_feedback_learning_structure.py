"""Structural guardrails for optional Feedback & Learning routing.

These tests validate canonical source declarations, not live agent behavior.
"""

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


class FeedbackLearningStructureTests(unittest.TestCase):
    def test_skill_has_one_owner_and_is_discoverable(self):
        skill = read("contexts/delivery/skills/assess-feedback/SKILL.md")
        self.assertTrue(skill.startswith("---\nname: assess-feedback\n"))
        self.assertIn("## Workflow", skill)
        self.assertIn("## Boundary", skill)
        self.assertIn("## Stop Conditions", skill)
        self.assertIn("| Delivery | `skills/assess-feedback/SKILL.md` | Skill |", read("ARCHITECTURE.md"))
        self.assertIn("contexts/delivery/skills/assess-feedback/SKILL.md", read("contexts/delivery/agents/delivery-coordinator.md"))
        self.assertIn("contexts/delivery/skills/assess-feedback/SKILL.md", read("contexts/delivery/skills/coordinate-delivery/SKILL.md"))

    def test_feedback_workflow_has_a_real_state_model(self):
        skill = read("contexts/delivery/skills/assess-feedback/SKILL.md")
        state = skill.split("## State Model", 1)[1].split("## Working State", 1)[0]
        workflow = skill.split("## Workflow", 1)[1].split("## Output", 1)[0]
        self.assertEqual(state.count("```mermaid"), 1)
        self.assertIn("stateDiagram-v2", state)
        self.assertIn("Follow the State Model", workflow)
        for transition in (
            "Capture --> Assess",
            "Assess --> Reflect",
            "Reflect --> DecideAndRoute",
            "DecideAndRoute --> ValidateLearning",
            "DecideAndRoute --> Pending",
            "ValidateLearning --> Complete",
            "ValidateLearning --> Pending",
        ):
            with self.subTest(transition=transition):
                self.assertIn(transition, state)

    def test_read_only_feedback_does_not_create_delivery_stage_or_permission(self):
        command = read("contexts/delivery/commands/deliver-change.md")
        rule = read("contexts/delivery/rules/delivery.md")
        skill = read("contexts/delivery/skills/assess-feedback/SKILL.md")
        self.assertIn("without a delivery target", command)
        self.assertIn("routes only the read-only", command)
        self.assertIn("no normative authority", rule)
        self.assertIn("No self-approved rule edits", skill)
        self.assertIn("separately applicable authorization", rule)
        self.assertIn("not a mandatory stage", read("contexts/delivery/skills/coordinate-delivery/SKILL.md"))

    def test_learning_requires_real_followup_and_keeps_outcome_owner(self):
        skill = read("contexts/delivery/skills/assess-feedback/SKILL.md")
        rule = read("contexts/delivery/rules/delivery.md")
        for phrase in ("single-loop", "double-loop", "counterexamples", "corroborated", "refuted", "inconclusive", "pending"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, skill)
        self.assertIn("contracts/outcome-evidence.md", skill)
        self.assertIn("A change without follow-up evidence", rule)
        self.assertIn("no duplicate contract", rule)
        self.assertIn("Do not invent", read("contracts/outcome-evidence.md"))


if __name__ == "__main__":
    unittest.main()
