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

    def test_git_planning_happens_before_implementation(self):
        skill = doc("contexts/delivery/skills/coordinate-delivery/SKILL.md")
        self.assertIn("Auth --> Strategy", skill)
        self.assertIn("GitPlan --> PlanReady", skill)
        self.assertIn("PlanReady -->|No| Block", skill)
        self.assertIn("PR Boundary", skill)
        self.assertIn("read-only `plan`", skill)

    def test_commit_result_and_remote_actions_are_separate(self):
        skill = doc("contexts/delivery/skills/coordinate-delivery/SKILL.md")
        rule = doc("contexts/delivery/rules/delivery.md")
        self.assertIn("missing required commit or unproductive", skill)
        self.assertIn("actual verified commit SHA or explicit blocked/uncommitted state", skill)
        self.assertIn("create-semantic-commits/SKILL.md", rule)
        self.assertIn("separate authorization", rule)

    def test_integration_orders_checks_review_pr_and_merge(self):
        skill = doc("contexts/delivery/skills/coordinate-delivery/SKILL.md")
        self.assertIn('Need -->|Integration after Implementation| Preflight', skill)
        self.assertIn('Checks -->|Yes| Review', skill)
        self.assertIn('ReviewResult -->|PASS, reviewed stage reached| DoneReviewed', skill)
        self.assertIn('ReviewResult -->|PASS, PR stage authorized| ReadyPrepare', skill)
        self.assertIn('ReadyPrepare --> PublishDecision', skill)
        self.assertIn('PublishDecision -->|Ready and separately authorized creation, or explicitly authorized draft| GitCreate', skill)
        self.assertIn('Created --> PostTarget', skill)
        self.assertIn('Need -->|Existing published PR requires integration| PostTarget', skill)
        self.assertIn('PostTarget -->|No, integration requested| PostChecks', skill)
        self.assertIn('PostGate -->|Yes and explicit merge authorization| GitMerge', skill)
        self.assertIn('GitMerge --> Confirm', skill)

    def test_review_failure_loops_back_and_draft_is_truthful(self):
        skill = doc("contexts/delivery/skills/coordinate-delivery/SKILL.md")
        rule = doc("contexts/delivery/rules/delivery.md")
        self.assertIn('ReviewResult -->|No, correctable| Fix', skill)
        self.assertIn('ChecksResult -->|No, explicit draft intent| DraftPrepare', skill)
        self.assertIn('Fix --> Reconcile', skill)
        self.assertIn('ReviewResult -->|No, explicitly authorized draft| DraftPrepare', skill)
        self.assertIn('ReviewResult -->|No, cannot proceed| Block', skill)
        self.assertIn("review_profile=advisory", rule)
        self.assertIn("PASS", rule)
        self.assertIn("explicitly authorized Draft PR", rule)

    def test_pr_state_and_authority_are_not_conflated(self):
        command = doc("contexts/delivery/commands/deliver-change.md")
        skill = doc("contexts/delivery/skills/coordinate-delivery/SKILL.md")
        for marker in ("pr-prepared", "pr-created", "integrated"):
            self.assertIn(marker, command)
            self.assertIn(marker, skill)
        self.assertIn("explicit PR-creation authority", command)
        self.assertIn("merge authority", command)
        self.assertIn("separately authorized Git integration", skill)

    def test_context_registered(self):
        self.assertIn("| Delivery | `rules/delivery.md` | Rule |", doc("ARCHITECTURE.md"))
        self.assertIn('"Delivery"', doc("scripts/toolkit_lint.py"))


if __name__ == "__main__":
    unittest.main()
