"""Offline contract and fallback tests for the optional OCR delegation adapter."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "adapters" / "ocr"))
from delegate import adapter, main  # noqa: E402


def run_git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=root, stderr=subprocess.DEVNULL).decode().strip()


class OcrAdapterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        run_git(self.repo, "init", "-q")
        run_git(self.repo, "config", "user.name", "Review Test")
        run_git(self.repo, "config", "user.email", "test@example.invalid")
        (self.repo / "src").mkdir()
        (self.repo / "src" / "app.py").write_text("original = True\n")
        (self.repo / "tests").mkdir()
        (self.repo / "tests" / "test_app.py").write_text("assert True\n")
        run_git(self.repo, "add", ".")
        run_git(self.repo, "commit", "-q", "-m", "initial")
        self.base = run_git(self.repo, "rev-parse", "HEAD")
        (self.repo / "src" / "app.py").write_text("original = False\n")
        (self.repo / "tests" / "test_app.py").write_text("assert False\n")
        run_git(self.repo, "add", ".")
        run_git(self.repo, "commit", "-q", "-m", "change")
        self.head = run_git(self.repo, "rev-parse", "HEAD")
        self.bin = self.root / "bin"
        self.bin.mkdir()

    def fake_ocr(self, *, invalid_json=False, unsupported=False, malicious=False, skip_test=False):
        script = self.bin / "ocr"
        preview = {
            "schema_version": "1", "mode": "range", "repository": str(self.repo), "from": self.base, "to": self.head,
            "merge_base": self.base,
            "reviewable_files": [{"path": "src/app.py", "status": "M"}],
            "excluded_files": [] if skip_test else [{"path": "tests/test_app.py", "status": "M", "exclude_reason": "test"}],
        }
        if malicious:
            preview["reviewable_files"][0]["path"] = "../escape.py"
        body = [
            "#!/usr/bin/env python3",
            "import json, sys",
            "args = sys.argv[1:]",
            "if '--format' in args and " + repr(unsupported) + ":",
            "    sys.stderr.write('unknown flag: --format')",
            "    sys.exit(1)",
            "if args[1] == 'preview':",
            "    print(" + ("'not valid json'" if invalid_json else "json.dumps(" + repr(preview) + ")") + ")",
            "elif args[1] == 'rule':",
            "    paths = args[args.index('--repo')+2:]",
            "    print(json.dumps({'schema_version':'1', 'groups':[{'group_id':1,'source':'default','pattern':'*','files': paths, 'rule':'Check errors and invariants.'}]}))",
            "else: sys.exit(2)",
        ]
        script.write_text("\n".join(body) + "\n")
        script.chmod(0o755)
        return str(script)

    def test_without_ocr_native_inventory_remains_required(self):
        got = adapter(repo=self.repo, ocr_bin="intentionally-missing-ocr", from_ref=self.base, to_ref=self.head)
        self.assertEqual("unavailable", got["status"])
        self.assertEqual(["src/app.py", "tests/test_app.py"], got["native_review_required_files"])
        self.assertEqual(got["git_changed_files"], got["ocr_unaccounted_files"])
        self.assertFalse(got["review_performed"])
        self.assertIsNone(got["review_verdict"])

    def test_valid_delegate_preview_preserves_excluded_tests_for_native(self):
        got = adapter(repo=self.repo, ocr_bin=self.fake_ocr(), from_ref=self.base, to_ref=self.head)
        self.assertEqual("available", got["status"], got["diagnostics"])
        self.assertEqual(self.head, got["target"]["head_sha"])
        self.assertEqual(["src/app.py", "tests/test_app.py"], got["native_review_required_files"])
        self.assertEqual(["tests/test_app.py"], [f["path"] for f in got["ocr_excluded_files"]])
        self.assertEqual([], got["ocr_unaccounted_files"])
        self.assertEqual(["src/app.py"], got["ocr_rule_groups"][0]["files"])

    def test_ocr_does_not_account_for_a_file(self):
        got = adapter(repo=self.repo, ocr_bin=self.fake_ocr(skip_test=True), from_ref=self.base, to_ref=self.head)
        self.assertEqual("available", got["status"])
        self.assertEqual(["tests/test_app.py"], got["ocr_unaccounted_files"])
        self.assertIn("tests/test_app.py", got["native_review_required_files"])

    def test_old_ocr_json_incompatible_falls_back(self):
        got = adapter(repo=self.repo, ocr_bin=self.fake_ocr(unsupported=True), from_ref=self.base, to_ref=self.head)
        self.assertEqual("unsupported", got["status"])
        self.assertEqual(2, len(got["native_review_required_files"]))
        self.assertFalse(got["review_performed"])

    def test_invalid_json_never_becomes_valid_review(self):
        got = adapter(repo=self.repo, ocr_bin=self.fake_ocr(invalid_json=True), from_ref=self.base, to_ref=self.head)
        self.assertEqual("failed", got["status"])
        self.assertEqual(2, len(got["native_review_required_files"]))

    def test_untrusted_path_is_rejected(self):
        got = adapter(repo=self.repo, ocr_bin=self.fake_ocr(malicious=True), from_ref=self.base, to_ref=self.head)
        self.assertEqual("failed", got["status"])
        self.assertEqual([], got["ocr_rule_groups"])
        self.assertEqual(2, len(got["native_review_required_files"]))

    def test_commit_mode_without_ocr_preserves_complete_inventory(self):
        got = adapter(repo=self.repo, ocr_bin="intentionally-missing-ocr", commit_ref=self.head)
        self.assertEqual("commit", got["mode"])
        self.assertEqual(self.head, got["target"]["head_sha"])
        self.assertEqual(["src/app.py", "tests/test_app.py"], got["native_review_required_files"])

    def test_merge_commit_first_parent_inventory(self):
        original_branch = run_git(self.repo, "symbolic-ref", "--short", "HEAD")
        run_git(self.repo, "checkout", "-q", "-b", "side", self.base)
        (self.repo / "side.py").write_text("side = True\n")
        run_git(self.repo, "add", ".")
        run_git(self.repo, "commit", "-q", "-m", "side feature")
        run_git(self.repo, "checkout", "-q", original_branch)
        run_git(self.repo, "merge", "-q", "--no-ff", "side", "-m", "merge feature")
        merged = run_git(self.repo, "rev-parse", "HEAD")
        got = adapter(repo=self.repo, ocr_bin="intentionally-missing-ocr", commit_ref=merged)
        self.assertTrue(got["target"]["merge_commit"])
        self.assertEqual(self.head, got["target"]["first_parent_sha"])
        self.assertEqual(["side.py"], got["native_review_required_files"])

    def test_root_commit_inventory(self):
        got = adapter(repo=self.repo, ocr_bin="intentionally-missing-ocr", commit_ref=self.base)
        self.assertIsNone(got["target"]["first_parent_sha"])
        self.assertEqual(["src/app.py", "tests/test_app.py"], got["native_review_required_files"])

    def test_rename_in_commit_and_range_includes_both_paths(self):
        run_git(self.repo, "mv", "src/app.py", "src/renamed.py")
        run_git(self.repo, "commit", "-q", "-m", "rename app")
        rename_head = run_git(self.repo, "rev-parse", "HEAD")
        for mode in ("commit", "range"):
            if mode == "commit":
                got = adapter(repo=self.repo, ocr_bin="intentionally-missing-ocr", commit_ref=rename_head)
            else:
                got = adapter(repo=self.repo, ocr_bin="intentionally-missing-ocr", from_ref=self.head, to_ref=rename_head)
            self.assertEqual(["src/app.py", "src/renamed.py"], got["native_review_required_files"])

    def test_rename_in_workspace_includes_both_paths(self):
        run_git(self.repo, "mv", "src/app.py", "src/renamed.py")
        got = adapter(repo=self.repo, ocr_bin="intentionally-missing-ocr")
        self.assertEqual(["src/app.py", "src/renamed.py"], got["native_review_required_files"])

    def test_workspace_without_ocr_includes_untracked(self):
        (self.repo / "new.py").write_text("print('new')\n")
        (self.repo / "src" / "app.py").write_text("uncommitted = True\n")
        got = adapter(repo=self.repo, ocr_bin="intentionally-missing-ocr")
        self.assertEqual("workspace", got["mode"])
        self.assertTrue(got["target"]["workspace_unpinned"])
        self.assertEqual(["new.py", "src/app.py"], got["git_changed_files"])

    def test_invalid_scope_does_not_call_ocr(self):
        with self.assertRaises(ValueError):
            adapter(repo=self.repo, from_ref="HEAD")
        with self.assertRaises(ValueError):
            adapter(repo=self.repo, commit_ref="")
        with self.assertRaises(ValueError):
            adapter(repo=self.repo, from_ref="HEAD", to_ref="HEAD", commit_ref="HEAD")

    def test_cli_emits_json_even_when_ocr_is_unavailable(self):
        from contextlib import redirect_stdout
        from io import StringIO
        output = StringIO()
        with redirect_stdout(output):
            exit_code = main(["--repo", str(self.repo), "--from", self.base, "--to", self.head, "--ocr-bin", "intentionally-missing-ocr"])
        self.assertEqual(0, exit_code)
        payload = json.loads(output.getvalue())
        self.assertEqual("unavailable", payload["status"])
        self.assertFalse(payload["review_performed"])


if __name__ == "__main__":
    unittest.main()
