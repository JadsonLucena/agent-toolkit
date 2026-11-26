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
        self.assertIn("explicit PR-creation request can authorize first-time publication", front)
        self.assertIn("retrieve and apply", front)
        self.assertIn("Listing a Rule", front)

    def test_delivery_frontloads_remote_authority_and_source_loading(self):
        skill = read("contexts/delivery/skills/coordinate-delivery/SKILL.md")
        front = skill.split("## Uses", 1)[0]
        self.assertIn("target stage or implementation alone does not authorize push", front)
        self.assertIn("retrieve the **next owner's applicable canonical Rule", front)

    def test_rule_and_command_separate_publication_authority(self):
        self.assertIn("An explicit request to create a remote PR authorizes only its necessary first-time",
                      read("contexts/git/rules/pull-request.md").split("## Core Principle", 1)[0])
        command = read("contexts/git/commands/create-pull-request.md")
        self.assertIn("explicit PR-creation request may include",
                      command.split("## Uses", 1)[0])

    def test_bounded_first_publication_never_grants_remote_ref_update(self):
        rule = read("contexts/git/rules/pull-request.md")
        git_rule = read("contexts/git/rules/git.md")
        command = read("contexts/git/commands/create-pull-request.md")
        self.assertIn("existing remote branch", rule)
        self.assertIn("different SHA", rule)
        self.assertIn("does not authorize publication", git_rule)
        self.assertIn("explicitly prohibited by the user", command)

    def test_architecture_agrees_on_conditional_pr_publication(self):
        architecture = read("ARCHITECTURE.md")
        self.assertIn("only the necessary first-time non-force publication", architecture)
        self.assertIn("does not authorize updating existing remote refs", architecture)
        self.assertNotIn("creation-only authorization", architecture)

    def test_optional_cursor_hook_guidance_does_not_promise_enforcement(self):
        doc = read(".cursor-plugin/README.md")
        self.assertIn("failClosed: true", doc)
        self.assertIn("A string-matching shell hook cannot prove user authorization", doc)
        self.assertIn("None of these safeguards are installed by this plugin", doc)


if __name__ == "__main__":
    unittest.main()
