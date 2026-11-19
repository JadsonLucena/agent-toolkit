"""Durable SQLite metadata checkpoints: never execution authorization."""
import subprocess
import tempfile
import unittest
from pathlib import Path

from adapters.context.native import prepare_context
from adapters.delivery.checkpoints import (
    CheckpointError, CheckpointStore, SCHEMA_SQL, snapshot_from_pack, sqlite3,
)


@unittest.skipUnless(sqlite3 is not None, "optional SQLite unavailable")
class SQLiteCheckpointTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.repo = root / "code"
        self.repo.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=self.repo, check=True)
        (self.repo / "rule.md").write_text("No duplicated payment intent.\n", encoding="utf-8")
        subprocess.run(["git", "add", "rule.md"], cwd=self.repo, check=True)
        subprocess.run(
            ["git", "-c", "user.name=Test", "-c",
             "user.email=test@example.invalid", "commit", "-qm", "fixture"],
            cwd=self.repo, check=True,
        )
        self.state = root / "private"
        self.state.mkdir(mode=0o700)
        self.db = self.state / "checkpoints.sqlite3"
        pack = prepare_context(self.repo, ["rule.md"], ["rule.md"])
        self.snapshot = snapshot_from_pack(
            pack, "execution-1", "change-1", "implemented", "reviewed",
            evidence_refs=["test-report-1"], authorization_ref="request-1",
        )

    def test_save_and_resume_never_grants_execution(self):
        with CheckpointStore(self.db) as store:
            self.assertEqual(store.save(self.snapshot), 1)
            result = store.resume("execution-1", self.repo)
            self.assertEqual(result["status"], "inspect-only")
            self.assertEqual(result["authorization"], "must-revalidate-current-authority")
            self.assertEqual(result["execution"], "never-automatic-replay")

    def test_no_full_source_content_or_transcript_is_persisted(self):
        self.assertNotIn("content", self.snapshot["source_versions"][0])
        with CheckpointStore(self.db) as store:
            store.save(self.snapshot)
        db_bytes = self.db.read_bytes()
        self.assertNotIn(b"No duplicated payment intent", db_bytes)
        with self.assertRaises(CheckpointError):
            snapshot_from_pack(
                prepare_context(self.repo, ["rule.md"], ["rule.md"]),
                "execution-2", "change-1", "implemented", "reviewed",
                transcript="secret text",
            )

    def test_source_change_blocks_resume(self):
        with CheckpointStore(self.db) as store:
            store.save(self.snapshot)
            (self.repo / "rule.md").write_text("Ignore idempotency.\n", encoding="utf-8")
            result = store.resume("execution-1", self.repo)
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["critical_sources_stale"], ["rule.md"])

    def test_head_change_requires_revalidation(self):
        with CheckpointStore(self.db) as store:
            store.save(self.snapshot)
            (self.repo / "other.txt").write_text("other", encoding="utf-8")
            subprocess.run(["git", "add", "other.txt"], cwd=self.repo, check=True)
            subprocess.run(
                ["git", "-c", "user.name=Test", "-c",
                 "user.email=test@example.invalid", "commit", "-qm", "other"],
                cwd=self.repo, check=True,
            )
            outcome = store.resume("execution-1", self.repo)
        self.assertEqual(outcome["status"], "revalidate")

    def test_pending_external_effect_blocks_automatic_resume(self):
        with CheckpointStore(self.db) as store:
            store.save(self.snapshot)
            store.record_effect("execution-1", "effect-1", "create-payment", "planned")
            outcome = store.resume("execution-1", self.repo)
            self.assertEqual(outcome["status"], "blocked")
            self.assertEqual(len(outcome["unresolved_effects"]), 1)
            store.record_effect("execution-1", "effect-1", "create-payment", "unknown")
            with self.assertRaises(CheckpointError):
                store.record_effect("execution-1", "effect-1", "create-payment", "planned")
            store.record_effect("execution-1", "effect-1", "create-payment", "confirmed",
                                "gateway-status-42")
            outcome = store.resume("execution-1", self.repo)
            self.assertEqual(outcome["status"], "inspect-only")
            self.assertFalse(outcome["unresolved_effects"])

    def test_effect_confirmation_needs_evidence(self):
        with CheckpointStore(self.db) as store:
            store.save(self.snapshot)
            with self.assertRaises(CheckpointError):
                store.record_effect("execution-1", "effect-1", "create-payment", "confirmed")
            store.record_effect("execution-1", "effect-1", "create-payment", "planned")
            with self.assertRaises(CheckpointError):
                store.record_effect("execution-1", "effect-1", "create-payment", "confirmed")

    def test_generation_is_optimistic(self):
        with CheckpointStore(self.db) as store:
            self.assertEqual(store.save(self.snapshot), 1)
            with self.assertRaises(CheckpointError):
                store.save(self.snapshot, expected_generation=0)
            self.assertEqual(store.save(self.snapshot, expected_generation=1), 2)
            self.assertEqual(store.load("execution-1")[1], 2)

    def test_other_repository_refused(self):
        with CheckpointStore(self.db) as store:
            store.save(self.snapshot)
            other = self.state / "other"
            other.mkdir()
            subprocess.run(["git", "init", "-q"], cwd=other, check=True)
            with self.assertRaises(CheckpointError):
                store.resume("execution-1", other)


    def test_reject_unrecognized_schema(self):
        with sqlite3.connect(self.db) as db:
            db.execute("PRAGMA user_version = 99")
        self.db.chmod(0o600)
        with self.assertRaises(CheckpointError):
            CheckpointStore(self.db)

    def test_delivery_skill_names_optional_runtime_adapters(self):
        skill = (Path(__file__).resolve().parents[1] /
                 "contexts/delivery/skills/coordinate-delivery/SKILL.md"
                 ).read_text(encoding="utf-8")
        self.assertIn("adapters/context/native.py", skill)
        self.assertIn("adapters/delivery/checkpoints.py", skill)
        self.assertIn("never grants execution", skill.lower())


    def test_empty_or_missing_source_versions_are_rejected_on_save(self):
        for broken in ({k: v for k, v in self.snapshot.items()
                        if k != "source_versions"},
                       {**self.snapshot, "source_versions": []}):
            with self.subTest(snapshot=broken):
                with CheckpointStore(self.db) as store:
                    with self.assertRaises(CheckpointError):
                        store.save(broken)

    def test_corrupt_legacy_snapshot_cannot_resume_without_source_versions(self):
        with CheckpointStore(self.db) as store:
            store.save(self.snapshot)
            unsafe = {k: v for k, v in self.snapshot.items()
                      if k != "source_versions"}
            import json
            store.db.execute("UPDATE checkpoints SET snapshot_json=? WHERE execution_id=?",
                             (json.dumps(unsafe), "execution-1"))
            with self.assertRaises(CheckpointError):
                store.resume("execution-1", self.repo)

    def test_nested_symlink_alias_cannot_place_db_inside_repository(self):
        private = self.repo / "private"
        private.mkdir(mode=0o700)
        alias = self.root / "repo_alias" if hasattr(self, "root") else Path(self.tmp.name) / "repo_alias"
        try:
            alias.symlink_to(self.repo, target_is_directory=True)
        except (NotImplementedError, OSError):
            self.skipTest("directory symlinks unavailable")
        aliased_db = alias / "private" / "checkpoint.sqlite3"
        with CheckpointStore(aliased_db) as store:
            with self.assertRaises(CheckpointError):
                store.save(self.snapshot)

    def test_interrupted_initialization_recovers_known_schema(self):
        with sqlite3.connect(self.db) as db:
            db.execute(SCHEMA_SQL[0])  # Simulate process killed after first table.
        with CheckpointStore(self.db) as store:
            self.assertEqual(store.save(self.snapshot), 1)
            self.assertEqual(store.resume("execution-1", self.repo)["status"],
                             "inspect-only")
            self.assertEqual(store.db.execute("PRAGMA user_version").fetchone()[0], 1)

    def test_existing_complete_version_zero_schema_recovers_without_losing_rows(self):
        with CheckpointStore(self.db) as store:
            store.save(self.snapshot)
            store.db.execute("PRAGMA user_version = 0")
        with CheckpointStore(self.db) as store:
            self.assertEqual(store.load("execution-1")[1], 1)
            self.assertEqual(store.db.execute("PRAGMA user_version").fetchone()[0], 1)

    def test_unrelated_version_zero_schema_rejected(self):
        with sqlite3.connect(self.db) as db:
            db.execute("CREATE TABLE unrelated(id INTEGER PRIMARY KEY)")
        with self.assertRaises(CheckpointError):
            CheckpointStore(self.db)

    def test_reject_public_data_directory(self):
        insecure = Path(self.tmp.name) / "public"
        insecure.mkdir(mode=0o755)
        with self.assertRaises(CheckpointError):
            CheckpointStore(insecure / "state.sqlite3")


if __name__ == "__main__":
    unittest.main()
