"""Structural regression checks for conditional-write concurrency guidance."""

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


class OptimisticConcurrencyTests(unittest.TestCase):
    def test_guidance_focuses_on_lost_update_prevention(self):
        guide = read("contexts/design/skills/design-solution/references/http-api-design.md")
        section = guide.split("## Conditional Requests and Optimistic Concurrency", 1)[1].split("\n## ", 1)[0]
        for required in (
            "strong ETag", "If-Match", "412 Precondition Failed",
            "atomic", "lost updates", "If-None-Match", "idempotency",
        ):
            with self.subTest(required=required):
                self.assertIn(required, section)
        for out_of_scope in ("outbox", "financial deduplication", "PUT response"):
            self.assertNotIn(out_of_scope, section)

    def test_lifecycle_preserves_atomicity(self):
        impl = read("contexts/implementation/skills/implement-slice/SKILL.md")
        testing = read("contexts/testing/rules/testing.md")
        review = read("contexts/review/skills/review-change/references/http-api-review.md")
        self.assertIn("an unconditional update", impl)
        self.assertIn("competing writes", testing)
        self.assertIn("atomic persistence update", review)

    def test_focused_evaluation_cases(self):
        cases = json.loads(read("evals/api/cases.json"))["cases"]
        selected = [case for case in cases if case["id"] in {"API-17", "API-18"}]
        self.assertEqual(2, len(selected))
        self.assertFalse(any(case["id"] in {"API-19", "API-20"} for case in cases))
        for case in selected:
            self.assertEqual({"presence", "absence"}, {c["mode"] for c in case["checks"]})


if __name__ == "__main__":
    unittest.main()
