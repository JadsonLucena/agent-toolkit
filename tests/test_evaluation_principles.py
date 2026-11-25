"""Guard the evaluation methodology's scope and refined principles.

These are structural regression checks, not proof of agent behavior or enforcement.
"""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


class EvaluationPrinciplesTests(unittest.TestCase):
    def test_single_ordered_evaluation_reference(self):
        doc = read("evals/README.md")
        numbered = re.findall(r"^(\\d+)\\. \\*\\*([^*]+)\\*\\*\\.", doc, re.M)
        self.assertEqual([str(i) for i in range(1, 16)], [n for n, _ in numbered])
        self.assertEqual(15, len({title for _, title in numbered}))

    def test_source_authority_and_operation_authorization_are_precise(self):
        doc = read("evals/README.md")
        self.assertIn("Source authority over inference", doc)
        self.assertIn("owner, version, scope, and precedence", doc)
        self.assertIn("never turn a preference into a universal requirement", doc)
        self.assertIn("Operation-specific authorization and traceable effects", doc)
        self.assertIn("authorization for that exact operation", doc)

    def test_methodology_does_not_become_a_second_runtime_policy(self):
        doc = read("evals/README.md")
        for phrase in ("not** a fifth canonical artifact", "not** a new schema or verdict enum",
                       "not** authorize repository edits", "not** a new canonical Rule",
                       "actual agent behavior requires observed host executions"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, doc)
        self.assertIn("independent review where the owning policy permits advisory self-review", doc)
        self.assertIn("Missing host execution remains **not measured**", doc)

    def test_references_are_linked_from_owners_without_duplication(self):
        for path in ("AGENTS.md", "ARCHITECTURE.md", "README.md"):
            with self.subTest(path=path):
                self.assertIn("(evals/README.md)", read(path))
        for context in ("routing", "delivery", "review", "requirements", "context", "debugging"):
            self.assertIn(f"({context}/README.md)", read("evals/README.md"))


if __name__ == "__main__":
    unittest.main()
