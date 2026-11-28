"""Structural and executable fixture checks for correctness review benchmarks."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from requirements_evals import evaluate, load_catalog  # noqa: E402

CATALOG = ROOT / "evals/review/correctness-cases.json"
BUILDER = ROOT / "evals/review/build_correctness_fixtures.py"


def run(*args, cwd=None):
    return subprocess.run(args, cwd=cwd, check=True,
                          capture_output=True, text=True).stdout.strip()


class CorrectnessReviewEvalsTests(unittest.TestCase):
    def test_cases_have_both_defects_and_false_positive_controls(self):
        cat = load_catalog(CATALOG)
        self.assertEqual(10, len(cat["cases"]))
        ids = [case["id"] for case in cat["cases"]]
        self.assertEqual(len(ids), len(set(ids)))
        groups = {case["polarity"] for case in cat["cases"]}
        self.assertEqual({"defect", "non-defect", "uncertain"}, groups)
        for case in cat["cases"]:
            with self.subTest(case=case["id"]):
                self.assertEqual("/review/review-code", case["command"])
                self.assertGreaterEqual(len(case["checks"]), 3)
                self.assertTrue(any(c["mode"] == "presence" for c in case["checks"]))
                self.assertTrue(any(c["mode"] == "absence" for c in case["checks"]))
                fixture = case["fixture"]
                self.assertEqual("src/logic.py", fixture["path"])
                self.assertTrue(fixture["contract"].startswith("# "))
                self.assertNotEqual(fixture["base"], fixture["changed"])
                compile(fixture["base"], f'{case["id"]}/base.py', "exec")
                compile(fixture["changed"], f'{case["id"]}/head.py', "exec")
                if "head_tests" in fixture:
                    compile(fixture["head_tests"], f'{case["id"]}/tests.py', "exec")
                for check in case["checks"]:
                    expected = ("absence" if check["criterion"].startswith("Does not")
                                else "presence")
                    self.assertEqual(expected, check["mode"])

    def test_ground_truth_witnesses_execute_and_match_contract(self):
        cat = load_catalog(CATALOG)
        for case in cat["cases"]:
            fixture = case["fixture"]
            function = fixture["function"]
            self.assertGreaterEqual(len(fixture["witnesses"]), 1)
            baseline = {}
            head = {}
            exec(compile(fixture["base"], "baseline", "exec"), baseline)
            exec(compile(fixture["changed"], "head", "exec"), head)
            for witness in fixture["witnesses"]:
                with self.subTest(case=case["id"], args=witness["args"]):
                    args = witness["args"]
                    self.assertEqual(witness["baseline"], baseline[function](*args))
                    self.assertEqual(witness["head"], head[function](*args))
                    if case["polarity"] == "defect":
                        self.assertEqual(witness["expected"], witness["baseline"])
                        self.assertNotEqual(witness["expected"], witness["head"])
                    elif case["polarity"] == "non-defect":
                        self.assertEqual(witness["expected"], witness["head"])
                    else:
                        self.assertNotIn("expected", witness)

    def test_unobserved_cases_are_incomplete_not_success(self):
        cat = load_catalog(CATALOG)
        result = evaluate(cat, {"version": 1, "assessments": []}, CATALOG.parent)
        self.assertEqual("INCOMPLETE", result["status"])
        self.assertEqual(len(cat["cases"]), result["incomplete"])
        self.assertEqual(0, result["passed"])

    def test_each_fixture_is_a_real_frozen_git_diff(self):
        cat = load_catalog(CATALOG)
        with tempfile.TemporaryDirectory() as directory:
            for case in cat["cases"]:
                with self.subTest(case=case["id"]):
                    result = json.loads(run(sys.executable, str(BUILDER),
                                            "--case", case["id"], "--out", directory))
                    repo = Path(result["repository"])
                    self.assertEqual(40, len(result["base_sha"]))
                    self.assertEqual(40, len(result["head_sha"]))
                    self.assertNotEqual(result["base_sha"], result["head_sha"])
                    self.assertEqual(result["head_sha"],
                                     run("git", "rev-parse", "HEAD", cwd=repo))
                    self.assertEqual(case["fixture"]["contract"],
                                     (repo / result["contract"]).read_text(encoding="utf-8"))
                    changed = set(run("git", "diff", "--name-only", result["base_sha"],
                                      result["head_sha"], cwd=repo).splitlines())
                    expected = {"src/logic.py"}
                    if "head_tests" in case["fixture"]:
                        expected.add("tests/test_logic.py")
                    self.assertEqual(expected, changed)

    def test_green_test_can_use_the_wrong_oracle(self):
        with tempfile.TemporaryDirectory() as directory:
            result = json.loads(run(sys.executable, str(BUILDER),
                                    "--case", "CR-10", "--out", directory))
            repo = Path(result["repository"])
            run(sys.executable, "-m", "unittest", "discover", "-s", "tests", cwd=repo)
            # The head test passes despite violating docs/accepted-behavior.md.
            self.assertIn("15 percent", (repo / "docs/accepted-behavior.md").read_text())


if __name__ == "__main__":
    unittest.main()
