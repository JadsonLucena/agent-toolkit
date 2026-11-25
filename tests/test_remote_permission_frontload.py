"""Structural guardrails for high-impact remote operation permissions.

Host authorization and Rule loading still require real tool traces.
"""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


class RemotePermissionFrontloadTests(unittest.TestCase):
    def test_git_skill_frontloads_push_separation_and_rule_loading(self):
        skill = read("contexts/git/skills/manage-pull-request/SKILL.md")
        front = skill.split("## Uses", 1)[0]
        self.assertIn("Creating a PR never authorizes pushing a branch", front)
        self.assertIn("retrieve and apply", front)
        self.assertIn("Listing a Rule", front)

    def test_delivery_frontloads_remote_authority_and_source_loading(self):
        skill = read("contexts/delivery/skills/coordinate-delivery/SKILL.md")
        front = skill.split("## Uses", 1)[0]
        self.assertIn("separate authorization decisions", front)
        self.assertIn("retrieve the **next owner's applicable canonical Rule", front)

    def test_rule_and_command_separate_publication_authority(self):
        self.assertIn("Creating a PR does not authorize a push",
                      read("contexts/git/rules/pull-request.md").split("## Core Principle", 1)[0])
        command = read("contexts/git/commands/create-pull-request.md")
        self.assertIn("PR creation permission does not grant push permission",
                      command.split("## Uses", 1)[0])

    def test_optional_cursor_hook_guidance_does_not_promise_enforcement(self):
        doc = read(".cursor-plugin/README.md")
        self.assertIn("failClosed: true", doc)
        self.assertIn("A string-matching shell hook cannot prove user authorization", doc)
        self.assertIn("None of these safeguards are installed by this plugin", doc)


if __name__ == "__main__":
    unittest.main()
