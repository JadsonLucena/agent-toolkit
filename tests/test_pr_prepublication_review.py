"""Structural tests for the universal pre-publication PR quality gate.

A real Code Review and completed checks are separate host observations;
these tests cannot establish that a model executed them.
"""

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


class PrPrepublicationReviewTests(unittest.TestCase):
    def test_git_policy_requires_tests_and_review_before_any_remote_pr(self):
        rule = read("contexts/git/rules/pull-request.md")
        gate = rule.split("## Pre-Creation Quality Gate", 1)[1].split("## Template Precedence", 1)[0]
        for expected in (
            "Before creating any remote pull request, including a Draft",
            "passing applicable project tests and lint",
            "review_status=PASS",
            "complete coverage",
            "exact intended head/base",
            "Missing, failed, incomplete, stale or uncorroborated evidence blocks remote creation",
            "Do not publish a Draft to bypass",
            "same explicit PR-creation request authorizes initiating",
            "read-only `/review/review-code`",
            "Local preparation is allowed without this floor",
        ):
            with self.subTest(expected=expected):
                self.assertIn(expected, gate)
        self.assertIn("not required for ready", gate)  # signed gate != advisory requirement

    def test_git_create_routes_review_and_has_no_draft_bypass(self):
        command = read("contexts/git/commands/create-pull-request.md")
        skill = read("contexts/git/skills/manage-pull-request/SKILL.md")
        workflow = skill.split("```mermaid", 1)[1].split("```", 1)[0]
        self.assertIn("Before creating either a ready PR or a Draft", command)
        self.assertIn("without a second authorization", command)
        self.assertIn('Verify --> ReviewCheck', workflow)
        self.assertIn('ReviewCheck -->|Missing or stale| RequestReview', workflow)
        self.assertIn('ReviewCheck -->|FAIL or unresolved INCOMPLETE| ReviewGap', workflow)
        self.assertIn('/review/review-code advisory', workflow)
        self.assertIn('RequestReview --> ReviewResult', workflow)
        self.assertIn('ReviewResult -->|No or unavailable| ReviewGap', workflow)
        self.assertIn('ReviewGap -->|create| Blocked', workflow)
        self.assertIn('ExistingPR -->|none| InspectDiff', workflow)
        self.assertNotIn('ExistingPR -->|none| Gate', workflow)
        self.assertIn('Gate -->|create: passed pre-publication checks and Review;', workflow)

    def test_delivery_and_git_checks_protect_draft_publication(self):
        git_rule = read("contexts/git/rules/git.md")
        delivery_rule = read("contexts/delivery/rules/delivery.md")
        delivery_skill = read("contexts/delivery/skills/coordinate-delivery/SKILL.md")
        self.assertIn("including Draft", git_rule)
        self.assertIn("remote Draft PR", delivery_rule)
        self.assertIn("same mandatory pre-publication tests/lint and Code Review", delivery_rule)
        self.assertIn("no remote PR (including Draft)", delivery_skill)

    def test_optional_adapter_no_longer_publishes_unsigned_drafts(self):
        adapter = read("adapters/github/guarded_pr.py")
        self.assertNotIn("def guard_unsigned_draft(", adapter)
        self.assertIn("all PRs including Draft require --evidence and --signature", adapter)
        self.assertIn("info = guard(args.repo", adapter)
        self.assertIn("verify_signature(evidence_path", adapter)

    def test_ci_runs_on_branch_push_before_pr_creation(self):
        workflow = read(".github/workflows/toolkit-validation.yml")
        event_block = workflow.split("on:", 1)[1].split("permissions:", 1)[0]
        self.assertIn("pull_request:", event_block)
        self.assertIn("push:", event_block)
        self.assertNotIn("branches: [main]", event_block)


if __name__ == "__main__":
    unittest.main()
