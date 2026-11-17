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
                      "Review owner", "sole technical verdict"):
            self.assertIn(token, skill)
        self.assertIn("Git: prepare ready PR", skill)
        self.assertIn("Git: create PR", skill)
        agent = doc("contexts/delivery/agents/delivery-coordinator.md")
        self.assertIn("not another Code Review verdict", agent)

    def test_recovery_and_result_are_not_fabricated(self):
        rules = doc("contexts/delivery/rules/delivery.md")
        for token in ("Checkpoints cannot undo", "no material progress", "business problem", "source baseline"):
            self.assertIn(token.lower(), rules.lower())

    def test_git_planning_happens_before_implementation(self):
        skill = doc("contexts/delivery/skills/coordinate-delivery/SKILL.md")
        self.assertIn("Need -->|Implementation| Strategy", skill)
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
        self.assertIn('Need -->|New integration after Implementation| Preflight', skill)
        self.assertIn('Checks -->|Yes| Review', skill)
        self.assertIn('ReviewResult -->|PASS, reviewed target| DoneReviewed', skill)
        self.assertIn('ReviewResult -->|PASS, PR progression authorized| PublishRoute', skill)
        self.assertIn('PublishRoute -->|No| ReadyPrepare', skill)
        self.assertIn('ReadyPrepare --> PublishDecision', skill)
        self.assertIn('PublishDecision -->|Create authorized, Git eligibility satisfied| GitCreate', skill)
        self.assertIn('Created --> PostTarget', skill)
        self.assertIn('Need -->|Existing published PR| ExistingPR', skill)
        self.assertIn('ExistingPR --> ExistingFresh', skill)
        self.assertIn('ExistingFresh -->|No, stale or changed| Preflight', skill)
        self.assertIn('PublishRoute -->|Yes| ExistingContinue', skill)
        self.assertIn('ExistingContinue --> PostTarget', skill)
        self.assertIn('PostTarget -->|No, integrated requested| PostChecks', skill)
        self.assertIn('PostGate -->|Yes| MergeAuth', skill)
        self.assertIn('MergeAuth -->|No| Block', skill)
        self.assertIn('MergeAuth -->|Yes| GitMerge', skill)
        self.assertIn('GitMerge --> Confirm', skill)

    def test_review_failure_loops_back_and_draft_is_truthful(self):
        skill = doc("contexts/delivery/skills/coordinate-delivery/SKILL.md")
        rule = doc("contexts/delivery/rules/delivery.md")
        self.assertIn('ReviewResult -->|No, correctable| Fix', skill)
        self.assertIn('ChecksResult -->|No, expressly authorized Draft| DraftRoute', skill)
        self.assertIn('Fix --> Reconcile', skill)
        self.assertIn('ReviewResult -->|No, expressly authorized Draft| DraftRoute', skill)
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

    def test_product_slice_completion_is_distinct_from_pr_merge(self):
        rule = doc("contexts/delivery/rules/delivery.md")
        skill = doc("contexts/delivery/skills/coordinate-delivery/SKILL.md")
        agent = doc("contexts/delivery/agents/delivery-coordinator.md")
        for token in ("integrated target revision", "cross-PR", "Product Slice still incomplete"):
            self.assertIn(token.lower(), rule.lower())
        self.assertIn('Confirm -->|Verified| SliceNeeded', skill)
        self.assertIn('SliceNeeded -->|Yes| SliceReconcile', skill)
        self.assertIn('SliceNeeded -->|No, PR integration only| Done', skill)
        self.assertIn('SliceComplete -->|No, pending or unverified| SlicePending', skill)
        self.assertIn("PR integration status", skill)
        self.assertIn("Product Slice technical verification status", skill)
        self.assertIn("a merged pr", agent.lower())

    def test_existing_pr_must_not_flow_to_duplicate_creation(self):
        skill = doc("contexts/delivery/skills/coordinate-delivery/SKILL.md")
        self.assertIn('ExistingFresh -->|Yes| PostTarget', skill)
        self.assertIn('PublishRoute -->|Yes| ExistingContinue', skill)
        self.assertIn('ExistingContinue --> PostTarget', skill)
        self.assertIn('DraftRoute -->|Yes| ExistingPending', skill)
        self.assertIn('DraftRoute -->|No| DraftPrepare', skill)
        self.assertIn('ExistingPending --> Block', skill)
        self.assertIn('never create duplicate or auto-promote Draft', skill)
        self.assertIn('resume the existing PR', skill)
        self.assertNotIn('ExistingPR --> GitCreate', skill)

    def test_stage_order_and_explicit_authorization_edges(self):
        skill = doc("contexts/delivery/skills/coordinate-delivery/SKILL.md")
        self.assertIn('Auth --> Need', skill)
        self.assertIn('Need -->|Requirements| Requirements', skill)
        self.assertIn('Need -->|Design| Design', skill)
        self.assertIn('Need -->|Implementation| Strategy', skill)
        self.assertNotIn('Auth --> Strategy', skill)
        self.assertIn('PublishDecision -->|Prepare only or creation not authorized| Prepared', skill)
        self.assertIn('PostGate -->|Yes| MergeAuth', skill)
        self.assertIn('MergeAuth -->|No| Block', skill)
        self.assertIn('SliceNeeded -->|No, PR integration only| Done', skill)
        self.assertIn('optional TDD', skill)
        self.assertIn('atomic Git commit handoffs', skill)

    def test_slice_context_selection_is_selective_but_preserves_guarantees(self):
        rule = doc("contexts/delivery/rules/delivery.md")
        skill = doc("contexts/delivery/skills/coordinate-delivery/SKILL.md")
        agent = doc("contexts/delivery/agents/delivery-coordinator.md")
        for token in ("Slice-Scoped Context Integrity", "progressive, authorized retrieval",
                      "critical source is missing", "Invalidate only affected"):
            self.assertIn(token.lower(), rule.lower())
        for token in ("Slice-Scoped Context Handoffs", "context_id", "change_boundary_ref",
                      "scenario_refs", "source_baseline_ref", "on demand",
                      "referenced, actually retrieved, and verified"):
            self.assertIn(token.lower(), skill.lower())
        self.assertIn("Do not drop critical guarantees", agent)
        self.assertIn("does **not** define a new context-packet contract", skill)

    def test_context_registered(self):
        self.assertIn("| Delivery | `rules/delivery.md` | Rule |", doc("ARCHITECTURE.md"))
        self.assertIn('"Delivery"', doc("scripts/toolkit_lint.py"))


if __name__ == "__main__":
    unittest.main()
