"""Static verification for the Debugging behavioral catalog (not LLM evaluation)."""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class DebuggingCatalogTests(unittest.TestCase):
    def load_cases(self):
        data = json.loads((ROOT / "evals/debugging/cases.json").read_text(encoding="utf-8"))
        self.assertEqual(1, data["schema_version"])
        return data["cases"]

    def test_behavior_catalog_has_distinct_meaningful_cases(self):
        cases = self.load_cases()
        self.assertGreaterEqual(len(cases), 5)
        ids = [case["id"] for case in cases]
        self.assertEqual(len(ids), len(set(ids)))
        for case in cases:
            self.assertRegex(case["id"], r"^[a-z]+(?:-[a-z]+)+$")
            self.assertGreaterEqual(len(case["scenario"]), 80)
            self.assertTrue(case["expected"])
            self.assertTrue(case["forbidden"])
            self.assertTrue(all(len(item) > 15 for item in case["expected"] + case["forbidden"]))

    def test_debugging_routing_cases_cover_positive_and_negative_boundaries(self):
        data = json.loads((ROOT / "evals/routing/cases.json").read_text(encoding="utf-8"))
        debugging = [case for case in data["cases"] if case["id"].startswith(("skill-debugging-", "agent-debugging-", "command-debugging-", "rule-debugging-"))]
        self.assertGreaterEqual(len(debugging), 10)
        self.assertEqual({"skill", "agent", "command", "rule"}, {case["kind"] for case in debugging})
        self.assertTrue(any("systematic-debugging" in case["expected"] for case in debugging))
        self.assertTrue(any("systematic-debugging" in case["forbidden"] for case in debugging))
        self.assertTrue(any("investigate-defect" in case["expected"] for case in debugging))
        self.assertTrue(any("debugging" in case["expected"] for case in debugging if case["kind"] == "rule"))
        self.assertTrue(any("debugging-investigator" in case["expected"] for case in debugging))


if __name__ == "__main__":
    unittest.main()
