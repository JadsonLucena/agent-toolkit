"""Regression tests for the Claude-format adapter's declared canonical coverage."""
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from claude_plugin_lint import canonical_files, lint_claude_plugin  # noqa: E402


class ClaudePluginTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        shutil.copytree(ROOT / "contexts", self.root / "contexts")
        for folder in (".claude-plugin", ".cursor-plugin"):
            (self.root / folder).mkdir(parents=True)
            shutil.copy2(ROOT / folder / "plugin.json",
                         self.root / folder / "plugin.json")
        self.manifest_path = self.root / ".claude-plugin/plugin.json"

    def manifest(self):
        return json.loads(self.manifest_path.read_text(encoding="utf-8"))

    def write(self, manifest):
        self.manifest_path.write_text(
            json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
        )

    def assert_issue(self, needle):
        errors = lint_claude_plugin(self.root)
        self.assertTrue(any(needle in error for error in errors), errors)

    def test_current_plugin_exposes_all_canonical_components_without_copy(self):
        self.assertEqual([], lint_claude_plugin(self.root))
        manifest = self.manifest()
        self.assertEqual(8, len(manifest["skills"]))
        self.assertEqual(20, len(canonical_files(self.root, "skills")))
        self.assertEqual(18, len(canonical_files(self.root, "commands")))
        self.assertEqual(17, len(canonical_files(self.root, "agents")))
        self.assertEqual(18, len(manifest["commands"]))
        self.assertEqual(17, len(manifest["agents"]))
        self.assertNotIn("rules", manifest)
        self.assertNotIn("hooks", manifest)
        self.assertNotIn("mcpServers", manifest)

    def test_missing_one_agent_is_detected(self):
        manifest = self.manifest()
        manifest["agents"].pop()
        self.write(manifest)
        self.assert_issue("agents coverage mismatch")

    def test_missing_one_command_is_detected(self):
        manifest = self.manifest()
        manifest["commands"].pop()
        self.write(manifest)
        self.assert_issue("commands coverage mismatch")

    def test_missing_skill_directory_is_detected(self):
        manifest = self.manifest()
        manifest["skills"].pop()
        self.write(manifest)
        self.assert_issue("skills coverage mismatch")

    def test_duplicate_command_path_is_detected(self):
        manifest = self.manifest()
        manifest["commands"].append(manifest["commands"][0])
        self.write(manifest)
        self.assert_issue("duplicate commands artifact")

    def test_directory_in_agents_is_not_accepted(self):
        manifest = self.manifest()
        manifest["agents"] = ["./contexts/review/agents"]
        self.write(manifest)
        self.assert_issue("invalid agents path")

    def test_missing_target_is_detected(self):
        manifest = self.manifest()
        manifest["agents"][0] = "./contexts/review/agents/not-a-real-agent.md"
        self.write(manifest)
        self.assert_issue("invalid agents path")

    def test_traversal_is_rejected(self):
        manifest = self.manifest()
        manifest["commands"][0] = "./../other-repo/untrusted.md"
        self.write(manifest)
        self.assert_issue("unsafe commands path")

    def test_symlink_escaping_package_is_rejected(self):
        manifest = self.manifest()
        manifest["commands"][0] = "./external.md"
        foreign = tempfile.TemporaryDirectory()
        self.addCleanup(foreign.cleanup)
        external = Path(foreign.name) / "foreign-command.md"
        external.write_text("---\nname: external\ndescription: x\n---\n", encoding="utf-8")
        (self.root / "external.md").symlink_to(external)
        self.write(manifest)
        self.assert_issue("escaping commands path")

    def test_name_must_match_canonical_filename(self):
        target = self.root / "contexts/review/agents/code-reviewer.md"
        content = target.read_text(encoding="utf-8")
        self.assertIn("name: code-reviewer", content)
        target.write_text(
            content.replace("name: code-reviewer", "name: unrelated", 1),
            encoding="utf-8"
        )
        self.assert_issue("invalid agents identity")

    def test_description_consistency_is_required(self):
        manifest = self.manifest()
        manifest["description"] = "Unrelated product."
        self.write(manifest)
        self.assert_issue("public descriptions must match Cursor")

    def test_rules_cannot_be_silently_listed_as_supported_component(self):
        manifest = self.manifest()
        manifest["rules"] = ["./contexts/review/rules"]
        self.write(manifest)
        self.assert_issue("unsupported manifest fields")

    def test_silent_unknown_manifest_field_is_rejected(self):
        manifest = self.manifest()
        manifest["typ0"] = "ignored by Claude Code"
        self.write(manifest)
        self.assert_issue("unsupported manifest fields")

    def test_missing_manifest_is_rejected(self):
        self.manifest_path.unlink()
        self.assert_issue("manifest is missing")

    def test_empty_author_is_rejected(self):
        manifest = self.manifest()
        manifest["author"]["name"] = " "
        self.write(manifest)
        self.assert_issue("missing author.name")


if __name__ == "__main__":
    unittest.main()
