"""Comparison metrics require independent, matched observations."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from context_compare import ComparisonError, evaluate_runs, load_case_ids  # noqa: E402


class ContextComparisonTests(unittest.TestCase):
    def record(self, strategy, **extra):
        rec = {
            "case_id": "CX-01", "strategy": strategy, "iteration": 1,
            "model": "fixture-model", "harness": "test-harness",
            "repository_sha": "a" * 40, "source_baseline_ref": "R-1",
            "authority_ref": "read-only", "cache_state": "cold",
            "verdict": "pass", "reviewer": "independent-1",
            "trace_ref": "trace-1", "tokens": 200, "elapsed_ms": 300,
            "required_obligations": 2, "verified_obligations": 2,
        }
        rec.update(extra)
        return rec

    def test_only_matched_runs_are_compared(self):
        baseline = self.record("native")
        indexed = self.record("sqlite-fts5", tokens=180, elapsed_ms=400)
        result = evaluate_runs(
            {"version": 1, "runs": [baseline, indexed]},
            load_case_ids(ROOT),
        )
        self.assertEqual(result["status"], "observations-only")
        self.assertEqual(result["matched_pairs"][0]["tokens_delta"], -20)
        self.assertEqual(result["matched_pairs"][0]["elapsed_ms_delta"], 100)

    def test_different_baseline_is_not_compared(self):
        baseline = self.record("native")
        indexed = self.record("sqlite-fts5", source_baseline_ref="R-2")
        result = evaluate_runs(
            {"version": 1, "runs": [baseline, indexed]}, load_case_ids(ROOT)
        )
        self.assertEqual(result["matched_pairs"], [])
        self.assertEqual(result["unmatched_candidates"], 1)

    def test_missing_metric_does_not_become_zero(self):
        baseline = self.record("native", tokens=None)
        indexed = self.record("structural", tokens=50)
        result = evaluate_runs(
            {"version": 1, "runs": [baseline, indexed]}, load_case_ids(ROOT)
        )
        self.assertIsNone(result["matched_pairs"][0]["tokens_delta"])

    def test_unverified_success_is_rejected(self):
        invalid = self.record("native")
        del invalid["trace_ref"]
        with self.assertRaises(ComparisonError):
            evaluate_runs({"version": 1, "runs": [invalid]}, load_case_ids(ROOT))

    def test_duplicate_mode_fixture_rejected(self):
        x = self.record("native")
        with self.assertRaises(ComparisonError):
            evaluate_runs({"version": 1, "runs": [x, x]}, load_case_ids(ROOT))

    def test_no_runs_do_not_count_as_success(self):
        result = evaluate_runs({"version": 1, "runs": []}, load_case_ids(ROOT))
        self.assertEqual(result["status"], "no-observations")
        self.assertEqual(result["matched_pairs"], [])


if __name__ == "__main__":
    unittest.main()
