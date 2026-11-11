"""Integration tests for signed, trusted GitHub PR preflight and remote verification."""
from __future__ import annotations

import contextlib
import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "adapters" / "github"))
import guarded_pr as gate  # noqa: E402


class BodyClaimTests(unittest.TestCase):
    def test_negation_in_an_earlier_clause_does_not_cancel_a_later_pass(self):
        self.assertTrue(gate.body_claims_gate_pass("Signed gate evidence is absent.\nGate: PASS\n"))
        self.assertTrue(gate.body_claims_gate_pass("No remaining implementation work. Gate: PASS"))

    def test_negation_in_the_same_clause_cancels_pass(self):
        self.assertFalse(gate.body_claims_gate_pass(
            "This draft does not claim PASS.\nSigned gate evidence is absent.\n"
        ))


def git(cwd: Path, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=cwd, stderr=subprocess.DEVNULL).decode().strip()


@unittest.skipUnless(shutil.which("ssh-keygen"), "OpenSSH ssh-keygen is required for SSHSIG integration tests")
class GuardedPRTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        self.remote = self.root / "remote.git"
        git(self.root, "init", "-q", "--bare", str(self.remote))
        git(self.repo, "init", "-q")
        git(self.repo, "config", "user.name", "Test User")
        git(self.repo, "config", "user.email", "test@example.invalid")
        (self.repo / "app.py").write_text("value = 1\n")
        git(self.repo, "add", "app.py")
        git(self.repo, "commit", "-q", "-m", "base")
        git(self.repo, "branch", "-m", "main")
        git(self.repo, "remote", "add", "origin", str(self.remote))
        git(self.repo, "push", "-q", "origin", "main")
        self.base = git(self.repo, "rev-parse", "HEAD")
        git(self.repo, "checkout", "-q", "-b", "feature")
        (self.repo / "app.py").write_text("value = 2\n")
        (self.repo / "test_app.py").write_text("assert 2 == 2\n")
        git(self.repo, "add", ".")
        git(self.repo, "commit", "-q", "-m", "change")
        git(self.repo, "push", "-q", "origin", "feature")
        self.head = git(self.repo, "rev-parse", "HEAD")
        self.review_paths = ["app.py", "test_app.py"]
        self.reviewer = "reviewer@example.invalid"
        self.evidence = self.root / "review.json"
        self.signature = self.root / "review.json.sig"
        self.check_policy = self.root / "trusted-policy.json"
        self.allowed_signers = self.root / "trusted-signers"
        self.key = self.root / "reviewer-ed25519"
        self.body = self.root / "pr.md"
        self.body.write_text("# PR\n")
        subprocess.run(
            ["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-f", str(self.key)],
            check=True, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        self.allowed_signers.write_text(self.reviewer + " " + (self.root / "reviewer-ed25519.pub").read_text())
        self.write_policy()
        self.write_evidence()

    def write_policy(self, *, fail: str | None = None, **changes):
        def cmd(name: str):
            script = "import sys;sys.exit(1)" if fail == name else "print('ok')"
            return [sys.executable, "-c", script]
        value = {
            "schema_version": 1, "github_repository": "org/repo",
            "remote_url": str(self.remote), "allowed_signers_file": str(self.allowed_signers),
            "reviewers": [self.reviewer],
            "checks": {"lint": cmd("lint"), "tests": cmd("tests")},
        }
        value.update(changes)
        self.check_policy.write_text(json.dumps(value))
        return value

    def write_evidence(self, *, sign=True, **changes):
        value = {
            "repository": "org/repo", "review_profile": "gate", "review_status": "PASS",
            "coverage_status": "complete", "reviewer": self.reviewer,
            "reviewer_independent": True,
            "target": {"base_sha": self.base, "head_sha": self.head},
            "changed_files": self.review_paths, "reviewed_files": self.review_paths,
            "unreviewed_files": [], "blocking_findings": [], "unresolved_questions": [],
        }
        value.update(changes)
        self.evidence.write_text(json.dumps(value, sort_keys=True))
        if sign:
            self.signature.unlink(missing_ok=True)
            subprocess.run(
                ["ssh-keygen", "-Y", "sign", "-f", str(self.key), "-n",
                 gate.SIGNATURE_NAMESPACE, str(self.evidence)],
                check=True, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            )
        return value

    def preflight(self):
        return gate.guard(self.repo, "main", "feature", self.evidence, self.signature, self.check_policy)

    def test_repository_check_manifest_matches_ci_commands(self):
        checks = gate.read_checks(gate.load_json(ROOT / ".github" / "toolkit-pr-checks.json"))
        workflow = (ROOT / ".github" / "workflows" / "toolkit-validation.yml").read_text()
        self.assertEqual({"lint", "tests"}, set(checks))
        for argv in checks.values():
            self.assertIn(" ".join(argv), workflow)

    def test_signed_review_with_trusted_checks_passes(self):
        result = self.preflight()
        self.assertEqual(self.head, result["head_sha"])
        self.assertEqual(self.reviewer, result["reviewer"])
        self.assertTrue(result["signed_review_verified"])
        self.assertEqual({"lint", "tests"}, set(result["checks_passed"]))
        self.assertEqual(self.review_paths, result["changed_files"])

    def test_signed_advisory_pass_never_satisfies_pre_pr_gate(self):
        self.write_evidence(review_profile="advisory")
        with self.assertRaisesRegex(gate.GateError, "gate"):
            self.preflight()

    def test_legacy_missing_profile_never_satisfies_pre_pr_gate(self):
        self.write_evidence(review_profile=None)
        with self.assertRaisesRegex(gate.GateError, "gate"):
            self.preflight()

    def test_nonmaterial_questions_with_explicit_material_false_are_not_gate_blockers(self):
        self.write_evidence(unresolved_questions=[{
            "question": "Noncritical naming preference", "material": False,
        }])
        outcome = self.preflight()
        self.assertEqual(self.head, outcome["head_sha"])

    def test_forged_pass_without_signature_is_blocked(self):
        self.write_evidence(review_status="FAIL", sign=True)
        self.write_evidence(review_status="PASS", sign=False)
        with self.assertRaisesRegex(gate.GateError, "signature"):
            self.preflight()

    def test_signature_of_different_ssh_key_is_blocked(self):
        other = self.root / "attacker"
        subprocess.run(
            ["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-f", str(other)],
            check=True, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        self.signature.unlink(missing_ok=True)
        subprocess.run(
            ["ssh-keygen", "-Y", "sign", "-f", str(other), "-n",
             gate.SIGNATURE_NAMESPACE, str(self.evidence)],
            check=True, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        with self.assertRaisesRegex(gate.GateError, "signature"):
            self.preflight()

    def test_incomplete_review_is_blocked(self):
        self.write_evidence(review_status="INCOMPLETE")
        with self.assertRaisesRegex(gate.GateError, "not PASS"):
            self.preflight()

    def test_self_attestation_flag_false_is_blocked(self):
        self.write_evidence(reviewer_independent=False)
        with self.assertRaisesRegex(gate.GateError, "independent-review"):
            self.preflight()

    def test_reviewer_cannot_match_commit_author(self):
        self.allowed_signers.write_text(
            self.allowed_signers.read_text() + "test@example.invalid " +
            (self.root / "reviewer-ed25519.pub").read_text()
        )
        self.write_policy(reviewers=[self.reviewer, "test@example.invalid"])
        self.write_evidence(reviewer="test@example.invalid")
        with self.assertRaisesRegex(gate.GateError, "also a change author"):
            self.preflight()

    def test_stale_sha_is_blocked(self):
        self.write_evidence(target={"base_sha": self.base, "head_sha": self.base})
        with self.assertRaisesRegex(gate.GateError, "another head/base"):
            self.preflight()

    def test_partial_coverage_is_blocked(self):
        self.write_evidence(reviewed_files=["app.py"])
        with self.assertRaisesRegex(gate.GateError, "coverage does not match"):
            self.preflight()

    def test_unreported_change_is_blocked(self):
        self.write_evidence(changed_files=["app.py"])
        with self.assertRaisesRegex(gate.GateError, "coverage does not match"):
            self.preflight()

    def test_material_unresolved_issue_is_blocked(self):
        self.write_evidence(unresolved_questions=["unresolved financial integrity"])
        with self.assertRaisesRegex(gate.GateError, "unresolved"):
            self.preflight()

    def test_missing_trusted_required_check_is_blocked(self):
        self.write_policy(checks={"lint": [sys.executable, "-c", "pass"]})
        with self.assertRaisesRegex(gate.GateError, "lint and tests"):
            self.preflight()

    def test_changed_repository_manifest_cannot_weaken_checks(self):
        (self.repo / ".github").mkdir()
        (self.repo / ".github" / "toolkit-pr-checks.json").write_text(
            json.dumps({"checks": {"lint": ["true"], "tests": ["true"]}})
        )
        with self.assertRaisesRegex(gate.GateError, "differs from protected"):
            self.preflight()

    def test_trust_policy_cannot_be_provided_inside_repo(self):
        local = self.repo / "untrusted.json"
        local.write_text(self.check_policy.read_text())
        with self.assertRaisesRegex(gate.GateError, "outside the target"):
            gate.guard(self.repo, "main", "feature", self.evidence, self.signature, local)

    def test_failed_lint_blocks(self):
        self.write_policy(fail="lint")
        with self.assertRaisesRegex(gate.GateError, "failed"):
            self.preflight()

    def test_failed_tests_block(self):
        self.write_policy(fail="tests")
        with self.assertRaisesRegex(gate.GateError, "failed"):
            self.preflight()

    def test_dirty_worktree_blocks(self):
        (self.repo / "untracked.txt").write_text("new")
        with self.assertRaisesRegex(gate.GateError, "dirty"):
            self.preflight()

    def test_remote_base_mismatch_blocks(self):
        git(self.remote, "update-ref", "refs/heads/main", self.head)
        with self.assertRaisesRegex(gate.GateError, "remote base"):
            self.preflight()

    def test_unpublished_head_blocks(self):
        (self.repo / "app.py").write_text("value = 3\n")
        git(self.repo, "add", ".")
        git(self.repo, "commit", "-q", "-m", "unpublished")
        with self.assertRaisesRegex(gate.GateError, "remote head"):
            self.preflight()

    def gh_mock(self, *, wrong_head=False, wrong_draft=False, commands=None):
        seen = []
        original = gate.invoke

        def intercepted(argv, cwd, timeout=300):
            if argv[:3] == ["gh", "pr", "create"]:
                seen.append("create")
                if commands is not None:
                    commands.append(argv)
                return "https://github.com/org/repo/pull/99"
            if argv[:2] == ["gh", "api"]:
                seen.append("verify")
                return json.dumps({
                    "number": 99, "html_url": "https://github.com/org/repo/pull/99",
                    "state": "open", "draft": wrong_draft, "title": "Add feature",
                    "base": {"sha": self.base, "ref": "main",
                             "repo": {"full_name": "org/repo"}},
                    "head": {"sha": self.base if wrong_head else self.head,
                             "ref": "feature", "repo": {"full_name": "org/repo"}},
                })
            return original(argv, cwd, timeout)
        return seen, intercepted

    def cli(self, *extra):
        return [
            "--repo", str(self.repo), "--base", "main", "--head", "feature",
            "--evidence", str(self.evidence), "--signature", str(self.signature),
            "--trust-policy", str(self.check_policy), *extra,
        ]

    def test_remote_creation_requires_verification(self):
        seen, mock = self.gh_mock()
        with patch.object(gate, "invoke", side_effect=mock):
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                rc = gate.main(self.cli("--create", "--title", "Add feature",
                                        "--body-file", str(self.body)))
        self.assertEqual(0, rc)
        self.assertEqual(["create", "verify"], seen)
        result = json.loads(out.getvalue())
        self.assertEqual("passed", result["status"])
        self.assertTrue(result["remote_verified"])
        self.assertEqual(99, result["pr_number"])

    def test_wrong_remote_pr_sha_is_created_unverified(self):
        seen, mock = self.gh_mock(wrong_head=True)
        with patch.object(gate, "invoke", side_effect=mock):
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                rc = gate.main(self.cli("--create", "--title", "Add feature",
                                        "--body-file", str(self.body)))
        self.assertEqual(3, rc)
        self.assertEqual(["create", "verify"], seen)
        self.assertEqual("created_unverified", json.loads(out.getvalue())["status"])

    def test_wrong_remote_draft_is_created_unverified(self):
        seen, mock = self.gh_mock(wrong_draft=True)
        with patch.object(gate, "invoke", side_effect=mock):
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                rc = gate.main(self.cli("--create", "--title", "Add feature",
                                        "--body-file", str(self.body)))
        self.assertEqual(3, rc)
        self.assertEqual("created_unverified", json.loads(out.getvalue())["status"])

    def test_blocked_preflight_never_calls_github(self):
        self.write_policy(fail="tests")
        seen, mock = self.gh_mock()
        with patch.object(gate, "invoke", side_effect=mock):
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                rc = gate.main(self.cli("--create", "--title", "Add feature",
                                        "--body-file", str(self.body)))
        self.assertEqual(2, rc)
        self.assertEqual([], seen)
        self.assertEqual("blocked", json.loads(out.getvalue())["status"])

    def run_cli(self, argv, mock):
        out = io.StringIO()
        with patch.object(gate, "invoke", side_effect=mock):
            with contextlib.redirect_stdout(out):
                rc = gate.main(argv)
        return rc, out.getvalue()

    def unsigned_draft_cli(self, *extra):
        return [
            "--repo", str(self.repo), "--base", "main", "--head", "feature",
            "--trust-policy", str(self.check_policy), "--draft", *extra,
        ]

    def test_unsigned_draft_creates_without_gate_evidence(self):
        self.body.write_text("Signed gate evidence is absent.\n")
        commands = []
        seen, mock = self.gh_mock(wrong_draft=True, commands=commands)
        rc, raw = self.run_cli(self.unsigned_draft_cli(
            "--create", "--title", "Add feature", "--body-file", str(self.body),
        ), mock)
        result = json.loads(raw)
        self.assertEqual(0, rc)
        self.assertEqual(["create", "verify"], seen)
        self.assertIn("--draft", commands[0])
        self.assertNotIn("--evidence", commands[0])
        self.assertFalse(result["signed_review_verified"])
        self.assertEqual({"lint", "tests"}, set(result["checks_passed"]))
        self.assertTrue(result["remote_verified"])

    def test_unsigned_draft_refuses_body_that_affirms_pass(self):
        self.body.write_text("independent code review (PASS)\n")
        seen, mock = self.gh_mock(wrong_draft=True)
        rc, raw = self.run_cli(self.unsigned_draft_cli(
            "--create", "--title", "Add feature", "--body-file", str(self.body),
        ), mock)
        self.assertEqual(2, rc)
        self.assertEqual([], seen)
        self.assertIn("affirms", json.loads(raw)["reason"])

    def test_unsigned_draft_refuses_review_profile_gate_in_body(self):
        self.body.write_text("review_profile=gate\n")
        seen, mock = self.gh_mock(wrong_draft=True)
        rc, raw = self.run_cli(self.unsigned_draft_cli(
            "--create", "--title", "Add feature", "--body-file", str(self.body),
        ), mock)
        self.assertEqual(2, rc)
        self.assertEqual([], seen)
        self.assertIn("affirms", json.loads(raw)["reason"])

    def test_negated_pass_token_does_not_block_unsigned_draft(self):
        self.body.write_text("This draft does not claim PASS.\nSigned gate evidence is absent.\n")
        seen, mock = self.gh_mock(wrong_draft=True)
        rc, raw = self.run_cli(self.unsigned_draft_cli(
            "--create", "--title", "Add feature", "--body-file", str(self.body),
        ), mock)
        self.assertEqual(0, rc)
        self.assertEqual(["create", "verify"], seen)
        self.assertFalse(json.loads(raw)["signed_review_verified"])

    def test_ready_creation_without_signature_never_calls_github(self):
        seen, mock = self.gh_mock()
        rc, raw = self.run_cli([
            "--repo", str(self.repo), "--base", "main", "--head", "feature",
            "--trust-policy", str(self.check_policy),
            "--create", "--title", "Add feature", "--body-file", str(self.body),
        ], mock)
        self.assertEqual(2, rc)
        self.assertEqual([], seen)
        self.assertIn("signature", json.loads(raw)["reason"])

    def test_unsigned_draft_rejects_unverified_evidence_file(self):
        seen, mock = self.gh_mock(wrong_draft=True)
        rc, raw = self.run_cli(self.unsigned_draft_cli(
            "--evidence", str(self.evidence),
            "--create", "--title", "Add feature", "--body-file", str(self.body),
        ), mock)
        self.assertEqual(2, rc)
        self.assertEqual([], seen)
        self.assertIn("does not accept", json.loads(raw)["reason"])

    def test_failed_checks_still_block_unsigned_draft(self):
        self.write_policy(fail="tests")
        self.body.write_text("Signed gate evidence is absent.\n")
        seen, mock = self.gh_mock(wrong_draft=True)
        rc, raw = self.run_cli(self.unsigned_draft_cli(
            "--create", "--title", "Add feature", "--body-file", str(self.body),
        ), mock)
        self.assertEqual(2, rc)
        self.assertEqual([], seen)
        self.assertEqual("blocked", json.loads(raw)["status"])

    def test_signed_draft_still_verifies_gate_evidence(self):
        seen, mock = self.gh_mock(wrong_draft=True)
        rc, raw = self.run_cli(self.cli(
            "--draft", "--create", "--title", "Add feature", "--body-file", str(self.body),
        ), mock)
        result = json.loads(raw)
        self.assertEqual(0, rc)
        self.assertEqual(["create", "verify"], seen)
        self.assertTrue(result["signed_review_verified"])


if __name__ == "__main__":
    unittest.main()
