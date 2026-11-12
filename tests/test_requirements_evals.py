"""Regression tests for the Requirements evaluation evidence envelope.

These test the harness and catalog shape, not the behavior of an AI agent.
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from requirements_evals import evaluate, load_catalog  # noqa: E402


class RequirementsEvalTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "trace.txt").write_text(
            "Asked about the underlying need.\n"
            "Identified a pending authority decision.\n",
            encoding="utf-8",
        )
        self.catalog = {
            "version": 1,
            "cases": [{
                "id": "EL-TEST",
                "command": "/requirements/elicit-requirements",
                "scenario": "Unresolved stakeholder intent",
                "input": "Feature request without an agreed business goal",
                "checks": [
                    {"id": "ask", "mode": "presence",
                     "criterion": "Ask about the underlying need"},
                    {"id": "avoid", "mode": "absence",
                     "criterion": "Do not invent stakeholder intent"},
                ],
            }],
        }

    def _assessment(self, quote="Asked about the underlying need."):
        return {
            "version": 1,
            "assessments": [{
                "case_id": "EL-TEST",
                "reviewer": "human reviewer",
                "transcript": "trace.txt",
                "checks": [
                    {"id": "ask", "verdict": "pass",
                     "quote": quote, "rationale": "Question was asked"},
                    {"id": "avoid", "verdict": "pass",
                     "rationale": "Reviewed complete trace for unsupported decisions"},
                ],
            }],
        }

    def test_catalog_in_repository_is_valid(self):
        catalog = load_catalog(ROOT / "evals/requirements/cases.json")
        self.assertGreaterEqual(len(catalog["cases"]), 10)
        self.assertIn("SC-01", {c["id"] for c in catalog["cases"]})

    def test_supported_review_is_passed_without_claiming_llm_execution(self):
        result = evaluate(self.catalog, self._assessment(), self.root)
        self.assertEqual("PASSED", result["status"])
        self.assertEqual(1, result["passed"])

    def test_no_observations_are_incomplete_not_passed(self):
        result = evaluate(self.catalog, {"version": 1, "assessments": []}, self.root)
        self.assertEqual("INCOMPLETE", result["status"])
        self.assertEqual(1, result["incomplete"])

    def test_failure_is_visible(self):
        data = self._assessment()
        data["assessments"][0]["checks"][1]["verdict"] = "fail"
        self.assertEqual("FAILED", evaluate(self.catalog, data, self.root)["status"])

    def test_missing_check_is_incomplete(self):
        data = self._assessment()
        data["assessments"][0]["checks"].pop()
        self.assertEqual("INCOMPLETE", evaluate(self.catalog, data, self.root)["status"])

    def test_quote_must_exist_in_transcript(self):
        with self.assertRaisesRegex(ValueError, "absent from transcript"):
            evaluate(self.catalog, self._assessment("Invented transcript quote"), self.root)

    def test_positive_pass_requires_exact_quote(self):
        data = self._assessment()
        del data["assessments"][0]["checks"][0]["quote"]
        with self.assertRaisesRegex(ValueError, "positive pass requires"):
            evaluate(self.catalog, data, self.root)

    def test_verdict_requires_rationale(self):
        data = self._assessment()
        data["assessments"][0]["checks"][1]["rationale"] = ""
        with self.assertRaisesRegex(ValueError, "rationale required"):
            evaluate(self.catalog, data, self.root)

    def test_unsafe_transcript_path_is_rejected(self):
        data = self._assessment()
        data["assessments"][0]["transcript"] = "../outside.txt"
        with self.assertRaisesRegex(ValueError, "relative path"):
            evaluate(self.catalog, data, self.root)

    def test_unknown_check_is_rejected(self):
        data = self._assessment()
        data["assessments"][0]["checks"][1]["id"] = "not-in-rubric"
        with self.assertRaisesRegex(ValueError, "unknown or duplicate observation"):
            evaluate(self.catalog, data, self.root)

    def test_duplicate_case_or_check_is_rejected(self):
        file = self.root / "catalog.json"
        self.catalog["cases"].append(dict(self.catalog["cases"][0]))
        file.write_text(json.dumps(self.catalog), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "duplicate case id"):
            load_catalog(file)
        self.catalog["cases"].pop()
        self.catalog["cases"][0]["checks"].append(dict(self.catalog["cases"][0]["checks"][0]))
        file.write_text(json.dumps(self.catalog), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "duplicate check id"):
            load_catalog(file)


if __name__ == "__main__":
    unittest.main()
