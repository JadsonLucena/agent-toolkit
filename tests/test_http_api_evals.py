"""HTTP API evaluation fixtures: structure and absent-observation behavior only."""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from requirements_evals import evaluate, load_catalog  # noqa: E402


class HttpApiEvaluationCatalogTests(unittest.TestCase):
    def test_valid_catalog_has_complementary_scenarios(self):
        catalog = load_catalog(ROOT / "evals/api/cases.json")
        self.assertEqual(16, len(catalog["cases"]))
        ids = [case["id"] for case in catalog["cases"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(all(len(case["checks"]) >= 3 for case in catalog["cases"]))
        self.assertTrue(any("offset" in case["scenario"].lower() for case in catalog["cases"]))
        self.assertTrue(any("keyset" in case["scenario"].lower() for case in catalog["cases"]))
        for case in catalog["cases"]:
            for check in case["checks"]:
                expected = "absence" if check["criterion"].startswith("Does not") else "presence"
                with self.subTest(case=case["id"], check=check["id"]):
                    self.assertEqual(expected, check["mode"])

    def test_unobserved_agent_runs_cannot_pass(self):
        catalog = load_catalog(ROOT / "evals/api/cases.json")
        result = evaluate(catalog, {"version": 1, "assessments": []}, ROOT / "evals/api")
        self.assertEqual("INCOMPLETE", result["status"])
        self.assertEqual(len(catalog["cases"]), result["incomplete"])


if __name__ == "__main__":
    unittest.main()
