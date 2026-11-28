"""Specification obligation evidence stays source-grounded and reaches the Lead."""
import asyncio
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "adapters" / "review"))
from team_orchestration import (  # noqa: E402
    TeamPlanningError, _validate_first_pass, execute,
)


class SpecificationHandoffTests(unittest.TestCase):
    @staticmethod
    def plan(role="specification-reviewer"):
        return {
            "review_id": "r1", "repository": str(ROOT),
            "target": {"head_sha": "a" * 40},
            "scope": {"base_ref": "base", "head_ref": "head"},
            "changed_files": ["src/service.py"], "risk_profile": "R1",
            "review_profile": "advisory", "selected_roles": [role],
            "role_assignments": {role: {"reason": "behavioral obligation"}},
            "omitted_roles": {}, "n_justification": {},
            "execution_mode": "team-relayed", "lead_implemented_change": False,
            "verifier_required": False, "output_language": "pt-BR",
            "capabilities": {"direct_peer_supported": False, "isolated_tasks": True},
        }

    @staticmethod
    def response(plan):
        return {
            "review_id": plan["review_id"], "repository": plan["repository"],
            "target": plan["target"], "verified_head_sha": plan["target"]["head_sha"],
            "role": plan["selected_roles"][0], "task_id": "isolated-1",
            "reviewed_files": ["src/service.py"], "candidate_findings": [],
            "uncertainties": [], "relay_requests": [],
            "assessed_obligations": [{
                "source_ref": "rules.md#R1", "source_baseline_ref": "spec-v2",
                "expected_behavior": "Refunds within 365 days are bounded",
                "implementation_refs": ["src/service.py:10"],
                "assessment": "satisfied", "evidence_refs": ["src/service.py:10"],
                "counterevidence_refs": [], "limitations": [],
            }],
        }

    def test_finding_free_obligations_reach_lead(self):
        plan = self.plan()
        reply = self.response(plan)

        class Host:
            async def task_batch(self, requests):
                return [reply]

        result = asyncio.run(execute(plan, Host()))
        self.assertEqual([], result["raw_findings"])
        self.assertEqual("specification-reviewer", result["specialist_obligations"][0]["role"])
        self.assertEqual([reply["assessed_obligations"][0]],
                         result["specialist_obligations"][0]["obligations"])
        self.assertIsNone(result["review_status"])

    def test_invalid_or_unsupported_claims_are_rejected(self):
        plan = self.plan()
        for field, value in (
            ("assessment", "passed"),
            ("evidence_refs", []),
            ("source_ref", ""),
        ):
            reply = self.response(plan)
            reply["assessed_obligations"][0][field] = value
            with self.subTest(field=field), self.assertRaises(TeamPlanningError):
                _validate_first_pass([reply], plan)

    def test_unverified_obligation_explains_missing_evidence(self):
        plan = self.plan()
        reply = self.response(plan)
        obligation = reply["assessed_obligations"][0]
        obligation["assessment"] = "unverified"
        obligation["evidence_refs"] = []
        obligation["limitations"] = ["Downstream consumer unavailable"]
        self.assertIn("specification-reviewer", _validate_first_pass([reply], plan))
        obligation["limitations"] = []
        with self.assertRaisesRegex(TeamPlanningError, "limitations"):
            _validate_first_pass([reply], plan)

    def test_other_lenses_do_not_require_specification_field(self):
        plan = self.plan("correctness-reviewer")
        reply = self.response(plan)
        del reply["assessed_obligations"]
        self.assertIn("correctness-reviewer", _validate_first_pass([reply], plan))
        reply["assessed_obligations"] = []
        with self.assertRaisesRegex(TeamPlanningError, "only specification"):
            _validate_first_pass([reply], plan)

    def test_conditional_method_and_single_verdict_wiring(self):
        reference = (ROOT / "contexts/review/skills/review-change/references/specification-review.md").read_text()
        agent = (ROOT / "contexts/review/agents/specification-reviewer.md").read_text()
        skill = (ROOT / "contexts/review/skills/review-change/SKILL.md").read_text()
        contract = (ROOT / "contracts/review-specialist-evidence.md").read_text()
        self.assertIn("Trace both directions", reference)
        self.assertIn("Attempt concrete falsification", reference)
        self.assertIn("specification-review.md", agent)
        self.assertIn("specification-review.md", skill)
        self.assertIn("assessed_obligations", contract)
        self.assertIn("No new verdict or gate", contract)


if __name__ == "__main__":
    unittest.main()
