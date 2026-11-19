"""FTS5 is optional, never auto-built, and never overrides native evidence."""
import importlib
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from adapters.context import native, fts5


class OptionalFTS5Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=self.repo, check=True)
        (self.repo / "docs").mkdir()
        (self.repo / "other").mkdir()
        (self.repo / "docs" / "a.md").write_text(
            "Authorization check must hold.\nContext selection is bounded.\n",
            encoding="utf-8",
        )
        (self.repo / "docs" / "b.md").write_text("Check the security boundary.\n", encoding="utf-8")
        (self.repo / "other" / "c.md").write_text("Other domain authorization.\n", encoding="utf-8")
        (self.repo / "docs" / ".env").write_text("API_TOKEN=never-index\n", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=self.repo, check=True)
        subprocess.run(
            ["git", "-c", "user.name=Test", "-c", "user.email=test@example.invalid",
             "commit", "-qm", "test fixtures"], cwd=self.repo, check=True,
        )
        self.private = self.root / "private"
        self.private.mkdir(mode=0o700)
        self.db = self.private / "index.sqlite3"

    def _build(self):
        if fts5._sqlite() is None:
            self.skipTest("FTS5 trigram unavailable on this host")
        return fts5.build_index(self.repo, ["docs"], self.db, approved=True)

    def test_default_never_imports_sqlite_or_touches_existing_database(self):
        with patch.object(fts5, "_sqlite", side_effect=AssertionError("SQLite probed")), \
             patch.object(fts5, "_indexed_search", side_effect=AssertionError("index opened")):
            result = fts5.search(self.repo, "authorization", ["docs"], db=self.db)
        self.assertFalse(result["index_used"])
        self.assertEqual(result["backend"], "native")
        self.assertFalse(self.db.exists())

    def test_build_requires_explicit_approval(self):
        with patch.object(fts5, "_sqlite", side_effect=AssertionError("SQLite probed")):
            with self.assertRaises(fts5.IndexError):
                fts5.build_index(self.repo, ["docs"], self.db)
        self.assertFalse(self.db.exists())

    def test_requested_index_matches_scoped_native_leads(self):
        result = self._build()
        self.assertEqual(result["backend"], "sqlite-fts5")
        self.assertEqual(result["indexed"], 2)
        self.assertEqual(result["skipped"], 1)
        indexed = fts5.search(self.repo, "authorization", ["docs"], db=self.db, mode="indexed")
        native_result = native.search_sources(self.repo, "authorization", ["docs"])
        self.assertTrue(indexed["index_used"])
        self.assertEqual(indexed["results"], native_result["results"])
        self.assertEqual(indexed["status"], "incomplete")
        self.assertNotIn("never-index", str(indexed))

    def test_auto_uses_existing_index_only_after_native_is_incomplete(self):
        self._build()
        with patch.object(native, "MAX_SCAN_FILES", 1):
            result = fts5.search(self.repo, "authorization", ["docs"], db=self.db,
                                 mode="auto", enable_optional=True)
        self.assertTrue(result["index_used"])
        self.assertEqual(result["selection_reason"], "native_incomplete")
        self.assertEqual(result["results"][0]["ref"], "docs/a.md#L1")

    def test_auto_does_not_use_index_when_native_is_sufficient(self):
        self._build()
        with patch.object(fts5, "_indexed_search", side_effect=AssertionError("index opened")):
            result = fts5.search(self.repo, "authorization", ["docs"], db=self.db,
                                 mode="auto", enable_optional=True)
        self.assertFalse(result["index_used"])
        self.assertEqual(result["selection_reason"], "native_sufficient")

    def test_unavailable_fts5_falls_back_to_native(self):
        with patch.object(fts5, "_sqlite", return_value=None):
            result = fts5.search(self.repo, "authorization", ["docs"],
                                 db=self.db, mode="indexed")
        self.assertEqual(result["backend"], "native")
        self.assertFalse(result["index_used"])
        self.assertIn("unavailable", result["fallback_reason"])
        self.assertFalse(self.db.exists())

    def test_scope_cannot_expand_after_index_build(self):
        self._build()
        result = fts5.search(self.repo, "authorization", ["."],
                             db=self.db, mode="indexed")
        self.assertEqual(result["backend"], "native")
        self.assertIn("scope", result["fallback_reason"])

    def test_foreign_repository_cannot_reuse_index(self):
        self._build()
        second = self.root / "repo2"
        second.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=second, check=True)
        (second / "docs").mkdir()
        (second / "docs" / "a.md").write_text("authorization\n", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=second, check=True)
        subprocess.run(["git", "-c", "user.name=Test", "-c",
                        "user.email=test@example.invalid", "commit", "-qm", "fixture"],
                       cwd=second, check=True)
        result = fts5.search(second, "authorization", ["docs"], db=self.db, mode="indexed")
        self.assertEqual(result["backend"], "native")
        self.assertIn("another repo", result["fallback_reason"])

    def test_head_change_invalidates_index(self):
        self._build()
        (self.repo / "docs" / "a.md").write_text("Different wording.\n", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=self.repo, check=True)
        subprocess.run(["git", "-c", "user.name=Test", "-c",
                        "user.email=test@example.invalid", "commit", "-qm", "changed"],
                       cwd=self.repo, check=True)
        result = fts5.search(self.repo, "authorization", ["docs"], db=self.db, mode="indexed")
        self.assertEqual(result["backend"], "native")
        self.assertIn("stale", result["fallback_reason"])

    def test_dirty_worktree_invalidates_index(self):
        self._build()
        (self.repo / "docs" / "a.md").write_text("New authorization.\n", encoding="utf-8")
        result = fts5.search(self.repo, "authorization", ["docs"], db=self.db, mode="indexed")
        self.assertEqual(result["backend"], "native")
        self.assertIn("dirty", result["fallback_reason"])

    def test_private_db_is_required_and_outside_repository(self):
        if fts5._sqlite() is None:
            self.skipTest("FTS5 unavailable")
        with self.assertRaises(fts5.IndexError):
            fts5.build_index(self.repo, ["docs"], self.repo / "repo_index.sqlite3",
                             approved=True)
        public = self.root / "public"
        public.mkdir(mode=0o755)
        with self.assertRaises(fts5.IndexError):
            fts5.build_index(self.repo, ["docs"], public / "index.sqlite3", approved=True)

    def test_short_query_does_not_use_index(self):
        self._build()
        result = fts5.search(self.repo, "au", ["docs"], db=self.db, mode="indexed")
        self.assertFalse(result["index_used"])
        self.assertEqual(result["backend"], "native")


    def test_casefold_expansion_matches_native_unicode_search(self):
        (self.repo / "docs" / "unicode.md").write_text(
            "Straße links to the security rule.\\n"
            "Somebody STRASSE used another spelling.\\n",
            encoding="utf-8",
        )
        subprocess.run(["git", "add", "."], cwd=self.repo, check=True)
        subprocess.run(["git", "-c", "user.name=Test", "-c",
                        "user.email=test@example.invalid", "commit",
                        "-qm", "unicode fixture"], cwd=self.repo, check=True)
        self._build()
        for term in ("STRASSE", "Straße", "straße", "STRASSe"):
            with self.subTest(term=term):
                found = fts5.search(self.repo, term, ["docs"],
                                    db=self.db, mode="indexed")
                direct = native.search_sources(self.repo, term, ["docs"])
                self.assertTrue(found["index_used"])
                self.assertEqual(found["results"], direct["results"])

    def test_wildcard_in_approved_directory_name_is_never_expanded(self):
        literal = self.repo / "docs*"
        literal.mkdir()
        other = self.repo / "docs2"
        other.mkdir()
        (literal / "allowed.md").write_text(
            "approved unusual scope\\n", encoding="utf-8"
        )
        (other / "outside.md").write_text(
            "UNAPPROVED_SCOPE_CONTENT\\n", encoding="utf-8"
        )
        subprocess.run(["git", "add", "."], cwd=self.repo, check=True)
        subprocess.run(["git", "-c", "user.name=Test", "-c",
                        "user.email=test@example.invalid", "commit",
                        "-qm", "literal pathspec fixtures"], cwd=self.repo, check=True)
        if fts5._sqlite() is None:
            self.skipTest("FTS5 unavailable")
        outcome = fts5.build_index(self.repo, ["docs*"], self.db, approved=True)
        self.assertEqual(outcome["indexed"], 1)
        self.assertEqual(outcome["skipped"], 0)
        result = fts5.search(self.repo, "approved", ["docs*"],
                             db=self.db, mode="indexed")
        self.assertEqual(result["results"][0]["ref"], "docs*/allowed.md#L1")
        import sqlite3
        with sqlite3.connect(self.db) as conn:
            entries = [row[0] for row in conn.execute("SELECT path FROM sources")]
        self.assertEqual(entries, ["docs*/allowed.md"])
        self.assertNotIn("UNAPPROVED_SCOPE_CONTENT", str(result))

    def test_glob_like_filename_does_not_expand_scoped_index(self):
        if fts5._sqlite() is None:
            self.skipTest("FTS5 unavailable")
        folder = self.repo / "docs[1]"
        folder.mkdir()
        (folder / "literal.md").write_text("Scoped authorization.\\n", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=self.repo, check=True)
        subprocess.run(["git", "-c", "user.name=Test", "-c",
                        "user.email=test@example.invalid", "commit",
                        "-qm", "bracket fixture"], cwd=self.repo, check=True)
        outcome = fts5.build_index(self.repo, ["docs[1]"], self.db, approved=True)
        self.assertEqual(outcome["indexed"], 1)
        found = fts5.search(self.repo, "authorization", ["docs[1]"],
                            db=self.db, mode="indexed")
        self.assertEqual(found["results"][0]["ref"], "docs[1]/literal.md#L1")


    def test_symlink_in_approved_scope_is_counted_as_skipped(self):
        try:
            (self.repo / "docs" / "linked.md").symlink_to("a.md")
        except (OSError, NotImplementedError):
            self.skipTest("symlinks unavailable")
        subprocess.run(["git", "add", "docs/linked.md"], cwd=self.repo, check=True)
        subprocess.run(
            ["git", "-c", "user.name=Test", "-c", "user.email=test@example.invalid",
             "commit", "-qm", "tracked symlink"], cwd=self.repo, check=True,
        )
        outcome = self._build()
        self.assertEqual(outcome["indexed"], 2)
        self.assertEqual(outcome["skipped"], 2)  # Existing .env plus symlink.
        found = fts5.search(self.repo, "authorization", ["docs"],
                            db=self.db, mode="indexed")
        self.assertTrue(found["index_used"])
        self.assertEqual(found["results"][0]["ref"], "docs/a.md#L1")
        self.assertEqual(found["status"], "incomplete")

    def test_assume_unchanged_flag_invalidates_existing_index(self):
        self._build()
        subprocess.run(
            ["git", "update-index", "--assume-unchanged", "docs/a.md"],
            cwd=self.repo, check=True,
        )
        (self.repo / "docs" / "a.md").write_text("No matching rule remains.\\n",
                                                   encoding="utf-8")
        result = fts5.search(self.repo, "authorization", ["docs"],
                             db=self.db, mode="indexed")
        self.assertEqual(result["backend"], "native")
        self.assertFalse(result["index_used"])
        self.assertIn("assume-unchanged", result["fallback_reason"])
        self.assertEqual(result["results"], [])

    def test_assume_unchanged_flag_blocks_index_creation(self):
        if fts5._sqlite() is None:
            self.skipTest("FTS5 unavailable")
        subprocess.run(
            ["git", "update-index", "--assume-unchanged", "docs/a.md"],
            cwd=self.repo, check=True,
        )
        with self.assertRaisesRegex(fts5.IndexError, "assume-unchanged"):
            fts5.build_index(self.repo, ["docs"], self.db, approved=True)
        self.assertFalse(self.db.exists())

    def test_skip_worktree_flag_invalidates_existing_index(self):
        self._build()
        subprocess.run(
            ["git", "update-index", "--skip-worktree", "docs/a.md"],
            cwd=self.repo, check=True,
        )
        result = fts5.search(self.repo, "authorization", ["docs"],
                             db=self.db, mode="indexed")
        self.assertEqual(result["backend"], "native")
        self.assertIn("skip-worktree", result["fallback_reason"])

    def test_probe_closes_temporary_sqlite_connection(self):
        import sqlite3
        actual_connect = sqlite3.connect
        opened = []

        class ConnectionSpy:
            def __init__(self, *args, **kwargs):
                self.actual = actual_connect(*args, **kwargs)
                self.closed = False
                opened.append(self)

            def execute(self, *args, **kwargs):
                return self.actual.execute(*args, **kwargs)

            def close(self):
                self.closed = True
                self.actual.close()

        with patch.object(sqlite3, "connect",
                          side_effect=lambda *a, **kw: ConnectionSpy(*a, **kw)):
            self.assertIs(fts5._sqlite(), sqlite3)
        self.assertTrue(opened)
        self.assertTrue(all(conn.closed for conn in opened))

    def test_indexed_search_closes_file_connection(self):
        self._build()
        import sqlite3
        actual_connect = sqlite3.connect
        opened = []

        class ConnectionSpy:
            def __init__(self, *args, **kwargs):
                self.actual = actual_connect(*args, **kwargs)
                self.closed = False
                opened.append(self)

            def execute(self, *args, **kwargs):
                return self.actual.execute(*args, **kwargs)

            def close(self):
                self.closed = True
                self.actual.close()

        class SQLiteProxy:
            Error = sqlite3.Error
            @staticmethod
            def connect(*args, **kwargs):
                return ConnectionSpy(*args, **kwargs)

        with patch.object(fts5, "_sqlite", return_value=SQLiteProxy):
            response = fts5.search(self.repo, "authorization", ["docs"],
                                   db=self.db, mode="indexed")
        self.assertTrue(response["index_used"])
        self.assertTrue(opened)
        self.assertTrue(all(conn.closed for conn in opened))


    def test_indexed_physical_line_references_match_native(self):
        (self.repo / "docs" / "unicode_lines.md").write_text(
            "Intro\u2028other text\nAuthorization must remain.\n",
            encoding="utf-8",
        )
        subprocess.run(["git", "add", "."], cwd=self.repo, check=True)
        subprocess.run(
            ["git", "-c", "user.name=Test", "-c", "user.email=test@example.invalid",
             "commit", "-qm", "physical line fixture"], cwd=self.repo, check=True,
        )
        self._build()
        found = fts5.search(self.repo, "Authorization", ["docs"],
                            db=self.db, mode="indexed")
        native_result = native.search_sources(self.repo, "Authorization", ["docs"])
        self.assertEqual(found["results"], native_result["results"])
        self.assertIn(
            {"ref": "docs/unicode_lines.md#L2",
             "preview": "Authorization must remain."},
            found["results"],
        )


    def test_auto_preserves_native_hits_excluded_by_partial_fts_index(self):
        (self.repo / "docs" / "binary.dat").write_bytes(b"\x00" + b"ignored")
        subprocess.run(["git", "add", "."], cwd=self.repo, check=True)
        subprocess.run(
            ["git", "-c", "user.name=Test", "-c", "user.email=test@example.invalid",
             "commit", "-qm", "binary scanned incompletely"],
            cwd=self.repo, check=True,
        )
        self._build()
        direct = native.search_sources(self.repo, "API_TOKEN", ["docs"])
        self.assertEqual(direct["status"], "incomplete")
        self.assertIn("docs/.env#L1", [x["ref"] for x in direct["results"]])
        joined = fts5.search(self.repo, "API_TOKEN", ["docs"],
                             db=self.db, mode="auto", enable_optional=True)
        self.assertTrue(joined["index_used"])
        self.assertEqual(joined["backend"], "native+sqlite-fts5")
        self.assertEqual(joined["status"], "incomplete")
        self.assertEqual(joined["results"], direct["results"])
        self.assertEqual(joined["native_hits_preserved"], 1)

    def test_auto_deduplicates_overlapping_native_and_indexed_hits(self):
        (self.repo / "docs" / "binary.dat").write_bytes(b"\x00" + b"ignored")
        subprocess.run(["git", "add", "."], cwd=self.repo, check=True)
        subprocess.run(
            ["git", "-c", "user.name=Test", "-c", "user.email=test@example.invalid",
             "commit", "-qm", "binary scanned incompletely"],
            cwd=self.repo, check=True,
        )
        self._build()
        direct = native.search_sources(self.repo, "authorization", ["docs"])
        self.assertEqual(direct["status"], "incomplete")
        joined = fts5.search(self.repo, "authorization", ["docs"],
                             db=self.db, mode="auto", enable_optional=True)
        self.assertEqual(joined["status"], "incomplete")
        self.assertEqual(joined["results"], direct["results"])
        self.assertEqual(len(joined["results"]), 1)

    def test_literal_query_quote_is_not_executable_fts_syntax(self):
        self._build()
        result = fts5.search(self.repo, 'authorization" OR secret', ["docs"],
                             db=self.db, mode="indexed")
        self.assertEqual(result["results"], [])


if __name__ == "__main__":
    unittest.main()
