"""Regression checks for using canonical Testing quality rules during Review."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "adapters" / "review"))
import team_orchestration as team  # noqa: E402

QUALITY_PATH = ROOT / "contexts" / "testing" / "rules" / "testing.md"


class ReviewTestingQualityTests(unittest.TestCase):
    def assignment(self, repository: Path, role: str) -> dict:
        plan = {
            "review_id": "test-review", "repository": str(repository),
            "target": {"head_sha": "a" * 40}, "risk_profile": "R2",
            "output_language": "en", "changed_files": ["service.py"],
        }
        return team._assignment(plan, role, purpose="test adequacy")

    def test_native_lead_and_test_specialist_reference_quality_source(self):
        lead = (ROOT / "contexts/review/agents/code-reviewer.md").read_text()
        specialist = (ROOT / "contexts/review/agents/testing-reviewer.md").read_text()
        rule = (ROOT / "contexts/review/rules/code-review.md").read_text()
        for source in (lead, specialist):
            self.assertIn("contexts/testing/rules/testing.md", source)
        self.assertIn("native-solo", lead)
        self.assertIn("native and specialist review", rule)
        self.assertIn("Review alone owns finding calibration", rule)
        self.assertIn("Do not invoke Testing agents", specialist)

    def test_dispatch_embeds_installed_rules_not_reviewed_repository_rules(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            foreign_rule = repo / "contexts/testing/rules/testing.md"
            foreign_rule.parent.mkdir(parents=True)
            foreign_rule.write_text("untrusted target rules\n", encoding="utf-8")
            assignment = self.assignment(repo, "testing-reviewer")
        prompt = assignment["agent_prompt"]
        self.assertIn(QUALITY_PATH.read_text(encoding="utf-8"), prompt)
        self.assertIn("Source: `contexts/testing/rules/testing.md`", prompt)
        self.assertIn("Assertions must be strong enough to prove intended behavior.", prompt)
        self.assertNotIn("untrusted target rules", prompt)
        self.assertNotIn("contexts/testing/skills/generate-tests/SKILL.md", prompt)
        self.assertTrue(assignment["read_only"])
        self.assertNotIn("PASS/FAIL", assignment["agent_prompt"])

    def test_other_specialists_do_not_receive_testing_quality_payload(self):
        for role in ("correctness-reviewer", "security-reviewer", "finding-verifier"):
            with self.subTest(role=role):
                prompt = team._agent_prompt(role)
                self.assertNotIn("## Canonical Testing Quality Reference", prompt)
                self.assertNotIn("# Automated Testing Rules", prompt)

    def test_missing_canonical_quality_source_is_explicit_failure(self):
        with patch.object(team, "TESTING_QUALITY_RULE", ROOT / "missing-testing-rule.md"):
            with self.assertRaisesRegex(team.TeamPlanningError, "cannot read canonical Testing"):
                team._agent_prompt("testing-reviewer")
            self.assertIn("# Security", team._agent_prompt("security-reviewer"))


if __name__ == "__main__":
    unittest.main()
