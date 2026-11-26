"""Fitness checks for the canonical Design handoff."""

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def doc(path):
    return (ROOT / path).read_text(encoding="utf-8")


class DesignContextTests(unittest.TestCase):
    def test_command_is_scoped_and_non_mutating(self):
        text = doc("contexts/design/commands/design-solution.md")
        for expected in ("## Intent", "## Invocation", "## Uses", "## Inputs", "## Output", "## Boundary", "No source/test code mutation", "design-evidence.md"):
            self.assertIn(expected, text)

    def test_skill_has_risk_sensitive_handoff(self):
        text = doc("contexts/design/skills/design-solution/SKILL.md")
        for expected in ("name: design-solution", "## Workflow", "```mermaid", "readiness", "Requirements owner", "Stop Conditions"):
            self.assertIn(expected, text)

    def test_design_is_not_business_specification_owner(self):
        rule = doc("contexts/design/rules/design.md")
        contract = doc("contracts/design-evidence.md")
        self.assertIn("does not authorize changes to product requirements", rule)
        self.assertIn("A design alternative is not a business requirement", contract)
        self.assertIn("source_baseline_ref", contract)

    def test_http_guidance_is_conditional_and_not_a_new_contract(self):
        rule = doc("contexts/design/rules/design.md")
        skill = doc("contexts/design/skills/design-solution/SKILL.md")
        reference = doc("contexts/design/skills/design-solution/references/http-api-design.md")
        self.assertIn("When a slice creates or changes an HTTP API", rule)
        self.assertIn("For an HTTP API contract or behavioral change", skill)
        self.assertIn("RFC 9110", reference)
        self.assertIn("RFC 9111", reference)
        self.assertIn("not an automatic requirement", reference)
        self.assertIn("contracts/design-evidence.md", skill)

    def test_architecture_and_linter_register_context(self):
        arch = doc("ARCHITECTURE.md")
        lint = doc("scripts/toolkit_lint.py")
        self.assertIn("| Design | `rules/design.md` | Rule |", arch)
        self.assertIn("| Cross-context | `contracts/design-evidence.md` | Contract |", arch)
        self.assertIn('"Design"', lint)


if __name__ == "__main__":
    unittest.main()
