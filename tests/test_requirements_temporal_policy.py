"""Structural regressions for FRET-inspired, tool-neutral temporal semantics.

These assertions check policy/contract wiring, not temporal logic or formal proof.
"""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


class TemporalRequirementsPolicyTests(unittest.TestCase):
    def test_rule_keeps_fretish_optional_and_demands_boundaries(self):
        rule = read("contexts/requirements/rules/requirements.md")
        temporal = rule.split("## Temporal Behavior and Formal Assurance", 1)[1].split("## Security Requirements", 1)[0]
        for token in ("scope or mode", "triggering condition/event",
                      "inclusive/exclusive endpoints", "started before a deadline",
                      "FRETish is optional", "Unknown semantics"):
            with self.subTest(token=token):
                self.assertIn(token, temporal)

    def test_evidence_does_not_confuse_inspection_with_formal_proof(self):
        rule = read("contexts/requirements/rules/requirements.md")
        for token in ("semantic inspection/examples", "formalization against a defined model",
                      "executed formal analysis", "Satisfiability is not realizability",
                      "not executed", "LLM's reasoning alone"):
            self.assertIn(token, rule)

    def test_lifecycle_routes_temporal_cases_without_requiring_fret(self):
        definition = read("contexts/requirements/skills/definition/SKILL.md")
        validation = read("contexts/requirements/skills/validation/SKILL.md")
        self.assertIn("DetermineApplicableSemantics --> AssessTemporalProperties", definition)
        self.assertIn("Temporal Behavior and Formal Assurance", definition)
        self.assertIn('Temporal["Temporal Behavior and Formal Assurance when applicable"]', validation)
        self.assertIn("when absent, report formal analysis as not executed", validation)

    def test_examples_and_contracts_preserve_temporal_meaning(self):
        examples = read("contexts/requirements/skills/example-discovery/SKILL.md")
        contract = read("contracts/requirements.md")
        basis = read("contracts/test-basis.md")
        self.assertIn("before, at, and after", examples)
        self.assertIn("`temporal_properties`", contract)
        self.assertIn("`formal_analysis_evidence`", contract)
        self.assertIn("`temporal_traces`", basis)
        self.assertIn("distinguish examples from formal counterexamples", basis)


if __name__ == "__main__":
    unittest.main()
