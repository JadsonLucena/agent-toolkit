"""Catalog checks for Review SDD behavioral evaluation fixtures."""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from requirements_evals import load_catalog, evaluate  # noqa: E402


class ReviewSddEvalsTests(unittest.TestCase):
    def test_catalog_valid_and_targets_review(self):
        cat = load_catalog(ROOT / "evals/review/cases.json")
        ids = [x["id"] for x in cat["cases"]]
        self.assertEqual(8, len(ids))
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(all(x["command"] == "/review/review-code" for x in cat["cases"]))
        self.assertTrue(all(len(x["checks"]) >= 3 for x in cat["cases"]))

    def test_missing_observed_agent_runs_cannot_pass(self):
        cat = load_catalog(ROOT / "evals/review/cases.json")
        result = evaluate(cat, {"version": 1, "assessments": []}, ROOT / "evals/review")
        self.assertEqual("INCOMPLETE", result["status"])
        self.assertEqual(len(cat["cases"]), result["incomplete"])


if __name__ == "__main__":
    unittest.main()
