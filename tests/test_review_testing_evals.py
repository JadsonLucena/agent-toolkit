"""Structural and executable evidence checks for Testing Review evaluation fixtures."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from requirements_evals import evaluate, load_catalog  # noqa: E402

CATALOG = ROOT / "evals/review/testing-cases.json"
BUILDER = ROOT / "evals/review/build_testing_fixtures.py"


def execute(*args, cwd=None):
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True)


class TestingReviewEvalsTests(unittest.TestCase):
    def test_catalog_has_adversarial_and_negative_controls(self):
        catalog = load_catalog(CATALOG)
        self.assertEqual(13, len(catalog["cases"]))
        self.assertEqual({"defect", "non-defect", "uncertain"},
                         {case["polarity"] for case in catalog["cases"]})
        for case in catalog["cases"]:
            with self.subTest(case=case["id"]):
                self.assertEqual("/review/review-code", case["command"])
                self.assertEqual(3, len(case["checks"]))
                self.assertEqual({"presence", "absence"},
                                 {check["mode"] for check in case["checks"]})
                fixture = case["fixture"]
                self.assertNotEqual(fixture["base"], fixture["head"])
                self.assertTrue(fixture["contract"].startswith("# "))
                for kind in ("base", "head", "tests", "witness"):
                    if kind in fixture:
                        compile(fixture[kind], f"{case['id']}/{kind}.py", "exec")
                if case["polarity"] == "uncertain":
                    self.assertNotIn("witness", fixture)
                elif case["id"] != "TR-07":
                    self.assertIn("witness", fixture)

    def test_unobserved_agent_results_are_incomplete(self):
        catalog = load_catalog(CATALOG)
        result = evaluate(catalog, {"version": 1, "assessments": []}, CATALOG.parent)
        self.assertEqual("INCOMPLETE", result["status"])
        self.assertEqual(13, result["incomplete"])
        self.assertEqual(0, result["passed"])

    def test_all_disposable_diffs_and_test_oracles(self):
        catalog = load_catalog(CATALOG)
        with tempfile.TemporaryDirectory() as directory:
            for case in catalog["cases"]:
                with self.subTest(case=case["id"]):
                    output = execute(sys.executable, str(BUILDER), "--case",
                                     case["id"], "--out", directory)
                    self.assertEqual(0, output.returncode, output.stderr)
                    built = json.loads(output.stdout)
                    repository = Path(built["repository"])
                    self.assertEqual(40, len(built["base_sha"]))
                    self.assertEqual(40, len(built["head_sha"]))
                    self.assertNotEqual(built["base_sha"], built["head_sha"])
                    changed = execute("git", "diff", "--name-only",
                                      built["base_sha"], built["head_sha"], cwd=repository)
                    self.assertEqual(0, changed.returncode, changed.stderr)
                    paths = set(changed.stdout.splitlines())
                    expected_paths = {"src/service.py"}
                    if case["fixture"].get("ci_stale"):
                        expected_paths.add("ci/check.json")
                    self.assertEqual(expected_paths, paths)

                    # Git checkout can preserve same-size source timestamps; -B prevents stale .pyc witnesses.
                    for revision in ("base_sha", "head_sha"):
                        checkout = execute("git", "checkout", "--detach", "-q",
                                           built[revision], cwd=repository)
                        self.assertEqual(0, checkout.returncode, checkout.stderr)
                        suite = execute(sys.executable, "-B", "-m", "unittest", "discover",
                                        "-s", "tests", cwd=repository)
                        self.assertEqual(0, suite.returncode,
                                         f"{case['id']}/{revision}: {suite.stderr}")
                        if case["id"] == "TR-06":
                            self.assertIn("skipped=1", suite.stderr)
                        if "witness" in case["fixture"]:
                            witness = execute(sys.executable, "-B", "-m", "unittest",
                                              "discover", "-s", "witness", cwd=repository)
                            expected_status = (0 if revision == "base_sha"
                                               or case["polarity"] == "non-defect" else 1)
                            self.assertEqual(expected_status, witness.returncode,
                                             f"{case['id']}/{revision}: {witness.stderr}")
                        if case["fixture"].get("isolation_probe"):
                            isolated = execute(sys.executable, "-B", "-m", "unittest",
                                               case["fixture"]["isolation_probe"],
                                               cwd=repository)
                            self.assertNotEqual(0, isolated.returncode)
                            self.assertIn("FAIL", isolated.stderr)

                    if case["fixture"].get("ci_stale"):
                        saved = json.loads((repository / "ci/check.json").read_text())
                        self.assertEqual("success", saved["status"])
                        self.assertEqual(built["base_sha"], saved["head_sha"])
                        self.assertNotEqual(built["head_sha"], saved["head_sha"])

    def test_builder_refuses_existing_fixture(self):
        with tempfile.TemporaryDirectory() as directory:
            first = execute(sys.executable, str(BUILDER), "--case", "TR-01",
                            "--out", directory)
            self.assertEqual(0, first.returncode, first.stderr)
            second = execute(sys.executable, str(BUILDER), "--case", "TR-01",
                             "--out", directory)
            self.assertNotEqual(0, second.returncode)
            self.assertIn("refusing to overwrite", second.stderr)


if __name__ == "__main__":
    unittest.main()
