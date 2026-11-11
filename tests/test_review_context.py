"""Acceptance tests for the review-context bridge and optional OCR invocation."""
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
import git_scope  # noqa: E402
import prepare_context as review  # noqa: E402


def git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=repo, stderr=subprocess.DEVNULL).decode().strip()


class ReviewContextTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name) / "repo"
        self.repo.mkdir()
        git(self.repo, "init", "-q")
        git(self.repo, "config", "user.name", "Test")
        git(self.repo, "config", "user.email", "test@example.invalid")
        (self.repo / "src.py").write_text("data=1\n")
        git(self.repo, "add", ".")
        git(self.repo, "commit", "-q", "-m", "base")
        self.base = git(self.repo, "rev-parse", "HEAD")
        (self.repo / "src.py").write_text("data=2\n")
        (self.repo / "tests.py").write_text("assert 2 == 2\n")
        git(self.repo, "add", ".")
        git(self.repo, "commit", "-q", "-m", "head")
        self.head = git(self.repo, "rev-parse", "HEAD")

    def test_native_context_keeps_all_files_and_no_approval(self):
        # An unavailable OCR Python module must not affect native-only mode.
        with patch.dict(sys.modules, {"delegate": None}):
            with patch.object(review, "ocr_adapter", side_effect=AssertionError("OCR must not run")) as mock:
                got = review.prepare_context(self.repo, base=self.base, head=self.head, allow_ocr=False)
        mock.assert_not_called()
        self.assertEqual(["src.py", "tests.py"], got["review_required_files"])
        self.assertEqual("disabled", got["optional_helpers"]["ocr"]["status"])
        self.assertEqual(self.head, got["target"]["head_sha"])
        self.assertIsNone(got["review_verdict"])
        self.assertFalse(got["review_performed"])

    def test_automatic_optional_ocr_discovery_wires_into_review_context(self):
        with patch.object(review, "ocr_adapter", return_value={
            "target": {"head_sha": self.head}, "mode": "range",
            "git_changed_files": ["src.py", "tests.py"],
            "native_review_required_files": ["src.py", "tests.py"],
            "status": "available",
            "ocr_reviewable_files": [{"path": "src.py"}],
            "ocr_excluded_files": [{"path": "tests.py"}],
            "ocr_rule_groups": [{"files": ["src.py"], "rule": "check semantics"}],
            "ocr_unaccounted_files": [], "diagnostics": [],
        }) as mock:
            got = review.prepare_context(self.repo, base=self.base, head=self.head)
        self.assertEqual("ocr", mock.call_args.kwargs["ocr_bin"])
        self.assertEqual("available", got["optional_helpers"]["ocr"]["status"])
        self.assertEqual(["src.py", "tests.py"], got["review_required_files"])
        self.assertFalse(got["review_performed"])

    def test_cli_returns_json_and_no_review(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc = review.main(["--repo", str(self.repo), "--from", self.base, "--to", self.head, "--no-ocr"])
        self.assertEqual(0, rc)
        payload = json.loads(out.getvalue())
        self.assertEqual("review-context", payload["kind"])
        self.assertEqual(2, len(payload["review_required_files"]))

    def test_bad_repo_fails_closed(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc = review.main(["--repo", str(self.repo / "does-not-exist")])
        self.assertEqual(2, rc)
        self.assertEqual("blocked", json.loads(out.getvalue())["status"])


class WorkspaceFingerprintTests(unittest.TestCase):
    def test_dirty_submodule_is_not_a_stable_review_target(self):
        parent, _sub = self._parent_with_submodule()
        (parent / "sub" / "app.py").write_text("v=2\n")
        with self.assertRaisesRegex(git_scope.GitScopeError, "dirty submodule"):
            git_scope.workspace_fingerprint(parent, 30)

    def test_clean_submodule_stays_fingerprintable(self):
        parent, _sub = self._parent_with_submodule()
        first = git_scope.workspace_fingerprint(parent, 30)
        second = git_scope.workspace_fingerprint(parent, 30)
        self.assertEqual(first, second)
        self.assertEqual(64, len(first))

    def _parent_with_submodule(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        sub = root / "sub"
        parent = root / "parent"
        sub.mkdir()
        parent.mkdir()
        git(sub, "init", "-q")
        git(sub, "config", "user.email", "test@example.invalid")
        git(sub, "config", "user.name", "Test")
        (sub / "app.py").write_text("v=1\n")
        git(sub, "add", "app.py")
        git(sub, "commit", "-q", "-m", "sub")
        git(parent, "init", "-q")
        git(parent, "config", "user.email", "test@example.invalid")
        git(parent, "config", "user.name", "Test")
        subprocess.check_call(
            ["git", "-c", "protocol.file.allow=always", "submodule", "add", "-q", str(sub), "sub"],
            cwd=parent, stdout=subprocess.DEVNULL,
        )
        git(parent, "commit", "-q", "-m", "add sub")
        return parent, sub


if __name__ == "__main__":
    unittest.main()
