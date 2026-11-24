"""Regression checks for Git-owned atomic intention partition and TDD handoffs.

These are policy/diagram checks; live agent behavior requires DL-48..DL-50
host executions with observed edit, verification, and commit order.
"""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


class AtomicIntentionPolicyTests(unittest.TestCase):
    def test_git_rule_defines_atomic_intention_beyond_task(self):
        rule = read("contexts/git/rules/semantic-commit.md")
        section = rule.split("## Atomic Intention and Separation Test", 1)[1].split("## Atomicity", 1)[0]
        for semantic in (
            "Before the first source or test edit",
            "atomic intention",
            "card, task, work item",
            "independently",
            "commit order",
            "experiment",
            "valid intermediate",
            "External task-level",
            "separation test",
        ):
            with self.subTest(semantic=semantic):
                self.assertIn(semantic.lower(), section.lower())
        self.assertIn("The cost of hunk staging does not justify one commit", rule)
        self.assertIn("An untested intermediate state is not proof", section)

    def test_implementation_preedit_partition_has_no_bypass(self):
        skill = read("contexts/implementation/skills/implement-slice/SKILL.md")
        rule = read("contexts/implementation/rules/implementation.md")
        diagram = skill.split("## Workflow", 1)[1].split("## Pre-Edit Atomic Intention Plan", 1)[0]
        for edge in (
            'PlanReady -->|Yes| Partition',
            'Strategy -->|Not required or existing plan valid| Partition',
            'Partition --> PartitionGate',
            'PartitionGate -->|No or unclear| Block',
            'PartitionGate -->|Yes| Plan',
            'Plan --> Test',
            'Repartition -->|Yes| Partition',
        ):
            with self.subTest(edge=edge):
                self.assertIn(edge, diagram)
        self.assertLess(diagram.index('Partition --> PartitionGate'), diagram.index('Plan --> Test'))
        self.assertIn("Before the first source or test edit", rule)
        self.assertIn("Git atomicity takes precedence", rule)

    def test_tdd_not_task_or_cycle_commit_unit(self):
        tdd = read("contexts/implementation/skills/test-driven-development/SKILL.md")
        parent = read("contexts/implementation/skills/implement-slice/SKILL.md")
        for needle in (
            "an external `commit per task` cadence is subordinate",
            "New separately revertible outcome",
            "Dependencies between valid changes determine ordering",
        ):
            self.assertIn(needle, tdd)
        self.assertIn("multiple RED/GREEN/REFACTOR cycles may complete the same intention", parent)
        self.assertIn("only if Git's separation test", parent)

    def test_git_handoff_does_not_retroactively_invent_plan(self):
        skill = read("contexts/git/skills/create-semantic-commits/SKILL.md")
        for needle in (
            "before the first edit",
            "reconstruct the intention partition",
            "do not claim that a pre-edit plan existed",
            "patch/hunk staging",
            "precise intermediate-state invariant",
        ):
            self.assertIn(needle, skill)

    def test_front_door_agent_command_reference_preedit_rule(self):
        command = read("contexts/implementation/commands/implement-slice.md")
        agent = read("contexts/implementation/agents/implementation-engineer.md")
        self.assertIn("Before the first edit", command)
        self.assertIn("task/card-level commit heuristic cannot override", command)
        self.assertIn("partition independently reversible intentions before changing source or tests", agent)

    def test_behavioral_falsification_cases_exist_but_are_not_claimed_passed(self):
        cases = {c["id"]: c for c in json.loads(read("evals/delivery/cases.json"))["cases"]}
        for identifier in ("DL-48", "DL-49", "DL-50"):
            case = cases[identifier]
            self.assertEqual(3, len(case["checks"]))
            self.assertEqual(["presence", "presence", "absence"], [c["mode"] for c in case["checks"]])
        self.assertIn("cannot yield separately valid", cases["DL-37"]["input"])
        self.assertIn("Before the first source or RED test edit", cases["DL-48"]["checks"][0]["criterion"])
        self.assertIn("single commit SHA", cases["DL-49"]["checks"][1]["criterion"])
        self.assertIn("Reassesses the intention partition", cases["DL-50"]["checks"][0]["criterion"])


if __name__ == "__main__":
    unittest.main()
