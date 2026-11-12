"""Structural guardrails for explicit cross-context SDD coordination."""

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def doc(path):
    return (ROOT / path).read_text(encoding="utf-8")


class DeliveryContextTests(unittest.TestCase):
    def test_default_read_only_and_stages_are_explicit(self):
        command = doc("contexts/delivery/commands/deliver-change.md")
        for token in ("target_stage", "read-only", "No implicit", "PR publication", "authorization"):
            self.assertIn(token.lower(), command.lower())

    def test_composes_specialists_without_second_review_verdict(self):
        skill = doc("contexts/delivery/skills/coordinate-delivery/SKILL.md")
        for token in ("Requirements owner", "Design owner", "Implementation owner",
                      "Review owner", "Git owner", "sole technical verdict"):
            self.assertIn(token, skill)
        agent = doc("contexts/delivery/agents/delivery-coordinator.md")
        self.assertIn("not another Code Review verdict", agent)

    def test_recovery_and_result_are_not_fabricated(self):
        rules = doc("contexts/delivery/rules/delivery.md")
        for token in ("Checkpoints cannot undo", "no material progress", "business problem", "source baseline"):
            self.assertIn(token.lower(), rules.lower())

    def test_context_registered(self):
        self.assertIn("| Delivery | `rules/delivery.md` | Rule |", doc("ARCHITECTURE.md"))
        self.assertIn('"Delivery"', doc("scripts/toolkit_lint.py"))


if __name__ == "__main__":
    unittest.main()
