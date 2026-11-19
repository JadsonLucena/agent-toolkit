"""Behavioral context evaluation catalog; these tests never simulate an LLM run."""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from requirements_evals import evaluate, load_catalog  # noqa: E402


class ContextEvalsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = load_catalog(ROOT / "evals/context/cases.json")
        cls.delivery = load_catalog(ROOT / "evals/delivery/cases.json")

    def test_no_duplicate_delivery_scenarios(self):
        self.assertEqual(len(self.catalog["cases"]), 6)
        self.assertTrue({"DL-05", "DL-08", "DL-25", "DL-26", "DL-27"}.issubset(
            {case["id"] for case in self.delivery["cases"]}
        ))
        self.assertEqual(len({case["id"] for case in self.catalog["cases"]}), 6)

    def test_relevant_negative_and_positive_checks(self):
        for case in self.catalog["cases"]:
            modes = {check["mode"] for check in case["checks"]}
            with self.subTest(case=case["id"]):
                self.assertIn("presence", modes)
                self.assertIn("absence", modes)

    def test_without_real_host_observations_remains_incomplete(self):
        verdict = evaluate(self.catalog, {"version": 1, "assessments": []}, ROOT)
        self.assertEqual(verdict["status"], "INCOMPLETE")
        self.assertEqual(verdict["incomplete"], len(self.catalog["cases"]))
        self.assertEqual(verdict["passed"], 0)

    def test_readme_discloses_limits(self):
        doc = (ROOT / "evals/context/README.md").read_text(encoding="utf-8")
        for marker in ("DL-25", "real compaction event", "INCOMPLETE",
                       "without SQLite", "independently assess"):
            with self.subTest(marker=marker):
                self.assertIn(marker, doc)


if __name__ == "__main__":
    unittest.main()
