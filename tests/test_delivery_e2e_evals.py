"""Delivery end-to-end eval catalog proves missing host runs stay INCOMPLETE."""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from requirements_evals import load_catalog, evaluate  # noqa: E402


class DeliveryE2EEvalsTests(unittest.TestCase):
    def test_cases_are_valid_and_target_delivery(self):
        cat = load_catalog(ROOT / "evals/delivery/cases.json")
        self.assertEqual(28, len(cat["cases"]))
        self.assertTrue(all(x["command"] in {"/delivery/deliver-change", "/implementation/implement-slice"} for x in cat["cases"]))
        self.assertEqual({f"DL-{i:02d}" for i in range(11, 29)},
                         {x["id"] for x in cat["cases"] if int(x["id"].split("-")[1]) >= 11})
        self.assertEqual(len(cat["cases"]), len(set(x["id"] for x in cat["cases"])))
        self.assertTrue(all(len(x["checks"]) >= 3 for x in cat["cases"]))

    def test_git_handoff_cases_are_actionable_and_modes_are_correct(self):
        cat = load_catalog(ROOT / "evals/delivery/cases.json")
        cases = {item["id"]: item for item in cat["cases"]}
        for index in range(11, 16):
            case = cases[f"DL-{index:02d}"]
            self.assertEqual(3, len(case["checks"]))
            for check in case["checks"]:
                expected = "absence" if check["criterion"].startswith("Does not") else "presence"
                with self.subTest(case=case["id"], check=check["id"]):
                    self.assertEqual(expected, check["mode"])

    def test_integration_lifecycle_cases_and_check_modes(self):
        cat = load_catalog(ROOT / "evals/delivery/cases.json")
        cases = {item["id"]: item for item in cat["cases"]}
        for index in range(16, 22):
            case = cases[f"DL-{index:02d}"]
            self.assertEqual("/delivery/deliver-change", case["command"])
            self.assertEqual(3, len(case["checks"]))
            for check in case["checks"]:
                expected = "absence" if check["criterion"].startswith("Does not") else "presence"
                with self.subTest(case=case["id"], check=check["id"]):
                    self.assertEqual(expected, check["mode"])

    def test_slice_continuity_and_context_selection_case_modes(self):
        cat = load_catalog(ROOT / "evals/delivery/cases.json")
        cases = {item["id"]: item for item in cat["cases"]}
        for index in range(22, 29):
            case = cases[f"DL-{index:02d}"]
            self.assertEqual("/delivery/deliver-change", case["command"])
            self.assertEqual(3, len(case["checks"]))
            for check in case["checks"]:
                expected = "absence" if check["criterion"].startswith("Does not") else "presence"
                with self.subTest(case=case["id"], check=check["id"]):
                    self.assertEqual(expected, check["mode"])

    def test_no_invented_pass_without_agent_execution(self):
        cat = load_catalog(ROOT / "evals/delivery/cases.json")
        summary = evaluate(cat, {"version": 1, "assessments": []}, ROOT / "evals/delivery")
        self.assertEqual("INCOMPLETE", summary["status"])
        self.assertEqual(28, summary["incomplete"])


if __name__ == "__main__":
    unittest.main()
