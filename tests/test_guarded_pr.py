"""Behavioral tests for the actual, fail-closed GitHub PR creation preflight."""
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
sys.path.insert(0, str(ROOT / "adapters" / "github"))
import guarded_pr as gate  # noqa: E402


def git(cwd: Path, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=cwd, stderr=subprocess.DEVNULL).decode().strip()


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
        self.paths = ["app.py", "test_app.py"]
        self.evidence = self.root / "review.json"
        self.checks = self.root / "checks.json"
        self.body = self.root / "pr.md"
        self.body.write_text("# PR\n")
        self.write_evidence()
        self.write_checks()

    def write_evidence(self, **changes):
        value = {
            "review_status": "PASS", "coverage_status": "complete",
            "reviewer": "independent-reviewer-session-123",
            "reviewer_independent": True,
            "target": {"base_sha": self.base, "head_sha": self.head},
            "changed_files": self.paths,
            "reviewed_files": self.paths,
            "unreviewed_files": [], "blocking_findings": [], "unresolved_questions": [],
        }
        value.update(changes)
        self.evidence.write_text(json.dumps(value))

    def write_checks(self, fail: str | None = None):
        def cmd(name: str):
            script = "import sys;sys.exit(1)" if fail == name else "print('ok')"
            return [sys.executable, "-c", script]
        self.checks.write_text(json.dumps({"checks": {"lint": cmd("lint"), "tests": cmd("tests")}}))

    def preflight(self):
        return gate.guard(self.repo, "main", "feature", self.evidence, self.checks)

    def test_repository_check_manifest_matches_ci_commands(self):
        checks = gate.read_checks(ROOT / ".github" / "toolkit-pr-checks.json")
        workflow = (ROOT / ".github" / "workflows" / "toolkit-validation.yml").read_text()
        self.assertEqual({"lint", "tests"}, set(checks))
        for argv in checks.values():
            self.assertIn(" ".join(argv), workflow)

    def test_runs_actual_checks_and_accepts_complete_evidence(self):
        result = self.preflight()
        self.assertEqual(self.head, result["head_sha"])
        self.assertEqual({"lint", "tests"}, set(result["checks_passed"]))
        self.assertEqual(self.paths, result["changed_files"])

    def test_incomplete_review_is_blocked(self):
        self.write_evidence(review_status="INCOMPLETE")
        with self.assertRaisesRegex(gate.GateError, "not PASS"):
            self.preflight()

    def test_self_review_cannot_qualify(self):
        self.write_evidence(reviewer_independent=False)
        with self.assertRaisesRegex(gate.GateError, "independent-review"):
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

    def test_unresolved_issue_is_blocked(self):
        self.write_evidence(unresolved_questions=["unresolved financial integrity"])
        with self.assertRaisesRegex(gate.GateError, "unresolved"):
            self.preflight()

    def test_missing_required_check_is_blocked(self):
        self.checks.write_text(json.dumps({"checks": {"lint": [sys.executable, "-c", "pass"]}}))
        with self.assertRaisesRegex(gate.GateError, "lint and tests"):
            self.preflight()

    def test_failed_lint_blocks(self):
        self.write_checks(fail="lint")
        with self.assertRaisesRegex(gate.GateError, "failed"):
            self.preflight()

    def test_failed_tests_block(self):
        self.write_checks(fail="tests")
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
        with self.assertRaisesRegex(gate.GateError, "published remote"):
            self.preflight()

    def test_real_creation_only_after_preflight_and_explicit_create(self):
        seen = []
        original = gate.invoke

        def intercepted(argv, cwd, timeout=300):
            if argv[0] == "gh":
                seen.append(argv)
                return "https://github.com/org/repo/pull/99"
            return original(argv, cwd, timeout)

        with patch.object(gate, "invoke", side_effect=intercepted):
            stream = io.StringIO()
            with contextlib.redirect_stdout(stream):
                rc = gate.main([
                    "--repo", str(self.repo), "--base", "main", "--head", "feature",
                    "--evidence", str(self.evidence), "--checks-file", str(self.checks),
                    "--create", "--title", "Add feature", "--body-file", str(self.body),
                ])
            self.assertEqual(0, rc)
            self.assertEqual("gh", seen[0][0])
            self.assertEqual("https://github.com/org/repo/pull/99",
                             json.loads(stream.getvalue())["created_pr_url"])

    def test_failed_preflight_never_calls_gh(self):
        self.write_checks(fail="tests")
        seen = []
        original = gate.invoke

        def intercepted(argv, cwd, timeout=300):
            if argv[0] == "gh":
                seen.append(argv)
                return "should-not-happen"
            return original(argv, cwd, timeout)

        with patch.object(gate, "invoke", side_effect=intercepted):
            stream = io.StringIO()
            with contextlib.redirect_stdout(stream):
                rc = gate.main([
                    "--repo", str(self.repo), "--base", "main", "--head", "feature",
                    "--evidence", str(self.evidence), "--checks-file", str(self.checks),
                    "--create", "--title", "Add feature", "--body-file", str(self.body),
                ])
            self.assertEqual(2, rc)
            self.assertEqual([], seen)
            self.assertEqual("blocked", json.loads(stream.getvalue())["status"])


if __name__ == "__main__":
    unittest.main()
