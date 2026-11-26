"""Structural regression checks for refactoring modes and safety boundaries.

These assertions check guidance wiring, not actual host behavior.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


class RefactoringImplementationPolicyTests(unittest.TestCase):
    def test_structural_only_never_fabricates_red(self):
        rule = read("contexts/implementation/rules/implementation.md")
        skill = read("contexts/implementation/skills/implement-slice/SKILL.md")
        self.assertIn("do not fabricate a failing RED", rule)
        self.assertIn("Structural-only, no new behavior", skill)
        self.assertIn("Baseline --> Change", skill)
        self.assertIn("A passing baseline is not a TDD RED", skill)

    def test_tdd_refactor_is_scoped_and_may_be_no_op(self):
        tdd = read("contexts/implementation/skills/test-driven-development/SKILL.md")
        self.assertIn("## REFACTOR Decision", tdd)
        self.assertIn("verified no-op", tdd)
        self.assertIn("after each transformation", tdd)
        self.assertIn("not silently included in REFACTOR", tdd)

    def test_legacy_protection_includes_side_effects_and_boundaries(self):
        rule = read("contexts/testing/rules/testing.md")
        guide = read("contexts/implementation/skills/implement-slice/references/refactoring.md")
        self.assertIn("never replay real payments", rule)
        self.assertIn("preconditions, postconditions", guide)
        self.assertIn("Strangler Fig", guide)
        self.assertIn("Git's independent reversible-intention test", guide)
        self.assertIn("required integrated checks", guide)

    def test_mode_does_not_bypass_authority_or_git(self):
        skill = read("contexts/implementation/skills/implement-slice/SKILL.md")
        self.assertIn("ScopeGate -->|No or unclear| Block", skill)
        self.assertIn("Commit --> CommitVerified", skill)
        self.assertIn("No implicit requirement approval, unrelated refactoring", skill)


if __name__ == "__main__":
    unittest.main()
