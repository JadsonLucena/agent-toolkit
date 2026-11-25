"""Regression checks for editorial drift, not behavioral host guarantees."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


class EditorialConsistencyTests(unittest.TestCase):
    def test_no_hard_coded_cursor_component_counts(self):
        text = read(".cursor-plugin/README.md")
        self.assertNotIn("seven contexts", text)
        self.assertNotIn("14 Rules", text)
        self.assertNotIn("14 canonical", text)

    def test_adapter_markdown_fences_are_not_escaped(self):
        readme = read("adapters/github/README.md")
        self.assertNotIn("\\`", readme)
        self.assertIn("```json", readme)
        self.assertIn("```bash", readme)

    def test_optional_ocr_version_lives_outside_canonical_diagram(self):
        diagram = read("contexts/review/skills/review-change/SKILL.md")
        self.assertNotIn("OCR >= 1.9", diagram)
        self.assertIn("Optional OCR capability check", diagram)
        cli = read("contexts/review/commands/review-code.md")
        inputs = cli.split("## Inputs", 1)[1].split("## Output", 1)[0]
        self.assertNotIn("--task-capable", inputs)
        self.assertIn("adapters/review/README.md", cli)

    def test_detail_constraints_do_not_replay_numbered_workflow(self):
        el = read("contexts/requirements/skills/elicitation/SKILL.md")
        section = el.split("### Decision-frontier interview protocol", 1)[1].split(
            "## Output", 1
        )[0]
        self.assertFalse(re.search(r"(?m)^\d+\.", section))
        fb = read("contexts/delivery/skills/assess-feedback/SKILL.md")
        workflow = fb.split("## Workflow", 1)[1].split("## Output", 1)[0]
        self.assertFalse(re.search(r"(?m)^\\d+\\.", workflow))

    def test_branch_policy_does_not_outlaw_trunk_based_work(self):
        git = read("contexts/git/rules/git.md")
        self.assertIn("including trunk-based development", git)
        self.assertIn("outside Git's internal", git)


if __name__ == "__main__":
    unittest.main()
