"""Structural regressions for semantic-change reconciliation across Requirements.

No executable runtime semantic diff or AI-agent behavior is claimed here.
"""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def doc(p):
    return (ROOT / p).read_text(encoding="utf-8")


class RequirementsReconciliationPolicyTests(unittest.TestCase):
    def test_change_rule_distinguishes_meaning_from_format_and_authority(self):
        text = doc("contexts/requirements/rules/requirements.md")
        section = text.split("## Requirement Change and Impact", 1)[1].split("## Requirements Architecture and Traceability", 1)[0]
        for term in ("old and proposed meanings", "formatting-only edit",
                     "proposed", "authorized/accepted", "rejected", "deferred",
                     "missing authority remains unresolved"):
            with self.subTest(term=term):
                self.assertIn(term, section)

    def test_impact_categories_and_unknown_consumers_are_explicit(self):
        text = doc("contexts/requirements/rules/requirements.md")
        for term in ("confirmed impact", "possible impact needing inspection",
                     "unaffected with rationale", "unavailable evidence",
                     "not confirmed current", "known evidence and intended downstream decision"):
            self.assertIn(term, text)

    def test_source_contract_preserves_baseline_change_and_assessment(self):
        text = doc("contracts/requirements.md")
        for term in ("`baseline_ref`", "`semantic_changes`",
                     "`impact_assessment`", "approved baseline revision",
                     "unknown/needs inspection"):
            self.assertIn(term, text)

    def test_workflows_route_reconciliation_without_mutating_validation(self):
        definition = doc("contexts/requirements/skills/definition/SKILL.md")
        validation = doc("contexts/requirements/skills/validation/SKILL.md")
        shape = doc("contexts/requirements/commands/specify-and-plan-change.md")
        basis = doc("contracts/test-basis.md")
        self.assertIn("InspectEvidence --> ComparePriorSemantics", definition)
        self.assertIn("Reconcile[\"Requirement Change and Impact when prior semantics exist\"]", validation)
        self.assertIn("Validation is read-only", validation)
        self.assertIn("known baseline/semantic-change/impact evidence", shape)
        self.assertIn("`source_baseline_ref`", basis)


if __name__ == "__main__":
    unittest.main()
