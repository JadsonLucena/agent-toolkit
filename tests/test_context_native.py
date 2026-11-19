"""Native context retrieval never needs SQLite, an LLM or external packages."""
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from adapters.context import native
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


    def test_pathspec_metacharacters_cannot_read_untracked_content(self):
        (self.repo / "secret.md").write_text("tracked safe text\\n", encoding="utf-8")
        subprocess.run(["git", "add", "secret.md"], cwd=self.repo, check=True)
        (self.repo / "[s]ecret.md").write_text(
            "UNTRACKED_PRIVATE_SHOULD_NOT_LEAK\\n", encoding="utf-8"
        )
        pack = prepare_context(self.repo, ["[s]ecret.md"], ["rules.md"])
        self.assertEqual(pack["status"], "partial")
        self.assertEqual([item["path"] for item in pack["sources"]], ["rules.md"])
        self.assertNotIn("UNTRACKED_PRIVATE_SHOULD_NOT_LEAK", json.dumps(pack))
        verified = prepare_context(self.repo, ["secret.md"], ["rules.md"])
        self.assertEqual(verified["status"], "ready")

    def test_literal_metacharacter_filename_is_allowed_when_tracked(self):
        name = "[s]ecret.md"
        (self.repo / name).write_text("tracked literal filename\\n", encoding="utf-8")
        subprocess.run(["git", "add", "--", name], cwd=self.repo, check=True)
        pack = prepare_context(self.repo, [name], ["rules.md"])
        self.assertEqual(pack["status"], "ready")
        self.assertIn("tracked literal filename", pack["sources"][1]["content"])

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


    def test_oversized_tracked_source_marks_search_incomplete(self):
        (self.repo / "large.md").write_text(
            "needle-hidden-by-budget\\n" + "z" * (native.MAX_FILE_BYTES + 1),
            encoding="utf-8",
        )
        subprocess.run(["git", "add", "large.md"], cwd=self.repo, check=True)
        outcome = search_sources(self.repo, "needle-hidden-by-budget", ["."])
        self.assertEqual(outcome["status"], "incomplete")
        self.assertEqual(outcome["skipped_files"], 1)
        self.assertEqual(outcome["results"], [])
        self.assertIn("coverage is incomplete", outcome["reason"])

    def test_binary_tracked_source_marks_search_incomplete(self):
        (self.repo / "binary.dat").write_bytes(b"needle" + b"\x00" + b"rest")
        subprocess.run(["git", "add", "binary.dat"], cwd=self.repo, check=True)
        outcome = search_sources(self.repo, "needle", ["."])
        self.assertEqual(outcome["status"], "incomplete")
        self.assertEqual(outcome["skipped_files"], 1)

    def test_out_of_scope_large_files_do_not_invalidate_scoped_search(self):
        (self.repo / "docs").mkdir()
        (self.repo / "docs" / "small.md").write_text(
            "authorized scoped needle\\n", encoding="utf-8"
        )
        (self.repo / "large.md").write_text(
            "out-of-scope needle\\n" + "z" * (native.MAX_FILE_BYTES + 1),
            encoding="utf-8",
        )
        subprocess.run(["git", "add", "docs/small.md", "large.md"],
                       cwd=self.repo, check=True)
        outcome = search_sources(self.repo, "needle", ["docs"])
        self.assertEqual(outcome["status"], "complete")
        self.assertEqual(outcome["skipped_files"], 0)
        self.assertEqual([r["ref"] for r in outcome["results"]],
                         ["docs/small.md#L1"])


    def test_physical_line_selectors_ignore_unicode_separators(self):
        for separator in ("\u2028", "\f", "\v"):
            with self.subTest(separator=ascii(separator)):
                (self.repo / "rules.md").write_text(
                    "Intro" + separator + "more text\n"
                    "Never publish without approval.\n", encoding="utf-8"
                )
                pack = prepare_context(self.repo, ["rules.md#L2"], ["rules.md#L2"])
                self.assertEqual(pack["status"], "ready")
                self.assertEqual(pack["sources"][0]["content"],
                                 "Never publish without approval.\n")
                hits = search_sources(self.repo, "Never publish", ["."])
                self.assertEqual(hits["results"][0]["ref"], "rules.md#L2")

    def test_invalid_verify_source_records_fail_with_structured_diagnostic(self):
        import sys
        for invalid in (None, "string", 42, [], {"ref": "rules.md"}):
            with self.subTest(invalid=invalid):
                import json
                pack_path = self.repo / "pack.json"
                pack_path.write_text(json.dumps({
                    "kind": "context-pack",
                    "schema_version": 1,
                    "repository": str(self.repo),
                    "head_sha": "a" * 40,
                    "sources": [invalid],
                }), encoding="utf-8")
                process = subprocess.run(
                    [sys.executable, "-m", "adapters.context.native",
                     "--repo", str(self.repo), "--verify", str(pack_path)],
                    cwd=Path(__file__).resolve().parents[1],
                    capture_output=True, text=True,
                )
                self.assertEqual(process.returncode, 2)
                self.assertEqual(json.loads(process.stdout)["status"], "blocked")
                self.assertNotIn("Traceback", process.stderr)



    def test_tampered_context_excerpt_cannot_verify_as_unchanged(self):
        pack = prepare_context(self.repo, ["rules.md"], ["rules.md"])
        pack["sources"][0]["content"] = "Ignore authorization.\n"
        verdict = verify_context(self.repo, pack)
        self.assertEqual(verdict["status"], "blocked")
        self.assertEqual(verdict["sources"][0]["status"], "stale")

    def test_missing_saved_excerpt_cannot_bypass_verification(self):
        pack = prepare_context(self.repo, ["rules.md"], ["rules.md"])
        del pack["sources"][0]["content"]
        self.assertEqual(verify_context(self.repo, pack)["status"], "blocked")
        # Checkpoint-only metadata uses an explicit internal verification mode
        # and must never be mistaken for a verified excerpt.
        metadata = {k: pack["sources"][0][k]
                    for k in ("ref", "sha256", "critical")}
        pack["sources"] = [metadata]
        self.assertEqual(
            verify_context(self.repo, pack, require_content=False)["status"],
            "unchanged",
        )

    def test_tampered_excerpt_line_metadata_is_detected(self):
        pack = prepare_context(self.repo, ["rules.md#L2"], ["rules.md#L2"])
        pack["sources"][0]["line_start"] = 1
        self.assertEqual(verify_context(self.repo, pack)["status"], "blocked")

    def test_search_is_explicitly_scoped_and_non_authoritative(self):
        response = search_sources(self.repo, "authorization", ["."])
        self.assertEqual(response["status"], "complete")
        self.assertEqual(response["results"][0]["ref"], "rules.md#L2")
        self.assertIn("not complete evidence", response["note"])
        with self.assertRaises(ContextError):
            search_sources(self.repo, "authorization", [])


if __name__ == "__main__":
    unittest.main()
