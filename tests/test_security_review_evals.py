"""Structural checks for security-review evaluation inputs; not host-behavior evidence."""
import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "evals/security/cases.json"
README = ROOT / "evals/security/README.md"
WORKFLOW = ROOT / ".github/workflows/toolkit-validation.yml"


class SecurityReviewEvalCatalogTests(unittest.TestCase):
    def setUp(self):
        self.catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
        self.cases = {c["id"]: c for c in self.catalog["cases"]}

    def test_catalog_is_validated_by_shared_checker(self):
        module_path = ROOT / "scripts/requirements_evals.py"
        spec = importlib.util.spec_from_file_location("requirements_eval_catalog", module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertEqual(self.catalog, module.load_catalog(CATALOG_PATH))
        self.assertIn("evals/security/cases.json", WORKFLOW.read_text(encoding="utf-8"))

    def test_realistic_attack_and_counterexample_pairs_exist(self):
        for cid in ("SEC-01", "SEC-03", "SEC-05", "SEC-07", "SEC-09", "SEC-11", "SEC-13"):
            with self.subTest(case=cid):
                self.assertTrue(any(c["mode"] == "presence" for c in self.cases[cid]["checks"]))
        for cid in ("SEC-02", "SEC-04", "SEC-06", "SEC-10", "SEC-12", "SEC-14"):
            with self.subTest(case=cid):
                self.assertTrue(any(c["mode"] == "absence" for c in self.cases[cid]["checks"]))
        self.assertIn("SEC-08", self.cases)

    def test_no_fake_observations_bundled(self):
        self.assertGreaterEqual(len(self.cases), 12)
        self.assertTrue(all(c["command"] == "/review/review-code" for c in self.cases.values()))
        for case in self.cases.values():
            self.assertEqual(len(set(x["id"] for x in case["checks"])), len(case["checks"]))
            self.assertTrue(all(x["mode"] in ("presence", "absence") for x in case["checks"]))
        readme = README.read_text(encoding="utf-8")
        self.assertIn("NOT MEASURED", readme)
        self.assertIn("--no-security-audit", readme)


if __name__ == "__main__":
    unittest.main()
