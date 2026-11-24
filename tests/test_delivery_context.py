"""Delivery structural tests with explicit safety/completeness invariant baseline.

These assertions cannot prove behavior of a real agent host: see evals/delivery.
They intentionally avoid coupling policy regression to Mermaid node names.
"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = "contexts/delivery/skills/coordinate-delivery/SKILL.md"
RULE = "contexts/delivery/rules/delivery.md"
AGENT = "contexts/delivery/agents/delivery-coordinator.md"
COMMAND = "contexts/delivery/commands/deliver-change.md"

# Invariant -> canonical source -> required evidence/stop semantics.
TRANSITION_BASELINE = {
    "authorization": (RULE, ("operation-specific authorization", "Default to read-only assessment", "A stage transition must not broaden permissions")),
    "freshness": (RULE, ("source baseline", "Invalidate only affected", "material handoff")),
    "pre-plan": (RULE, ("before the first implementation mutation", "read-only", "PR Boundary")),
    "commit": (RULE, ("create-semantic-commits/SKILL.md", "verified commit SHA or blocker")),
    "review": (RULE, ("single Code Review verdict", "review_profile=advisory", "PASS")),
    "draft": (RULE, ("remote Draft PR", "same mandatory pre-publication tests/lint and Code Review", "local `draft` preparation")),
    "integration": (RULE, ("separately authorized", "post-publication CI", "observed target state")),
    "slice-completeness": (RULE, ("integrated target revision", "cross-PR", "Product Slice still incomplete")),
    "recovery": (RULE, ("Checkpoints cannot undo", "no material progress")),
    "outcome": (RULE, ("business problem", "outcome")),
}

def doc(path):
    return (ROOT / path).read_text(encoding="utf-8")

class DeliveryContextTests(unittest.TestCase):
    def test_transition_baseline_remains_in_canonical_rules(self):
        for obligation, (path, anchors) in TRANSITION_BASELINE.items():
            content = doc(path).lower()
            for anchor in anchors:
                with self.subTest(obligation=obligation, anchor=anchor):
                    self.assertIn(anchor.lower(), content)

    def test_five_responsibilities_and_compact_graph(self):
        skill, agent = doc(SKILL), doc(AGENT)
        graph = re.search(r"(?s)"+chr(96)*3+"mermaid\\n(.*?)"+chr(96)*3, skill)
        self.assertIsNotNone(graph)
        diagram = graph.group(1)
        self.assertLessEqual(len(diagram.splitlines()), 18)
        for step in ("1. Inspect", "2. Select", "3. Pass", "4. Verify", "5. Supported"):
            self.assertIn(step, diagram)
        for edge in ("Reached -->|Yes| Done", "Specialist --> Reconcile",
                     "Decide -->|Verified progress; more work| Inspect",
                     "Decide -->|Correctable or changed upstream input| Inspect",
                     "Decide -->|Unsafe, unverified or no progress| Block"):
            self.assertIn(edge, diagram)
        for label in ("**Inspect:**", "**Select:**", "**Handoff:**", "**Reconcile:**", "**Decide:**"):
            self.assertIn(label, agent)

    def test_owner_routing_is_composed_not_duplicated(self):
        skill, agent = doc(SKILL), doc(AGENT)
        for owner in ("Requirements", "Design", "Implementation", "Testing", "Review", "Git"):
            self.assertIn(owner, skill)
            self.assertIn(owner, agent)
        for stage in ("planned", "designed", "implemented", "reviewed", "pr-prepared", "pr-created", "integrated"):
            self.assertIn(stage, doc(COMMAND))
            self.assertIn(stage, skill)
        self.assertIn("sole technical verdict", skill)
        self.assertIn("not a substitute Review verdict", agent)

    def test_no_implicit_authorization(self):
        command, rule = doc(COMMAND).lower(), doc(RULE).lower()
        for token in ("read-only", "target_stage", "authorization"):
            self.assertIn(token, command)
        self.assertIn("a target stage alone does not authorize code mutation", command)
        self.assertIn("never implies push", command)
        self.assertIn("once implementation mutation is authorized", command)
        self.assertIn("operation-specific authorization", rule)

    def test_requirements_command_is_resolved_at_runtime(self):
        skill = doc(SKILL)
        for marker in ("/requirements/specify-and-plan-change", "/requirements/shape-change",
                       "actually installed command", "Verify the entry point exists before routing"):
            self.assertIn(marker, skill)

    def test_preimplementation_plan_and_verified_commits_survive(self):
        skill = doc(SKILL)
        self.assertIn("Before any implementation mutation of a composite initiative", skill)
        self.assertIn("PR Boundary", skill)
        self.assertIn("actual verified commit SHA or explicit blocked/uncommitted state", skill)
        self.assertIn("create-semantic-commits/SKILL.md", doc(RULE))

    def test_review_publication_and_draft_gates_survive(self):
        skill = doc(SKILL)
        for marker in ("authorized tests/lint", "independent Code Review",
                       "advisory ", "no remote PR (including Draft)",
                       "pr-prepared", "pr-created", "post-PR checks"):
            self.assertIn(marker, skill)
        self.assertIn("review_profile=advisory", doc(RULE))

    def test_remote_branch_and_existing_pr_guards_survive(self):
        skill = doc(SKILL)
        for marker in ("source branch exists on the correct remote",
                       "If unpublished, stop and report the blocker",
                       "remote identity must be reverified before creation",
                       "existing published PR", "resume the existing PR",
                       "Never implicitly convert an existing Draft to ready"):
            self.assertIn(marker, skill)

    def test_merge_and_product_slice_completion_remain_distinct(self):
        skill = doc(SKILL).lower()
        for marker in ("separate merge authorization", "repository protections",
                       "verify the resulting target branch", "only when applicable",
                       "pr integration status", "product slice technical verification status",
                       "business/stakeholder acceptance", "outcome observation"):
            self.assertIn(marker, skill)

    def test_selective_context_and_recovery_remain_explicit(self):
        skill, agent = doc(SKILL).lower(), doc(AGENT).lower()
        for marker in ("context_id", "change_boundary_ref", "scenario_refs",
                       "source_baseline_ref", "on demand",
                       "referenced, actually retrieved, and verified",
                       "block only the dependent decision"):
            self.assertIn(marker, skill)
        self.assertIn("critical guarantees", agent)
        self.assertIn("checkpoint persisted", agent)
        self.assertIn("does **not** define a new context-packet contract", skill)

    def test_transition_contract_has_complete_conditional_outcomes(self):
        skill = doc(SKILL)
        section = re.search(r"(?ms)^## Transition Contract\n(.*?)(?=^## |\Z)", skill)
        self.assertIsNotNone(section)
        lines = [line for line in section.group(1).splitlines()
                 if line.startswith("| T") and line.count("|") == 7]
        rows = {}
        for line in lines:
            fields = [field.strip() for field in line.strip().strip("|").split("|")]
            self.assertEqual(6, len(fields), line)
            identifier, condition, owner, evidence, success, failure = fields
            self.assertNotIn(identifier, rows, "duplicate transition id")
            self.assertTrue(all((condition, owner, evidence, success, failure)))
            self.assertGreaterEqual(len(evidence.split()), 6)
            self.assertGreaterEqual(len(failure.split()), 6)
            rows[identifier] = {
                "condition": condition, "owner": owner,
                "evidence": evidence, "success": success, "failure": failure,
            }
        self.assertEqual({f"T{i:02d}" for i in range(1, 14)}, set(rows))
        self.assertIn("do not run every row as a mandatory sequence", section.group(1).lower())
        self.assertIn("not a second implementation", section.group(1))

    def test_transitions_retain_review_publication_and_merge_order(self):
        skill = doc(SKILL)
        section = re.search(r"(?ms)^## Transition Contract\n(.*?)(?=^## |\Z)", skill).group(1)
        rows = {
            parts[0]: parts[1:]
            for line in section.splitlines() if line.startswith("| T")
            for parts in [[x.strip() for x in line.strip().strip("|").split("|")]]
        }
        # A row's columns are: condition, owner, evidence, success, failure.
        for ident, fields in {
            "T04": ("before first code mutation", "Git", "PR Boundary", "Implementation", "Block"),
            "T05": ("authorized bounded intention", "Implementation", "commit SHA", "implemented", "failed/unverified"),
            "T06": ("reviewed stage", "independent Review", "tests/lint", "reviewed", "self-review"),
            "T07": ("pr-prepared", "Git", "T06", "pr-prepared", "Draft"),
            "T08": ("after T07", "Git", "create authorization", "pr-created", "push"),
            "T09": ("already exists", "Git", "head/base", "existing PR", "Draft"),
            "T10": ("integrated stage", "Git", "merge authorization", "integrated", "block"),
            "T11": ("Whole Product Slice", "Delivery", "cross-PR", "business acceptance", "incomplete"),
            "T12": ("uncertain side effect", "specialist", "external effect", "reconciliation", "unsafe replay"),
        }.items():
            for column, expected in enumerate(fields):
                with self.subTest(transition=ident, column=column):
                    self.assertIn(expected.lower(), rows[ident][column].lower())

    def test_context_is_registered(self):
        self.assertIn("| Delivery | "+chr(96)+"rules/delivery.md"+chr(96)+" | Rule |", doc("ARCHITECTURE.md"))
        self.assertIn('"Delivery"', doc("scripts/toolkit_lint.py"))

if __name__ == "__main__":
    unittest.main()
