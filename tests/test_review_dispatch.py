"""Behavioral acceptance tests: canonical review dispatch is OCR-first and fails closed."""
from __future__ import annotations

import contextlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "adapters" / "review"))
import run_review as runner  # noqa: E402


def git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=repo, stderr=subprocess.DEVNULL).decode().strip()


class ReviewDispatchTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        git(self.repo, "init", "-q")
        git(self.repo, "config", "user.name", "Test")
        git(self.repo, "config", "user.email", "test@example.invalid")
        (self.repo / "app.py").write_text("value = 1\n")
        git(self.repo, "add", ".")
        git(self.repo, "commit", "-q", "-m", "base")
        self.base = git(self.repo, "rev-parse", "HEAD")
        (self.repo / "app.py").write_text("value = 2\n")
        (self.repo / "test_app.py").write_text("assert 2 == 2\n")
        git(self.repo, "add", ".")
        git(self.repo, "commit", "-q", "-m", "change")
        self.head = git(self.repo, "rev-parse", "HEAD")
        self.capture = self.root / "review-context-captured.json"
        self.marker = self.root / "ocr-was-invoked"
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.reviewer = self.root / "fake-host-reviewer.py"
        self.reviewer.write_text(
            "import json, os, sys\n"
            "from pathlib import Path\n"
            "ctx=json.load(sys.stdin)\n"
            "Path(os.environ['CAPTURE_CONTEXT_PATH']).write_text(json.dumps(ctx))\n"
            "print(json.dumps({'review_status': 'PASS', 'coverage_status': 'complete', "
            "'target': ctx['target'], 'changed_files': ctx['changed_files'], "
            "'reviewed_files': ctx['review_required_files'], 'unreviewed_files': [], "
            "'blocking_findings': [], 'unresolved_questions': []}))\n"
        )

    def fake_ocr(self, version: str = "1.9.0") -> None:
        script = self.bin / "ocr"
        preview = {
            "schema_version": "1", "mode": "range", "repository": str(self.repo),
            "from": self.base, "to": self.head, "merge_base": self.base,
            "reviewable_files": [{"path": "app.py", "status": "M"}],
            "excluded_files": [{"path": "test_app.py", "status": "M",
                                "exclude_reason": "test"}],
        }
        script.write_text(
            "#!/usr/bin/env python3\n"
            "import sys, json\n"
            "from pathlib import Path\n"
            "Path(" + repr(str(self.marker)) + ").write_text('called')\n"
            "args = sys.argv[1:]\n"
            "if args == ['--version']:\n"
            "    print('open-code-review " + version + " linux/amd64')\n"
            "elif args[1] == 'preview':\n"
            "    print(json.dumps(" + repr(preview) + "))\n"
            "elif args[1] == 'rule':\n"
            "    paths = args[args.index('--repo') + 2:]\n"
            "    print(json.dumps({'schema_version': '1', 'groups': ["
            "{'group_id': 1, 'source': 'default', 'pattern': '*', "
            "'files': paths, 'rule': 'Check behavior'}]}))\n"
            "else: sys.exit(2)\n"
        )
        script.chmod(0o755)

    def call(self, *flags: str) -> tuple[int, dict]:
        out = io.StringIO()
        with patch.dict(os.environ, {
            "PATH": str(self.bin) + os.pathsep + os.environ.get("PATH", ""),
            "CAPTURE_CONTEXT_PATH": str(self.capture),
        }):
            with contextlib.redirect_stdout(out):
                code = runner.main([
                    "--repo", str(self.repo), "--from", self.base, "--to", self.head,
                    *flags, "--", sys.executable, str(self.reviewer),
                ])
        return code, json.loads(out.getvalue())

    def test_default_calls_ocr_first_then_native_reviewer(self):
        self.fake_ocr()
        code, result = self.call()
        self.assertEqual(0, code, result)
        self.assertTrue(self.marker.is_file())
        context = json.loads(self.capture.read_text())
        self.assertEqual("available", context["optional_helpers"]["ocr"]["status"])
        self.assertEqual(["app.py", "test_app.py"], context["review_required_files"])
        self.assertEqual("ocr-first", result["review_evidence"]["review_preparation"]["mode"])
        self.assertFalse(result["pre_pr_review_independence_verified"])
        self.assertEqual("PASS", result["review_status"])

    def test_no_ocr_even_when_installed_does_not_import_or_execute_ocr(self):
        self.fake_ocr()
        with patch("prepare_context.ocr_adapter", side_effect=AssertionError("OCR invoked")):
            code, result = self.call("--no-ocr")
        self.assertEqual(0, code, result)
        self.assertFalse(self.marker.exists())
        self.assertEqual("disabled", result["review_evidence"]["optional_helpers"]["ocr"]["status"])
        self.assertEqual("native-only", result["review_evidence"]["review_preparation"]["mode"])
        self.assertEqual(["app.py", "test_app.py"], result["native_full_scope"])

    def test_missing_ocr_falls_back_without_skipping_review(self):
        with patch("shutil.which", return_value=None):
            code, result = self.call()
        self.assertEqual(0, code, result)
        self.assertEqual("unavailable", result["review_evidence"]["optional_helpers"]["ocr"]["status"])
        self.assertEqual("native-fallback", result["review_evidence"]["review_preparation"]["mode"])
        self.assertTrue(self.capture.is_file())
        self.assertFalse(self.marker.exists())

    def test_unsupported_ocr_falls_back_without_skipping_review(self):
        self.fake_ocr(version="1.8.0")
        code, result = self.call()
        self.assertEqual(0, code, result)
        self.assertEqual("unsupported", result["review_evidence"]["optional_helpers"]["ocr"]["status"])
        self.assertEqual("native-fallback", result["review_evidence"]["review_preparation"]["mode"])
        self.assertTrue(self.capture.is_file())

    def test_r3_team_plan_is_frozen_before_host_reviewer(self):
        self.reviewer.write_text(
            "import json, os, sys\n"
            "from pathlib import Path\n"
            "ctx=json.load(sys.stdin)\n"
            "Path(os.environ['CAPTURE_CONTEXT_PATH']).write_text(json.dumps(ctx))\n"
            "print(json.dumps({'review_status':'INCOMPLETE','target':ctx['target'],"
            "'changed_files':ctx['changed_files'],'reviewed_files':[],"
            "'unreviewed_files':ctx['changed_files'],'risk_profile':'R3',"
            "'review_id':ctx['team_plan']['review_id']}))\n"
        )
        code, result = self.call(
            "--no-ocr", "--risk-profile", "R3", "--task-capable",
            "--isolated-subagents", "--concern", "correctness",
            "--concern", "reliability", "--concern", "security",
        )
        self.assertEqual(1, code, result)
        captured = json.loads(self.capture.read_text())
        plan = captured["team_plan"]
        self.assertEqual("R3", plan["risk_profile"])
        self.assertEqual(3, len(plan["selected_roles"]))
        self.assertEqual("team-relayed", plan["execution_mode"])
        self.assertEqual(captured["target"], plan["target"])

    def test_r3_task_without_concerns_blocks_before_reviewer(self):
        code, out = self.call(
            "--no-ocr", "--risk-profile", "R3", "--task-capable",
            "--isolated-subagents",
        )
        self.assertEqual(2, code)
        self.assertEqual("INCOMPLETE", out["review_status"])
        self.assertIn("at least one genuine", out["reason"])
        self.assertFalse(self.capture.exists())

    def test_task_requires_frozen_risk_before_review(self):
        code, out = self.call("--no-ocr", "--task-capable")
        self.assertEqual(2, code)
        self.assertIn("risk_profile must be classified", out["reason"])
        self.assertFalse(self.capture.exists())

    def test_r3_team_cannot_claim_pass_without_task_ids(self):
        code, out = self.call(
            "--no-ocr", "--risk-profile", "R3", "--task-capable",
            "--isolated-subagents", "--concern", "correctness",
            "--concern", "reliability", "--concern", "security",
        )
        self.assertEqual(2, code)
        self.assertIn("frozen team or risk identity", out["reason"])

    def test_workspace_mutation_during_review_invalidates_pass(self):
        self.reviewer.write_text(
            "import json, sys\n"
            "from pathlib import Path\n"
            "ctx=json.load(sys.stdin)\n"
            "Path('new-untracked.txt').write_text('changed while reviewing')\n"
            "print(json.dumps({'review_status':'PASS','coverage_status':'complete',"
            "'target':ctx['target'],'changed_files':ctx['changed_files'],"
            "'reviewed_files':ctx['changed_files'],'unreviewed_files':[],"
            "'blocking_findings':[],'unresolved_questions':[]}))\n"
        )
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = runner.main([
                "--repo", str(self.repo), "--no-ocr", "--", sys.executable, str(self.reviewer),
            ])
        self.assertEqual(2, code)
        result = json.loads(out.getvalue())
        self.assertEqual("INCOMPLETE", result["review_status"])
        self.assertIn("fingerprint changed during review", result["reason"])

    def test_missing_reviewer_command_does_not_claim_pass(self):
        with self.assertRaisesRegex(runner.ReviewInvocationError, "approved host reviewer"):
            runner.dispatch({"changed_files": [], "target": {}}, repo=self.repo, reviewer_command=[])

    def test_fake_pass_without_complete_native_coverage_is_blocked(self):
        self.reviewer.write_text(
            "import json, sys\n"
            "ctx=json.load(sys.stdin)\n"
            "print(json.dumps({'review_status':'PASS','coverage_status':'complete',"
            "'target':ctx['target'],'changed_files':ctx['changed_files'],"
            "'reviewed_files':['app.py'],'unreviewed_files':[] }))\n"
        )
        code, result = self.call("--no-ocr")
        self.assertEqual(2, code)
        self.assertEqual("INCOMPLETE", result["review_status"])
        self.assertIn("complete native review evidence", result["reason"])

    def test_reviewer_cannot_override_disabled_ocr_metadata(self):
        self.reviewer.write_text(
            "import json, sys\n"
            "ctx=json.load(sys.stdin)\n"
            "print(json.dumps({'review_status':'PASS','coverage_status':'complete',"
            "'target':ctx['target'],'changed_files':ctx['changed_files'],"
            "'reviewed_files':ctx['changed_files'],'unreviewed_files':[],"
            "'optional_helpers':{'ocr':{'status':'available'}} }))\n"
        )
        code, result = self.call("--no-ocr")
        self.assertEqual(0, code, result)
        self.assertEqual("disabled", result["review_evidence"]["optional_helpers"]["ocr"]["status"])


if __name__ == "__main__":
    unittest.main()
