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
        self.assertEqual(47, len(cat["cases"]))
        self.assertTrue(all(x["command"] in {"/delivery/deliver-change", "/implementation/implement-slice", "/git/create-pull-request"} for x in cat["cases"]))
        self.assertEqual({f"DL-{i:02d}" for i in range(11, 48)},
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
        for index in range(22, 30):
            case = cases[f"DL-{index:02d}"]
            self.assertEqual("/delivery/deliver-change", case["command"])
            self.assertEqual(3, len(case["checks"]))
            for check in case["checks"]:
                expected = "absence" if check["criterion"].startswith("Does not") else "presence"
                with self.subTest(case=case["id"], check=check["id"]):
                    self.assertEqual(expected, check["mode"])

    def test_unpublished_branch_case_protects_remote_creation(self):
        cat = load_catalog(ROOT / "evals/delivery/cases.json")
        case = next(x for x in cat["cases"] if x["id"] == "DL-29")
        self.assertEqual("/delivery/deliver-change", case["command"])
        self.assertIn("source branch", case["scenario"])
        self.assertIn("does not authorize push", case["input"])
        self.assertIn("not published", case["checks"][0]["criterion"])
        self.assertEqual("absence", case["checks"][2]["mode"])
        self.assertIn("Does not push the branch, invoke PR creation", case["checks"][2]["criterion"])

    def test_responsibility_boundaries_and_pdca_feedback_cases(self):
        cat = load_catalog(ROOT / "evals/delivery/cases.json")
        cases = {item["id"]: item for item in cat["cases"]}
        expected = {
            "DL-30": ("Design", "Requirements"),
            "DL-31": ("Testing", "Implementation"),
            "DL-32": ("Delivery", "read-only"),
            "DL-33": ("PDCA", "business decision owner"),
            "DL-34": ("self-review", "independent"),
        }
        for case_id, (subject, owner) in expected.items():
            with self.subTest(case=case_id):
                case = cases[case_id]
                self.assertIn(subject.lower(), (case["scenario"] + " " + case["input"]).lower())
                checks = case["checks"]
                self.assertEqual(3, len(checks))
                self.assertEqual(["presence", "presence", "absence"],
                                 [check["mode"] for check in checks])
                self.assertTrue(checks[-1]["criterion"].startswith("Does not"))
                self.assertIn(owner.lower(), " ".join(check["criterion"] for check in checks).lower())

    def test_commit_authority_and_tdd_behavioral_pilots(self):
        cat = load_catalog(ROOT / "evals/delivery/cases.json")
        cases = {item["id"]: item for item in cat["cases"]}
        for case_id in ("DL-35", "DL-36", "DL-37", "DL-38"):
            case = cases[case_id]
            self.assertEqual(3, len(case["checks"]))
            self.assertEqual(["presence", "presence", "absence"],
                             [check["mode"] for check in case["checks"]])
            self.assertTrue(case["checks"][-1]["criterion"].startswith("Does not"))
        self.assertEqual("/implementation/implement-slice", cases["DL-35"]["command"])
        self.assertEqual("/delivery/deliver-change", cases["DL-36"]["command"])
        self.assertIn("multiple TDD cycles", cases["DL-37"]["input"])
        self.assertIn("explicitly forbids", cases["DL-38"]["input"])

    def test_prepublication_review_and_draft_bypass_cases(self):
        cat = load_catalog(ROOT / "evals/delivery/cases.json")
        cases = {item["id"]: item for item in cat["cases"]}
        self.assertIn("Draft cannot bypass", cases["DL-19"]["scenario"])
        self.assertEqual(["presence", "presence", "absence"],
                         [check["mode"] for check in cases["DL-19"]["checks"]])
        for index in range(39, 43):
            case = cases[f"DL-{index:02d}"]
            with self.subTest(case=case["id"]):
                self.assertEqual("/git/create-pull-request", case["command"])
                self.assertEqual(["presence", "presence", "absence"],
                                 [check["mode"] for check in case["checks"]])
                self.assertTrue(case["checks"][-1]["criterion"].startswith("Does not"))

    def test_preferred_tdd_opt_out_exception_and_recovery_cases(self):
        cat = load_catalog(ROOT / "evals/delivery/cases.json")
        cases = {item["id"]: item for item in cat["cases"]}
        expectations = {
            "DL-43": ("without naming TDD", "/implementation/implement-slice"),
            "DL-44": ("without TDD", "/implementation/implement-slice"),
            "DL-45": ("destructive third-party service", "/implementation/implement-slice"),
            "DL-46": ("explicitly requires TDD", "/implementation/implement-slice"),
            "DL-47": ("behavioral edge case", "/delivery/deliver-change"),
        }
        for case_id, (prompt, command) in expectations.items():
            with self.subTest(case=case_id):
                case = cases[case_id]
                self.assertIn(prompt, case["input"])
                self.assertEqual(command, case["command"])
                self.assertEqual(["presence", "presence", "absence"],
                                 [check["mode"] for check in case["checks"]])
                self.assertTrue(case["checks"][-1]["criterion"].startswith("Does not"))

    def test_no_invented_pass_without_agent_execution(self):
        cat = load_catalog(ROOT / "evals/delivery/cases.json")
        summary = evaluate(cat, {"version": 1, "assessments": []}, ROOT / "evals/delivery")
        self.assertEqual("INCOMPLETE", summary["status"])
        self.assertEqual(47, summary["incomplete"])


if __name__ == "__main__":
    unittest.main()
