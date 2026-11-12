"""Structural regression for SDLC coverage and controlled execution policy."""

from pathlib import Path
import unittest

ARCH = (Path(__file__).resolve().parents[1] / "ARCHITECTURE.md").read_text(encoding="utf-8")


class SddLifecyclePolicyTests(unittest.TestCase):
    def test_stages_do_not_conflate_deployment_with_verification(self):
        block = ARCH.split("## SDLC Coverage, Reversibility, and Outcome Evidence", 1)[1].split("## Controlled Iteration", 1)[0]
        for token in ("specification", "PR ready", "deployed", "outcome demonstrated", "distinct evidence claims"):
            with self.subTest(token=token):
                self.assertIn(token, block)

    def test_rollback_is_not_revert(self):
        block = ARCH.split("## SDLC Coverage, Reversibility, and Outcome Evidence", 1)[1].split("## Controlled Iteration", 1)[0]
        for token in ("Git commit", "compensation", "reconciliation", "irreversible"):
            self.assertIn(token, block)

    def test_loops_and_parallel_work_are_bounded(self):
        loop = ARCH.split("## Controlled Iteration and Recovery", 1)[1].split("## Safe Parallel Work", 1)[0]
        parallel = ARCH.split("## Safe Parallel Work", 1)[1].split("## Change Boundary", 1)[0]
        for token in ("stop condition", "checkpoint", "authorization", "externally observable", "Independent review"):
            self.assertIn(token.lower(), loop.lower())
        for token in ("isolation", "stale", "synchronization", "immutable"):
            self.assertIn(token.lower(), parallel.lower())


if __name__ == "__main__":
    unittest.main()
