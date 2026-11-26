"""Routing and Delivery regression catalog coverage for refactoring.

The catalogs require observed host runs; static checks are not execution proof.
"""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


class RefactoringRoutingPolicyTests(unittest.TestCase):
    def test_standalone_refactoring_is_explicit_implementation_intent(self):
        command = read("contexts/implementation/commands/implement-slice.md")
        agent = read("contexts/implementation/agents/implementation-engineer.md")
        self.assertIn("structural refactoring", command)
        self.assertIn("rather than inventing a TDD RED", command)
        self.assertIn("standalone structural refactoring", agent)
        self.assertIn("without fabricating RED", agent)

    def test_routing_separates_design_review_and_implementation(self):
        cases = {c["id"]: c for c in json.loads(read("evals/routing/cases.json"))["cases"]}
        expected = {
            "command-refactor-standalone": "implement-slice",
            "command-refactor-review-only": "review-code",
            "command-refactor-design-only": "design-solution",
            "command-refactor-requirements-only": "specify-and-plan-change",
            "command-refactor-end-to-end": "deliver-change",
        }
        for case_id, target in expected.items():
            with self.subTest(case=case_id):
                self.assertEqual([target], cases[case_id]["expected"])
                self.assertEqual("explicit", cases[case_id]["mode"])
        self.assertIn("test-driven-development",
                      cases["skill-refactor-structural-no-red"]["forbidden"])

    def test_delivery_pilots_are_evidence_based(self):
        cases = {c["id"]: c for c in json.loads(read("evals/delivery/cases.json"))["cases"]}
        for n in range(52, 56):
            with self.subTest(case=n):
                case = cases[f"DL-{n}"]
                self.assertEqual(["presence", "presence", "absence"],
                                 [check["mode"] for check in case["checks"]])
                self.assertTrue(case["checks"][-1]["criterion"].startswith("Does not"))
        delivery = read("contexts/delivery/skills/coordinate-delivery/SKILL.md")
        self.assertIn("standalone refactoring initiative", delivery)
        self.assertIn("do not require an invented RED".lower(), delivery.lower())


if __name__ == "__main__":
    unittest.main()
