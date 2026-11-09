"""Contract tests for evidence-linked, bounded Review Team peer messaging."""
from __future__ import annotations

import asyncio
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "adapters" / "teams"))
from peer_bus import PeerBus, TeamError  # noqa: E402


class ReviewTeamTransportTests(unittest.IsolatedAsyncioTestCase):
    async def test_challenge_response_resolution_carries_provenance(self):
        bus = PeerBus({"correctness", "reliability"}, "head-abc", "base-def", review_id="review-14")

        async def correctness(ctx, name):
            challenge = await ctx.send(
                name, "reliability", "challenge", "Can retries charge twice?",
                ["billing.py:32"], requested_action="Inspect idempotency on retries",
                target_head_sha="head-abc", review_id="review-14",
            )
            reply = await ctx.receive(name)
            self.assertEqual("response", reply["kind"])
            self.assertEqual(challenge["message_id"], reply["response_to"])
            self.assertEqual(challenge["thread_id"], reply["thread_id"])
            await ctx.send(
                name, "reliability", "resolution", "Finding supported by trace",
                ["payments.py:18"], response_to=reply["message_id"],
            )
            return "challenge resolved"

        async def reliability(ctx, name):
            request = await ctx.receive(name)
            self.assertEqual("challenge", request["kind"])
            self.assertEqual("review-14", request["review_id"])
            self.assertEqual("Inspect idempotency on retries", request["requested_action"])
            await ctx.send(
                name, "correctness", "response", "Idempotency key is absent",
                ["payments.py:18"], response_to=request["message_id"],
                target_head_sha="head-abc",
            )
            resolved = await ctx.receive(name)
            self.assertEqual("resolution", resolved["kind"])
            return "evidence checked"

        out = await bus.run({"correctness": correctness, "reliability": reliability})
        self.assertEqual(3, len(out["peer_threads"]))
        self.assertEqual("review-14", out["review_id"])
        self.assertEqual(["correctness", "reliability"], out["participants"])
        self.assertEqual(["resolved"], list(out["thread_states"].values()))
        self.assertEqual("team-relayed", out["execution_mode"])
        self.assertFalse(out["independent_agents_executed"])
        self.assertIsNone(out["review_verdict"])

    async def test_unanswered_question_blocks_even_when_handlers_finish(self):
        bus = PeerBus({"a", "b"}, "head", "base")

        async def a(ctx, name):
            await ctx.send(name, "b", "question", "Where is retry guard?",
                           ["x:1"], requested_action="Find retry guard")

        async def b(ctx, name):
            await ctx.receive(name)
            return "nothing"

        with self.assertRaisesRegex(TeamError, "unresolved peer threads"):
            await bus.run({"a": a, "b": b})

    async def test_answer_without_resolution_does_not_pass(self):
        bus = PeerBus({"a", "b"}, "head", "base")

        async def a(ctx, name):
            await ctx.send(name, "b", "challenge", "Check race",
                           ["x:1"], requested_action="Prove ordering")
            await ctx.receive(name)

        async def b(ctx, name):
            first = await ctx.receive(name)
            await ctx.send(name, "a", "response", "Not ordered", ["x:4"],
                           response_to=first["message_id"])

        with self.assertRaisesRegex(TeamError, "unresolved peer threads"):
            await bus.run({"a": a, "b": b})

    async def test_response_to_unknown_message_is_rejected(self):
        bus = PeerBus({"a", "b"}, "head", "base")
        with self.assertRaisesRegex(TeamError, "unknown message"):
            await bus.send("a", "b", "response", "yes", ["x:1"],
                           response_to="does-not-exist")

    async def test_other_peer_cannot_resolve_challenge(self):
        bus = PeerBus({"a", "b", "c"}, "head", "base")
        req = await bus.send("a", "b", "question", "question", ["x:1"],
                             requested_action="investigate")
        with self.assertRaisesRegex(TeamError, "does not match an open"):
            await bus.send("c", "a", "response", "spoof", ["x:1"],
                           response_to=req["message_id"])

    async def test_stale_message_is_rejected(self):
        bus = PeerBus({"a", "b"}, "head", "base", review_id="run1")
        with self.assertRaisesRegex(TeamError, "stale review target"):
            await bus.send("a", "b", "question", "check invariant",
                           ["source.py:1"], requested_action="Inspect",
                           target_head_sha="other-head")
        with self.assertRaisesRegex(TeamError, "stale review identity"):
            await bus.send("a", "b", "question", "check invariant",
                           ["source.py:1"], requested_action="Inspect",
                           review_id="run2")
        self.assertEqual([], bus.ledger)

    async def test_unknown_peer_is_rejected(self):
        bus = PeerBus({"a", "b"}, "head", "base")
        with self.assertRaisesRegex(TeamError, "invalid peer"):
            await bus.send("a", "unknown", "question", "check?", ["file:3"],
                           requested_action="Check")

    async def test_missing_role_blocks(self):
        bus = PeerBus({"a", "b"}, "head", "base")
        with self.assertRaisesRegex(TeamError, "every selected role"):
            await bus.run({"a": lambda b, r: None})

    async def test_unanswered_challenge_blocks_on_timeout(self):
        bus = PeerBus({"a", "b"}, "head", "base")

        async def sender(ctx, name):
            await ctx.send(name, "b", "challenge", "respond", ["x:1"],
                           requested_action="Respond")
            await ctx.receive(name, timeout=0.01)

        async def receiver(ctx, name):
            await asyncio.sleep(0.05)

        with self.assertRaisesRegex(TeamError, "did not complete"):
            await bus.run({"a": sender, "b": receiver}, timeout=0.1)

    async def test_bounded_message_ledger(self):
        bus = PeerBus({"a", "b"}, "head", "base", max_messages=1)
        await bus.send("a", "b", "observation", "one", ["x:1"])
        with self.assertRaisesRegex(TeamError, "budget"):
            await bus.send("a", "b", "observation", "two", ["x:2"])

    async def test_question_requires_explicit_requested_action(self):
        bus = PeerBus({"a", "b"}, "head", "base")
        with self.assertRaisesRegex(TeamError, "requested_action"):
            await bus.send("a", "b", "challenge", "check something", ["x:1"])


if __name__ == "__main__":
    unittest.main()
