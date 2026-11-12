"""Structural regression checks for Requirements quality-verification semantics.

These tests guard canonical policy/handoff text. They are not behavioral agent
evaluations and do not prove a deployed agent follows the policy.
"""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RULE = ROOT / "contexts/requirements/rules/requirements.md"
VALIDATION = ROOT / "contexts/requirements/skills/validation/SKILL.md"
CONTRACT = ROOT / "contracts/requirements.md"
TEST_BASIS = ROOT / "contracts/test-basis.md"


def section(text: str, heading: str) -> str:
    match = re.search(
        rf"(?ms)^## {re.escape(heading)}\n(.*?)(?=^## |\Z)", text
    )
    return match.group(1) if match else ""


def has_verification_semantics(text: str) -> bool:
    normalized = " ".join(text.lower().split())
    return all(
        part in normalized
        for part in (
            "verification approach",
            "evaluation conditions",
            "expected evidence",
            "technology-neutral",
            "explicit unknown",
        )
    )


class QualityVerificationPolicyTests(unittest.TestCase):
    def test_quality_policy_exposes_method_conditions_and_evidence(self):
        quality = section(RULE.read_text(encoding="utf-8"), "Quality Requirements")
        self.assertTrue(has_verification_semantics(quality))
        self.assertIn("metric or observable property", quality)
        self.assertIn("threshold when justified", quality)
        self.assertIn("observation boundary", quality)

    def test_removing_method_requirement_is_detected(self):
        quality = section(RULE.read_text(encoding="utf-8"), "Quality Requirements")
        self.assertFalse(
            has_verification_semantics(
                quality.replace("verification approach", "optional implementation preference")
            )
        )

    def test_contract_transports_verification_not_executable_tests(self):
        requirements = section(
            CONTRACT.read_text(encoding="utf-8"), "Requirement Specification Semantics"
        )
        test_basis = section(TEST_BASIS.read_text(encoding="utf-8"), "Semantics")
        for field in ("quality verification approach", "evaluation conditions",
                      "expected evidence"):
            self.assertIn(field, requirements)
        for field in ("quality_fit_criteria", "verification approach",
                      "evaluation conditions", "expected evidence"):
            self.assertIn(field, test_basis)
        self.assertIn("not mandated executable tests or tools", test_basis)

    def test_validation_reports_material_gaps_without_inventing(self):
        validation = VALIDATION.read_text(encoding="utf-8")
        self.assertIn("Quality Requirements", validation)
        self.assertIn("readiness_for", validation)
        self.assertIn("report a", validation)
        self.assertIn("needs-clarification", validation)
        self.assertIn("do not invent the missing method", validation)


if __name__ == "__main__":
    unittest.main()
