"""Native context retrieval never needs SQLite, an LLM or external packages."""
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from adapters.context.native import ContextError, prepare_context, search_sources, verify_context


class NativeContextTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name)
        subprocess.run(["git", "init", "-q"], cwd=self.repo, check=True)
        (self.repo / "rules.md").write_text(
            "Never publish without approval.\nAuthorization must be checked.\n",
            encoding="utf-8",
        )
        (self.repo / "design.md").write_text("Implementation plan.\n", encoding="utf-8")
        subprocess.run(["git", "add", "rules.md", "design.md"], cwd=self.repo, check=True)
        subprocess.run(
            ["git", "-c", "user.email=test@example.invalid", "-c",
             "user.name=Test", "commit", "-qm", "fixture"],
            cwd=self.repo, check=True,
        )

    def test_critical_ref_is_fully_retrieved_and_ordered_first(self):
        pack = prepare_context(self.repo, ["design.md"], ["rules.md#L1"])
        self.assertEqual(pack["status"], "ready")
        self.assertEqual(pack["sources"][0]["ref"], "rules.md#L1")
        self.assertTrue(pack["sources"][0]["critical"])
        self.assertEqual(pack["sources"][0]["content"],
                         "Never publish without approval.\n")
        self.assertEqual(verify_context(self.repo, pack)["status"], "unchanged")

    def test_critical_source_not_found_blocks(self):
        pack = prepare_context(self.repo, ["design.md"], ["missing.md"])
        self.assertEqual(pack["status"], "blocked")
        self.assertEqual(pack["missing_critical"], ["missing.md"])

    def test_insufficient_budget_does_not_truncate_critical_rule(self):
        (self.repo / "rules.md").write_text("x" * 300, encoding="utf-8")
        pack = prepare_context(self.repo, [], ["rules.md"], max_chars=128)
        self.assertEqual(pack["status"], "blocked")
        self.assertEqual(pack["sources"], [])

    def test_untracked_files_cannot_be_injected_into_pack(self):
        (self.repo / "secret.txt").write_text("private", encoding="utf-8")
        pack = prepare_context(self.repo, ["secret.txt"], ["rules.md"])
        self.assertEqual(pack["status"], "partial")
        self.assertNotIn("private", json.dumps(pack))

    def test_path_escape_and_symlink_are_rejected(self):
        pack = prepare_context(self.repo, ["../outside"], ["rules.md"])
        self.assertEqual(pack["status"], "partial")
        (self.repo / "link.md").symlink_to(self.repo / "rules.md")
        pack = prepare_context(self.repo, ["link.md"], ["rules.md"])
        self.assertEqual(pack["status"], "partial")
        self.assertEqual(len(pack["sources"]), 1)

    def test_file_changes_invalidate_source_pack(self):
        pack = prepare_context(self.repo, ["rules.md"], ["rules.md"])
        (self.repo / "rules.md").write_text("Relax all rules.\n", encoding="utf-8")
        outcome = verify_context(self.repo, pack)
        self.assertEqual(outcome["status"], "blocked")
        self.assertEqual(outcome["sources"][0]["status"], "stale")

    def test_git_head_change_requires_revalidation(self):
        pack = prepare_context(self.repo, ["rules.md"], ["rules.md"])
        (self.repo / "other.md").write_text("other", encoding="utf-8")
        subprocess.run(["git", "add", "other.md"], cwd=self.repo, check=True)
        subprocess.run(
            ["git", "-c", "user.email=test@example.invalid", "-c",
             "user.name=Test", "commit", "-qm", "unrelated"],
            cwd=self.repo, check=True,
        )
        outcome = verify_context(self.repo, pack)
        self.assertEqual(outcome["status"], "revalidate")
        self.assertTrue(outcome["head_changed"])

    def test_search_is_explicitly_scoped_and_non_authoritative(self):
        response = search_sources(self.repo, "authorization", ["."])
        self.assertEqual(response["status"], "complete")
        self.assertEqual(response["results"][0]["ref"], "rules.md#L2")
        self.assertIn("not complete evidence", response["note"])
        with self.assertRaises(ContextError):
            search_sources(self.repo, "authorization", [])


if __name__ == "__main__":
    unittest.main()
