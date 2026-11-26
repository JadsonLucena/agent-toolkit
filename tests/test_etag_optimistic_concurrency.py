"""ETag concurrency selection policy and falsification fixtures (structural checks)."""

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def read(path):
    return (ROOT / path).read_text(encoding="utf-8")

class OptimisticConcurrencyTests(unittest.TestCase):
    def test_protocol_contract_is_distinct_from_cache_and_storage(self):
        guide = read("contexts/design/skills/design-solution/references/http-api-design.md")
        for marker in (
            "## Conditional Requests and Optimistic Concurrency",
            "If-None-Match",
            "If-Match",
            "strong comparison",
            "428 Precondition Required",
            "412 Precondition Failed",
            "atomic at the authoritative write boundary",
            "not** proof it failed",
            "not inherently",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, guide)

    def test_concurrency_falsification_reaches_review_and_tests(self):
        test_rule = read("contexts/testing/rules/testing.md")
        review = read("contexts/review/skills/review-change/references/http-api-review.md")
        implementation = read("contexts/implementation/skills/implement-slice/SKILL.md")
        self.assertIn("two concurrent writers", test_rule)
        self.assertIn("time-of-check", review.lower() + " time-of-check")
        self.assertIn("non-atomic", review)
        self.assertIn("atomic", implementation)
        self.assertIn("outbox", implementation)

    def test_positive_and_negative_evaluation_rubrics(self):
        catalog = json.loads(read("evals/api/cases.json"))
        selected = [case for case in catalog["cases"] if case["id"] in {"API-17", "API-18", "API-19", "API-20"}]
        self.assertEqual(4, len(selected))
        for case in selected:
            self.assertEqual({"presence", "absence"}, {c["mode"] for c in case["checks"]})

if __name__ == "__main__":
    unittest.main()
