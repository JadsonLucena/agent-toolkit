"""Behavioral regression tests for pinned, read-only Cloudflare guidance loading."""
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "adapters/security-audit"))
from resolve import DEFAULT_ROOT, LOCK_PATH, adapter, content_hash  # noqa: E402


class SecurityAuditAdapterTests(unittest.TestCase):
    def test_bundled_skill_matches_reviewed_lock(self):
        result = adapter(changed_files=["src/auth/session.py", "src/agent/mcp.py"])
        self.assertEqual("available", result["status"], result)
        self.assertEqual("guidance", result["mode"])
        self.assertFalse(result["review_performed"])
        self.assertIsNone(result["review_verdict"])
        names = {item["path"] for item in result["selected_references"]}
        self.assertIn("WEB-PROTOCOL-AND-AUTH.md", names)
        self.assertIn("AI-AND-LLM.md", names)
        self.assertNotIn("MEMORY-SAFETY-AND-BINARY.md", names)

    def test_hash_matches_cli_v2_algorithm(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "SKILL.md").write_text("# hi\n", encoding="utf-8")
            self.assertEqual(
                "93c36952d8843b33e68ae970ebabcc03e1687c9bb0dd1ecaf357060318952f55",
                content_hash(root),
            )

    def test_empty_context_does_not_force_all_references(self):
        result = adapter(changed_files=[])
        self.assertEqual("available", result["status"])
        self.assertEqual([], result["selected_references"])

    def test_disabled_does_not_probe_files(self):
        result = adapter(skill_root=Path("/invalid/should/not/be/read"), enabled=False)
        self.assertEqual("disabled", result["status"])
        self.assertEqual([], result["diagnostics"])

    def test_absent_skill_is_nonblocking(self):
        with tempfile.TemporaryDirectory() as directory:
            result = adapter(skill_root=Path(directory) / "missing")
            self.assertEqual("unavailable", result["status"])
            self.assertFalse(result["review_performed"])

    def test_unapproved_directory_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "security-audit"
            shutil.copytree(DEFAULT_ROOT, root)
            (root / "SKILL.md").write_text("malicious change\n", encoding="utf-8")
            self.assertEqual("rejected", adapter(skill_root=root)["status"])

    def test_additional_unapproved_file_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "security-audit"
            shutil.copytree(DEFAULT_ROOT, root)
            (root / "extra.md").write_text("unreviewed\n", encoding="utf-8")
            self.assertEqual("rejected", adapter(skill_root=root)["status"])

    def test_explicit_copy_with_matching_hash_is_approved(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "security-audit"
            shutil.copytree(DEFAULT_ROOT, root)
            result = adapter(skill_root=root)
            self.assertEqual("available", result["status"], result)

    def test_symlink_escape_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "security-audit"
            shutil.copytree(DEFAULT_ROOT, root)
            outside = Path(directory) / "external"
            outside.write_text("malicious\n", encoding="utf-8")
            try:
                (root / "escape.md").symlink_to(outside)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks unavailable on this platform")
            self.assertEqual("rejected", adapter(skill_root=root)["status"])

    def test_explicit_topic_covers_financial_operation_without_filename_hint(self):
        without = adapter(changed_files=["src/billing/charge.ts"], concerns=["security"])
        self.assertEqual([], without["selected_references"])
        with_topic = adapter(
            changed_files=["src/billing/charge.ts"], concerns=["security"],
            topics=["business-integrity"],
        )
        self.assertEqual("available", with_topic["status"])
        self.assertFalse(with_topic["review_performed"])
        names = {item["path"] for item in with_topic["selected_references"]}
        self.assertIn("PROTOCOLS-RPC-AND-MESSAGING.md", names)
        self.assertIn("DATA-ISOLATION-AND-LIFECYCLE.md", names)
        self.assertTrue(all("explicit security topic" in item["reason"]
                            for item in with_topic["selected_references"]))

    def test_topic_selection_is_bounded_deduplicated_and_non_authoritative(self):
        result = adapter(
            changed_files=["src/auth/session.py"],
            topics=["authorization", "authorization", "bogus;external"],
        )
        names = [item["path"] for item in result["selected_references"]]
        self.assertEqual(len(names), len(set(names)))
        self.assertIn("WEB-PROTOCOL-AND-AUTH.md", names)
        self.assertIn("DATA-ISOLATION-AND-LIFECYCLE.md", names)
        self.assertTrue(any("unrecognized" in d for d in result["diagnostics"]))
        self.assertNotIn("bogus;external", str(result["diagnostics"]))
        self.assertIsNone(result["review_verdict"])

    def test_explicit_topics_do_not_override_disabled_or_rejected_helper(self):
        self.assertEqual("disabled", adapter(enabled=False, topics=["authorization"])["status"])
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "unapproved"
            shutil.copytree(DEFAULT_ROOT, root)
            (root / "SKILL.md").write_text("# changed\\n", encoding="utf-8")
            result = adapter(skill_root=root, topics=["authorization"])
            self.assertEqual("rejected", result["status"])
            self.assertEqual([], result["selected_references"])

    def test_tampered_lock_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            lock = Path(directory) / "skills-lock.json"
            lock.write_text('{"version":2,"skills":{"security-audit":{}}}', encoding="utf-8")
            self.assertEqual("rejected", adapter(lock_path=lock)["status"])

    def test_lock_and_bundle_are_present(self):
        self.assertTrue(DEFAULT_ROOT.joinpath("SKILL.md").is_file())
        self.assertTrue(LOCK_PATH.is_file())


if __name__ == "__main__":
    unittest.main()
