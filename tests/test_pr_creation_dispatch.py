"""Structural checks for host-level Git PR creation routing and pilot fixtures."""

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from requirements_evals import load_catalog, evaluate  # noqa: E402


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


class PullRequestCreationDispatchTests(unittest.TestCase):
    def test_host_instruction_routes_every_remote_creation_through_command(self):
        route = read("AGENTS.md")
        for text in (
            "Crie o PR",
            "Abra um pull request",
            "Publish this PR",
            "Implement and create a PR",
            "contexts/git/commands/create-pull-request.md",
            "sole publication entry point",
            "gh pr create",
            "hosting-provider API",
            "MCP connector",
            "before skill selection",
        ):
            self.assertIn(text.lower(), route.lower())
        self.assertIn("must hand off publication", route)
        self.assertIn("Do not fall back to direct PR creation", route)

    def test_git_keeps_sole_readiness_authority_and_advisory_review(self):
        route = read("AGENTS.md")
        command = read("contexts/git/commands/create-pull-request.md")
        policy = read("contexts/git/rules/pull-request.md")
        self.assertIn("contexts/git/rules/pull-request.md", route)
        self.assertNotIn("review_profile=advisory", route)  # no copied gate procedure
        self.assertIn("review_profile=advisory", command)
        self.assertIn("no second authorization", policy)
        self.assertIn("exact head/base", policy)
        self.assertIn("explicitly authorized", policy)
        self.assertIn("cannot intercept unrestricted", route)

    def test_nonpublication_intents_and_host_limit_are_explicit(self):
        route = read("AGENTS.md")
        readme = read("README.md")
        for phrase in ("plan PR boundaries", "prepare descriptions", "review code"):
            self.assertIn(phrase, route)
        self.assertIn("not publication requests", route)
        self.assertIn("AGENTS.md", readme)
        self.assertIn("not a tool-level authorization gate", readme)
        self.assertIn("install", readme.lower())

    def test_dispatch_pilots_require_actual_agent_observations(self):
        catalog = load_catalog(ROOT / "evals/git/pr-creation-routing.json")
        self.assertEqual(7, len(catalog["cases"]))
        self.assertEqual({f"PR-{i:02d}" for i in range(1, 8)},
                         {case["id"] for case in catalog["cases"]})
        self.assertTrue(all(len(case["checks"]) == 3 for case in catalog["cases"]))
        self.assertTrue(all(
            case["command"] in ("/git/create-pull-request", "/git/plan-pull-requests")
            for case in catalog["cases"]
        ))
        summary = evaluate(catalog, {"version": 1, "assessments": []}, ROOT / "evals/git")
        self.assertEqual("INCOMPLETE", summary["status"])
        self.assertEqual(7, summary["incomplete"])


if __name__ == "__main__":
    unittest.main()
