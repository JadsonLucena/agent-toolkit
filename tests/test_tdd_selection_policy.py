"""Structural regressions for preference-based TDD selection.

These checks validate canonical policy and workflow wiring, not actual
test-first behavior in a model host.
"""

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


class TddSelectionPolicyTests(unittest.TestCase):
    def test_behavior_changes_prefer_tdd_without_a_special_request(self):
        rule = read("contexts/implementation/rules/implementation.md")
        command = read("contexts/implementation/commands/implement-slice.md")
        agent = read("contexts/implementation/agents/implementation-engineer.md")
        tdd = read("contexts/implementation/skills/test-driven-development/SKILL.md")

        for marker in ("Prefer TDD (RED/GREEN/REFACTOR)",
                       "new features", "bug fixes", "business-rule changes",
                       "caller need not explicitly request TDD"):
            with self.subTest(marker=marker):
                self.assertIn(marker, rule)
        self.assertIn("absence of a TDD request is not a direct-implementation exception", command)
        self.assertIn("prefer TDD when feasible", agent)
        self.assertIn("Preferred for features, fixes and business rules", tdd)

    def test_exception_path_records_reason_risk_and_alternative_checks(self):
        rule = read("contexts/implementation/rules/implementation.md")
        implementation = read("contexts/implementation/skills/implement-slice/SKILL.md")

        for marker in ("caller explicitly opts out of TDD",
                       "documentation, formatting, or non-behavioral configuration",
                       "exploratory spike", "explicit restriction on test authoring",
                       "unsafe/disproportionate test-first setup",
                       "Convenience, the absence of a TDD keyword",
                       "alternative verification plan",
                       "required tests, lint"):
            with self.subTest(marker=marker):
                self.assertIn(marker, rule)
        self.assertIn('Test -->|Justified exception| Explain', implementation)
        self.assertIn('Explain --> Change["Apply minimal in-scope implementation"]', implementation)
        self.assertIn('Change --> Check', implementation)
        self.assertIn("concrete exception and alternative verification", implementation)

    def test_explicit_caller_opt_out_does_not_remove_required_tests(self):
        rule = read("contexts/implementation/rules/implementation.md")
        command = read("contexts/implementation/commands/implement-slice.md")
        implementation = read("contexts/implementation/skills/implement-slice/SKILL.md")
        self.assertIn("caller explicitly opts out of TDD", rule)
        self.assertIn("Skipping TDD never waives required tests", rule)
        self.assertIn("An explicit caller TDD opt-out affects sequencing, not required testing", command)
        self.assertIn("Explicit TDD requirement or caller TDD opt-out", command)
        self.assertIn("explicit caller opt-out of TDD permits direct implementation", implementation)
        self.assertIn('Test -->|Justified exception| Explain', implementation)

    def test_failure_reselects_tdd_unless_same_behavior_already_tested(self):
        rule = read("contexts/implementation/rules/implementation.md")
        implementation = read("contexts/implementation/skills/implement-slice/SKILL.md")
        self.assertIn("A failure alone never authorizes silently abandoning TDD", rule)
        self.assertIn('Diagnose -->|Material new progress possible| Reassess', implementation)
        self.assertIn('Reassess -->|Yes or uncertain| Test', implementation)
        self.assertIn('Reassess -->|No; repair existing tested behavior| Change', implementation)
        self.assertNotIn('Diagnose -->|Material new progress possible| Change', implementation)
        self.assertIn("After diagnosis, reselect TDD", implementation)

    def test_merged_atomic_commit_boundary_and_authorization_are_preserved(self):
        implementation = read("contexts/implementation/skills/implement-slice/SKILL.md")
        tdd = read("contexts/implementation/skills/test-driven-development/SKILL.md")
        self.assertIn('ScopeGate -->|No or unclear| Block', implementation)
        self.assertIn("ResolveCommit --> Strategy", implementation)
        self.assertIn('CommitAuthority -->|Explicitly denied| Uncommitted', implementation)
        self.assertIn('CommitAuthority -->|Unknown| Block', implementation)
        self.assertIn('Evidence --> Boundary{"Current atomic intention complete?"}', tdd)
        self.assertIn('Boundary -->|Yes| Done["Return to implement-slice for integrated verification and Git handoff"]', tdd)
        self.assertIn("multiple RED/GREEN/REFACTOR cycles may complete the same intention", implementation)
        self.assertIn('CommitVerified -->|Yes| More', implementation)

    def test_discovery_and_architecture_metadata_match_preferred_policy(self):
        rule = read("contexts/implementation/rules/implementation.md")
        command = read("contexts/implementation/commands/implement-slice.md")
        implementation = read("contexts/implementation/skills/implement-slice/SKILL.md")
        arch = read("ARCHITECTURE.md")
        self.assertIn("prefer test-first TDD for testable behavior", rule.split("---", 2)[1])
        self.assertIn("preferring test-first TDD", command.split("---", 2)[1])
        self.assertIn("TDD as the preferred testable-behavior strategy", implementation.split("---", 2)[1])
        self.assertIn("Preferred RED/GREEN/REFACTOR inner loop", arch)

    def test_required_tdd_cannot_silently_degrade_to_direct_implementation(self):
        rule = read("contexts/implementation/rules/implementation.md")
        implementation = read("contexts/implementation/skills/implement-slice/SKILL.md")
        self.assertIn("caller explicitly requires TDD", rule)
        self.assertIn("stop and report the blocker", rule)
        self.assertIn('Test -->|Required but unavailable or unsafe| Block', implementation)
        self.assertIn('Test -->|Yes and feasible| TDD', implementation)
        self.assertIn('TDD --> Check', implementation)

    def test_tdd_remains_owned_and_both_paths_keep_integrated_gates(self):
        implementation = read("contexts/implementation/skills/implement-slice/SKILL.md")
        tdd = read("contexts/implementation/skills/test-driven-development/SKILL.md")
        self.assertIn("## Test Strategy Selection", implementation)
        self.assertIn("contexts/implementation/rules/implementation.md", implementation)
        self.assertIn("Selection and exceptions are decided by `implement-slice`", tdd)
        for marker in ("RED:", "GREEN:", "REFACTOR:"):
            self.assertIn(marker, tdd)
        for marker in ("Check --> Gate", "Gate -->|Yes| CommitAuthority",
                       "Commit --> CommitVerified", "CommitVerified -->|Yes| More"):
            self.assertIn(marker, implementation)
        self.assertIn("not a prerequisite for all tasks", read("contexts/implementation/rules/implementation.md"))


if __name__ == "__main__":
    unittest.main()
