"""Regression tests for routing-catalog validity and runtime-event scoring."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from routing_evals import (  # noqa: E402
    capability_inventory,
    make_template,
    score_observations,
    validate_catalog,
)


class RoutingEvalsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inventory = capability_inventory(ROOT)

    def case(self, **changes):
        case = {
            "id": "skill-example-positive",
            "kind": "skill",
            "mode": "implicit",
            "prompt": "Review these examples for requirements readiness without editing any files.",
            "expected": ["requirements-validation"],
            "forbidden": ["requirements-definition"],
        }
        case.update(changes)
        return case

    def observations(self, results, **overrides):
        data = {
            "schema_version": 1,
            "host": "cursor",
            "host_version": "3.29.15",
            "plugin_revision": "0123456789abcdef",
            "results": results,
        }
        data.update(overrides)
        return data

    def event(self, name, kind="skill"):
        return {
            "kind": kind,
            "name": name,
            "action": "activated",
            "origin": "host",
            "evidence_ref": "log:test-event-1",
        }

    def test_inventory_has_specific_requirement_skill_names(self):
        skills = self.inventory["skill"]
        self.assertIn("requirements-definition", skills)
        self.assertIn("requirements-validation", skills)
        self.assertNotIn("definition", skills)
        self.assertNotIn("validation", skills)

    def test_catalog_validity(self):
        import json
        catalog = json.loads((ROOT / "evals/routing/cases.json").read_text(encoding="utf-8"))
        self.assertEqual([], validate_catalog(catalog, self.inventory))
        self.assertGreaterEqual(len(catalog["cases"]), 40)
        self.assertEqual({"skill", "agent", "command", "rule"}, {c["kind"] for c in catalog["cases"]})
        self.assertTrue(any(not c["expected"] for c in catalog["cases"]))

    def test_rejects_unknown_capability(self):
        catalog = {"schema_version": 1, "cases": [self.case(expected=["not-a-real-skill"])]}
        self.assertIn("unknown skill expected", " ".join(validate_catalog(catalog, self.inventory)))

    def test_rejects_overlapping_expected_and_forbidden(self):
        catalog = {"schema_version": 1, "cases": [self.case(forbidden=["requirements-validation"])]}
        self.assertIn("overlap", " ".join(validate_catalog(catalog, self.inventory)))

    def test_command_must_be_explicit_when_expected(self):
        catalog = {"schema_version": 1, "cases": [
            self.case(kind="command", expected=["review-code"], forbidden=[], mode="implicit")
        ]}
        self.assertIn("Commands must use explicit", " ".join(validate_catalog(catalog, self.inventory)))

    def test_positive_activation_passes_with_real_host_reference_field(self):
        case = self.case()
        report = score_observations([case], self.observations([{
            "id": case["id"], "status": "observed",
            "events": [self.event("requirements-validation")]
        }]))
        self.assertEqual("PASS", report["status"])
        self.assertEqual(1.0, report["precision"])
        self.assertEqual(1.0, report["recall"])

    def test_missing_expected_and_unexpected_activation_fail(self):
        case = self.case()
        report = score_observations([case], self.observations([{
            "id": case["id"], "status": "observed",
            "events": [self.event("requirements-definition")]
        }]))
        self.assertEqual("FAIL", report["status"])
        self.assertEqual(1, report["false_positives"])
        self.assertEqual(1, report["false_negatives"])
        self.assertEqual(1, report["forbidden_activations"])

    def test_negative_no_activation_passes_if_actually_observed(self):
        case = self.case(expected=[], forbidden=["requirements-definition"])
        report = score_observations([case], self.observations([{
            "id": case["id"], "status": "observed", "events": []
        }]))
        self.assertEqual("PASS", report["status"])
        self.assertIsNone(report["precision"])
        self.assertIsNone(report["recall"])

    def test_not_run_and_unsupported_never_pass(self):
        cases = [self.case(id="skill-one"), self.case(id="skill-two")]
        report = score_observations(cases, self.observations([
            {"id": "skill-one", "status": "not-run", "events": []},
            {"id": "skill-two", "status": "unsupported", "events": []},
        ]))
        self.assertEqual("INCOMPLETE", report["status"])
        self.assertEqual(0, report["measured_cases"])
        self.assertEqual(1, report["unsupported_cases"])

    def test_model_self_report_is_not_host_evidence(self):
        case = self.case()
        bad = self.event("requirements-validation")
        bad["origin"] = "model"
        with self.assertRaisesRegex(ValueError, "host event"):
            score_observations([case], self.observations([{
                "id": case["id"], "status": "observed", "events": [bad]
            }]))

    def test_missing_evidence_ref_rejected(self):
        case = self.case()
        bad = self.event("requirements-validation")
        bad["evidence_ref"] = ""
        with self.assertRaisesRegex(ValueError, "evidence_ref"):
            score_observations([case], self.observations([{
                "id": case["id"], "status": "observed", "events": [bad]
            }]))

    def test_no_host_revision_cannot_pass(self):
        with self.assertRaisesRegex(ValueError, "plugin_revision"):
            score_observations([self.case()], self.observations([], plugin_revision="not-installed"))

    def test_unmeasured_cases_cannot_claim_events(self):
        with self.assertRaisesRegex(ValueError, "cannot contain activation events"):
            score_observations([self.case()], self.observations([{
                "id": "skill-example-positive", "status": "not-run",
                "events": [self.event("requirements-validation")]
            }]))

    def test_measured_route_requires_host_version(self):
        case = self.case()
        result = {
            "id": case["id"], "status": "observed",
            "events": [self.event("requirements-validation")],
        }
        with self.assertRaisesRegex(ValueError, "host_version"):
            score_observations([case], self.observations([result], host_version="not-recorded"))

    def test_report_includes_coverage_and_true_negatives(self):
        case = self.case(expected=[], forbidden=["requirements-definition"])
        report = score_observations([case], self.observations([{
            "id": case["id"], "status": "observed", "events": []
        }]))
        self.assertEqual(1.0, report["coverage"])
        self.assertEqual(1, report["true_negative_cases"])
        self.assertEqual("3.29.15", report["host_version"])

    def test_template_is_not_run(self):
        case = self.case()
        template = make_template([case], "cursor", "abc")
        self.assertEqual("not-run", template["results"][0]["status"])
        report = score_observations([case], template)
        self.assertEqual("INCOMPLETE", report["status"])
        self.assertEqual(0, report["measured_cases"])


if __name__ == "__main__":
    unittest.main()
