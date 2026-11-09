"""Portable Review acceptance tests (host-agent and subprocess adapters)."""
from __future__ import annotations
import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "adapters" / "review"))
import run_review  # noqa: E402
from prepare_context import prepare_context  # noqa: E402
from team_orchestration import (
    freeze, TeamPlanningError, _validate_finding, _validate_verified_finding,
)  # noqa: E402


def git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=repo, stderr=subprocess.DEVNULL).decode().strip()


class PortableReviewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        git(self.repo, "init", "-q")
        git(self.repo, "config", "user.name", "test")
        git(self.repo, "config", "user.email", "test@example.invalid")
        (self.repo / "service.py").write_text("value=1\n")
        git(self.repo, "add", ".")
        git(self.repo, "commit", "-q", "-m", "base")
        git(self.repo, "branch", "-m", "main")
        self.base = git(self.repo, "rev-parse", "HEAD")
        git(self.repo, "checkout", "-q", "-b", "feature")
        (self.repo / "service.py").write_text("value=2\n")
        (self.repo / "test_service.py").write_text("assert 2 == 2\n")
        git(self.repo, "add", ".")
        git(self.repo, "commit", "-q", "-m", "change")
        self.head = git(self.repo, "rev-parse", "HEAD")
        self.context_path = self.root / "context.json"
        self.evidence_path = self.root / "evidence.json"

    def call(self, *args):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = run_review.main(["--repo", str(self.repo), *args])
        return code, json.loads(stdout.getvalue())

    def prepare(self, *args):
        code, output = self.call(
            "--no-ocr", "--from", self.base, "--to", self.head,
            *args, "--prepare-only", "--out", str(self.context_path),
        )
        self.assertEqual(0, code, output)
        return json.loads(self.context_path.read_text())

    @staticmethod
    def valid_evidence(context):
        return {
            "review_status": "PASS", "target": context["target"],
            "changed_files": context["changed_files"],
            "reviewed_files": context["changed_files"],
            "unreviewed_files": [], "coverage_status": "complete",
            "blocking_findings": [], "unresolved_questions": [],
        }

    def validate(self, evidence, context_path=None):
        self.evidence_path.write_text(json.dumps(evidence))
        return self.call(
            "--validate-evidence", str(self.evidence_path),
            "--context", str(context_path or self.context_path),
        )

    def test_two_phase_preparation_and_validation(self):
        context = self.prepare()
        code, result = self.validate(self.valid_evidence(context))
        self.assertEqual(0, code, result)
        self.assertEqual("PASS", result["review_status"])

    def test_two_phase_wrong_head_is_blocked(self):
        context = self.prepare()
        evidence = self.valid_evidence(context)
        evidence["target"] = {**context["target"], "head_sha": "0" * 40}
        code, result = self.validate(evidence)
        self.assertEqual(2, code, result)
        self.assertIn("different", result["reason"])

    def test_two_phase_partial_coverage_is_blocked(self):
        context = self.prepare()
        evidence = self.valid_evidence(context)
        evidence["reviewed_files"] = ["service.py"]
        code, result = self.validate(evidence)
        self.assertEqual(2, code, result)
        self.assertIn("coverage", result["reason"].lower())

    def test_two_phase_stale_workspace_is_blocked(self):
        code, _ = self.call("--no-ocr", "--prepare-only", "--out", str(self.context_path))
        self.assertEqual(0, code)
        context = json.loads(self.context_path.read_text())
        (self.repo / "untracked.txt").write_text("new\n")
        code, result = self.validate(self.valid_evidence(context))
        self.assertEqual(2, code, result)
        self.assertIn("changed", result["reason"])

    def test_preparation_must_store_context_outside_repository(self):
        code, result = self.call(
            "--no-ocr", "--prepare-only", "--out", str(self.repo / "context.json"),
        )
        self.assertEqual(2, code, result)
        self.assertIn("outside", result["reason"])

    def test_base_branch_warns_when_cached_remote_ref_differs(self):
        git(self.repo, "update-ref", "refs/remotes/origin/main", self.head)
        context = prepare_context(self.repo, base_branch="main", allow_ocr=False)
        self.assertEqual(self.base, context["target"]["base_branch_resolved_sha"])
        self.assertTrue(context["warnings"])
        remote = prepare_context(self.repo, base_branch="origin/main", allow_ocr=False)
        self.assertEqual(self.head, remote["target"]["base_branch_resolved_sha"])
        self.assertEqual([], remote["changed_files"])

    def test_small_r3_can_use_one_distinct_concern_with_verifier(self):
        context = prepare_context(self.repo, base=self.base, head=self.head, allow_ocr=False)
        plan = freeze(
            context, self.repo, risk_profile="R3", concerns=["spec"],
            task_available=True, isolated_tasks=True,
        )
        self.assertEqual(["specification-reviewer"], plan["selected_roles"])
        self.assertTrue(plan["n_justification"]["below_ideal_range"])
        self.assertTrue(plan["verifier_required"])

    def test_invalid_concern_names_list_allowed_values(self):
        context = prepare_context(self.repo, base=self.base, head=self.head, allow_ocr=False)
        with self.assertRaisesRegex(TeamPlanningError, "contract.*correctness.*security"):
            freeze(
                context, self.repo, risk_profile="R3", concerns=["bogus"],
                task_available=True, isolated_tasks=True,
            )

    def test_verified_blocker_precedes_material_uncertainty(self):
        context = self.prepare()
        evidence = self.valid_evidence(context)
        evidence.update(
            review_status="FAIL",
            blocking_findings=[{"finding_id": "F1", "verification_status": "confirmed"}],
            unresolved_questions=["Unverified external state"],
        )
        code, result = self.validate(evidence)
        self.assertEqual(1, code, result)
        self.assertEqual("FAIL", result["review_status"])

    def test_ocr_exclusions_still_require_native_review(self):
        fake = {
            "status": "available", "target": {},
            "git_changed_files": [], "native_review_required_files": [],
            "ocr_reviewable_files": [{"path": "service.py"}],
            "ocr_excluded_files": [{"path": "test_service.py", "exclude_reason": "default_path"}],
            "ocr_rule_groups": [{"source": "system", "rule": "React defaults"}],
            "ocr_unaccounted_files": [], "diagnostics": [],
        }
        with patch("prepare_context.ocr_adapter", return_value=fake):
            context = prepare_context(self.repo, base=self.base, head=self.head)
        self.assertEqual(["service.py", "test_service.py"], context["review_required_files"])
        self.assertEqual(
            "test_service.py", context["helper_excluded_requires_native_review"][0]["path"],
        )
        self.assertFalse(context["optional_helpers"]["ocr"]["rule_groups"][0]["binding"])

    def test_specialist_finding_must_be_self_contained(self):
        finding = {
            "finding_id": "F1", "location": "service.py:1",
            "claim": "See previous message", "trigger": "charge",
            "evidence": "service.py:1", "consequence": "duplicate",
            "severity": "high", "confidence": "high",
        }
        with self.assertRaisesRegex(TeamPlanningError, "self-contained"):
            _validate_finding(finding, {"service.py"})

    def test_verifier_must_independently_cite_source(self):
        with self.assertRaisesRegex(TeamPlanningError, "self-contained"):
            _validate_verified_finding({
                "finding_id": "F1", "verification_status": "confirmed",
                "location": "service.py:1",
                "source_evidence": "See previous message",
            }, {"F1"})

    def test_human_output_language_propagates(self):
        context = prepare_context(self.repo, allow_ocr=False, output_language="pt-BR")
        self.assertEqual("pt-BR", context["output_language"])
        plan = freeze(
            context, self.repo, risk_profile="R3", concerns=["security"],
            task_available=True, isolated_tasks=True,
        )
        self.assertEqual("pt-BR", plan["output_language"])


if __name__ == "__main__":
    unittest.main()
