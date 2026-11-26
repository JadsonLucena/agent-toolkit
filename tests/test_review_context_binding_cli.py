"""Execute the Review prepare/validate contract in separate OS processes.

These tests exercise the reference adapter's binding, not host authorization
or authentication of a receipt held by a compromised orchestrator.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "adapters" / "review" / "run_review.py"


def git(repo: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", *args], cwd=repo, stderr=subprocess.DEVNULL
    ).decode("utf-8").strip()


class CrossProcessReviewBindingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)
        self.repo = self.home / "repo"
        self.repo.mkdir()
        git(self.repo, "init", "-q")
        git(self.repo, "config", "user.name", "Fixture")
        git(self.repo, "config", "user.email", "fixture@example.invalid")
        (self.repo / "service.py").write_text("value = 1\n", encoding="utf-8")
        git(self.repo, "add", ".")
        git(self.repo, "commit", "-qm", "base")
        self.base = git(self.repo, "rev-parse", "HEAD")
        git(self.repo, "checkout", "-qb", "change")
        (self.repo / "service.py").write_text("value = 2\n", encoding="utf-8")
        git(self.repo, "add", ".")
        git(self.repo, "commit", "-qm", "change")
        self.head = git(self.repo, "rev-parse", "HEAD")
        self.context_file = self.home / "context.json"
        self.evidence_file = self.home / "evidence.json"

    def call(self, *arguments: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(RUNNER), "--repo", str(self.repo), *arguments],
            cwd=self.repo, capture_output=True, text=True, timeout=30,
            check=False,
        )

    def prepare(self):
        process = self.call(
            "--no-ocr", "--from", self.base, "--to", self.head,
            "--risk-profile", "R3", "--concern", "security",
            "--prepare-only", "--out", str(self.context_file),
        )
        self.assertEqual(0, process.returncode, process.stderr + process.stdout)
        receipt = json.loads(process.stdout)
        context = json.loads(self.context_file.read_text(encoding="utf-8"))
        self.assertEqual(64, len(receipt["context_sha256"]))
        self.assertNotIn("context_sha256", context)
        return context, receipt["context_sha256"]

    def evidence(self, context):
        proof = {
            "review_status": "PASS", "review_profile": "advisory",
            "target": context["target"],
            "changed_files": context["changed_files"],
            "reviewed_files": context["changed_files"],
            "unreviewed_files": [], "coverage_status": "complete",
            "blocking_findings": [], "unresolved_questions": [],
            "review_id": context["team_plan"]["review_id"],
            "risk_profile": "R3", "execution_mode": "native-solo",
            "independent_verification": {
                "mode": "native-second-pass",
                "source_evidence": "Service source and changed test assertions independently reread",
            },
        }
        self.evidence_file.write_text(json.dumps(proof), encoding="utf-8")

    def validate(self, receipt: str | None):
        args = [
            "--validate-evidence", str(self.evidence_file),
            "--context", str(self.context_file),
        ]
        if receipt is not None:
            args += ["--expected-context-sha256", receipt]
        return self.call(*args)

    def test_valid_receipt_accepts_native_r3_review(self):
        context, trusted_receipt = self.prepare()
        self.evidence(context)
        result = self.validate(trusted_receipt)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        outcome = json.loads(result.stdout)
        self.assertEqual("PASS", outcome["review_status"])
        self.assertEqual(trusted_receipt, outcome["review_evidence"]["context_sha256"])

    def test_no_trusted_receipt_refuses_validation(self):
        context, _ = self.prepare()
        self.evidence(context)
        outcome = self.validate(None)
        self.assertEqual(2, outcome.returncode)
        self.assertIn("--expected-context-sha256", outcome.stderr)

    def test_erased_team_plan_cannot_downgrade_risk(self):
        context, trusted_receipt = self.prepare()
        self.evidence(context)
        context.pop("team_plan")
        self.context_file.write_text(json.dumps(context), encoding="utf-8")
        outcome = self.validate(trusted_receipt)
        self.assertEqual(2, outcome.returncode)
        self.assertIn("digest mismatch", json.loads(outcome.stdout)["reason"])

    def test_same_git_diff_but_new_execution_invalidates_old_receipt(self):
        context, old_receipt = self.prepare()
        second_context, new_receipt = self.prepare()
        self.assertEqual(context["changed_files"], second_context["changed_files"])
        self.assertNotEqual(old_receipt, new_receipt)
        self.evidence(second_context)
        outcome = self.validate(old_receipt)
        self.assertEqual(2, outcome.returncode)
        self.assertIn("digest mismatch", json.loads(outcome.stdout)["reason"])

    def test_malformed_receipt_fails_closed(self):
        context, _ = self.prepare()
        self.evidence(context)
        outcome = self.validate("not-a-valid-sha256")
        self.assertEqual(2, outcome.returncode)
        self.assertIn("trusted expected context digest", json.loads(outcome.stdout)["reason"])


if __name__ == "__main__":
    unittest.main()
