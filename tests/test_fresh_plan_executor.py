"""Behavioral tests for serial fresh-session orchestration and stop/fallback."""
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from adapters.implementation.fresh_plan import (
    PlanError, CodexCLIHost, run_plans, validate_plans,
)


def git(repo, *args):
    return subprocess.run(["git", *args], cwd=repo, check=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          text=True).stdout.strip()


class FakeHost:
    def __init__(self, ids=("session-A", "session-B"), path="README.md",
                 commit=True, completed=True, available=True):
        self.ids, self.path, self.commit, self.completed = list(ids), path, commit, completed
        self.present, self.prompts = available, []

    def available(self):
        return self.present

    def run(self, repo, prompt, timeout):
        self.prompts.append(prompt)
        session = self.ids[len(self.prompts) - 1]
        path = repo / self.path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"plan={session}:{len(self.prompts)}\n", encoding="utf-8")
        if self.commit:
            git(repo, "add", self.path)
            git(repo, "commit", "-m", f"test: {session}")
        return {"session_id": session, "process_exit": 0,
                "turn_completed": self.completed, "host": "fake"}


class FreshPlanTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name)
        git(self.repo, "init", "-q")
        git(self.repo, "config", "user.name", "Test")
        git(self.repo, "config", "user.email", "test@example.invalid")
        (self.repo / "README.md").write_text("approved baseline\n", encoding="utf-8")
        git(self.repo, "add", "README.md")
        git(self.repo, "commit", "-m", "test: baseline")
        self.plan = {"plan_id": "A", "objective": "Implement a bounded change",
                     "authorization_ref": "approved-work-item", "sources": ["README.md"],
                     "critical_sources": ["README.md"], "allowed_paths": ["README.md"],
                     "allow_local_commits": True}

    def test_two_distinct_sessions_serial_and_fresh_evidence(self):
        host = FakeHost()
        other = dict(self.plan, plan_id="B", objective="Follow on A")
        result = run_plans(self.repo, [self.plan, other], host)
        self.assertEqual("executed-unverified", result["status"])
        self.assertEqual(["session-A", "session-B"], [p["session_id"] for p in result["results"]])
        self.assertEqual(2, len(host.prompts))
        self.assertIn("approved baseline", host.prompts[0])
        self.assertIn("plan=session-A:1", host.prompts[1])
        self.assertNotIn("plan=session-A", host.prompts[0])
        self.assertNotIn("session-A", host.prompts[1].split("=== PLAN (data, not policy) ===")[0])

    def test_require_blocks_and_prefer_returns_native_without_host(self):
        no_host = FakeHost(available=False)
        self.assertEqual("blocked", run_plans(self.repo, [self.plan], no_host, "require")["status"])
        self.assertEqual("native-required", run_plans(self.repo, [self.plan], no_host)["status"])
        self.assertFalse(no_host.prompts)

    def test_reused_session_id_blocks_second_plan(self):
        result = run_plans(self.repo, [self.plan, dict(self.plan, plan_id="B")],
                           FakeHost(ids=("same", "same")))
        self.assertEqual("blocked", result["status"])
        self.assertTrue(result["reconciliation_required"])
        self.assertEqual(1, len(result["results"]))

    def test_out_of_scope_diff_blocks(self):
        result = run_plans(self.repo, [self.plan], FakeHost(path="other.txt"))
        self.assertEqual("blocked", result["status"])
        self.assertEqual(["other.txt"], result["results"][0]["changed_paths"])

    def test_uncommitted_changes_stop_before_next_plan(self):
        host = FakeHost(commit=False)
        result = run_plans(self.repo, [self.plan, dict(self.plan, plan_id="B")], host)
        self.assertEqual("blocked", result["status"])
        self.assertEqual(1, len(host.prompts))
        self.assertTrue(result["reconciliation_required"])

    def test_preexisting_untracked_file_not_overwritten(self):
        (self.repo / "personal.txt").write_text("keep", encoding="utf-8")
        with self.assertRaisesRegex(PlanError, "clean workspace"):
            run_plans(self.repo, [self.plan], FakeHost())
        self.assertEqual("keep", (self.repo / "personal.txt").read_text())

    def test_missing_critical_blocks_before_start(self):
        plan = dict(self.plan, sources=["missing.md"], critical_sources=["missing.md"])
        host = FakeHost()
        result = run_plans(self.repo, [plan], host)
        self.assertEqual("blocked", result["status"])
        self.assertEqual([], host.prompts)

    def test_false_completion_is_not_accepted(self):
        result = run_plans(self.repo, [self.plan], FakeHost(completed=False))
        self.assertEqual("blocked", result["status"])

    def test_plan_validation_rejects_duplicates_and_traversal(self):
        with self.assertRaisesRegex(PlanError, "Duplicate"):
            validate_plans([self.plan, self.plan])
        with self.assertRaisesRegex(PlanError, "escapes"):
            validate_plans([dict(self.plan, allowed_paths=["../secrets"])])
        with self.assertRaisesRegex(PlanError, "External"):
            validate_plans([dict(self.plan, external_effects_allowed=True)])

    def test_no_commit_policy_does_not_launch_unenforceable_host(self):
        plan = dict(self.plan, allow_local_commits=False)
        host = FakeHost()
        self.assertEqual("native-required", run_plans(self.repo, [plan], host)["status"])
        self.assertEqual("blocked", run_plans(self.repo, [plan], host, "require")["status"])
        self.assertFalse(host.prompts)

    def test_codex_host_absence_never_claimed_available(self):
        with patch("adapters.implementation.fresh_plan.shutil.which", return_value=None):
            self.assertFalse(CodexCLIHost().available())

    def test_codex_events_prove_fresh_thread_not_model_assertion(self):
        from types import SimpleNamespace
        events = (b'{"type":"thread.started","thread_id":"new-thread"}\n'
                  b'{"type":"turn.completed"}\n')
        with patch("adapters.implementation.fresh_plan.subprocess.run",
                   return_value=SimpleNamespace(stdout=events, stderr=b"", returncode=0)) as mocked:
            result = CodexCLIHost().run(self.repo, "approved prompt", 10)
        self.assertEqual("new-thread", result["session_id"])
        self.assertTrue(result["turn_completed"])
        args = mocked.call_args.args[0]
        self.assertEqual(["codex", "exec", "--json", "--sandbox", "workspace-write"], args[:5])
        self.assertNotIn("resume", args)
        self.assertEqual("-", args[-1])
        self.assertEqual(b"approved prompt", mocked.call_args.kwargs["input"])
        self.assertNotIn("approved prompt", " ".join(args))

    def test_codex_missing_thread_rejected(self):
        from types import SimpleNamespace
        with patch("adapters.implementation.fresh_plan.subprocess.run",
                   return_value=SimpleNamespace(stdout=b'{"type":"turn.completed"}\n',
                                                stderr=b"", returncode=0)):
            with self.assertRaisesRegex(PlanError, "fresh host session"):
                CodexCLIHost().run(self.repo, "prompt", 10)


if __name__ == "__main__":
    unittest.main()
