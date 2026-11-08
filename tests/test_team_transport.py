"""Contract tests for the optional, provider-neutral peer message transport."""
from __future__ import annotations

import asyncio
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "adapters" / "teams"))
from peer_bus import PeerBus, TeamError  # noqa: E402


class ReviewTeamTransportTests(unittest.IsolatedAsyncioTestCase):
    async def test_direct_cross_specialist_challenge_and_reply(self):
        bus = PeerBus({"correctness", "reliability"}, "head-abc", "base-def")

        async def correctness(ctx, name):
            first = await ctx.send(
                name, "reliability", "challenge", "Can a retry charge twice?",
                ["billing.py:32"], target_head_sha="head-abc",
            )
            reply = await ctx.receive(name)
            self.assertEqual("response", reply["kind"])
            self.assertEqual(first["message_id"], reply["response_to"])
            self.assertEqual(first["thread_id"], reply["thread_id"])
            return "question resolved"

        async def reliability(ctx, name):
            request = await ctx.receive(name)
            self.assertEqual("challenge", request["kind"])
            await ctx.send(
                name, "correctness", "response", "The idempotency key is absent",
                ["payments.py:18"], thread_id=request["thread_id"],
                response_to=request["message_id"], target_head_sha="head-abc",
            )
            return "evidence checked"

        result = await bus.run({"correctness": correctness, "reliability": reliability})
        self.assertEqual(2, len(result["peer_threads"]))
        self.assertEqual(["correctness", "reliability"], result["participants"])
        self.assertEqual("team-relayed", result["execution_mode"])
        self.assertFalse(result["independent_agents_executed"])
        self.assertIsNone(result["review_verdict"])

    async def test_stale_message_is_rejected(self):
        bus = PeerBus({"a", "b"}, "head-abc", "base-def")
        with self.assertRaisesRegex(TeamError, "stale"):
            await bus.send("a", "b", "question", "check invariant",
                           ["source.py:1"], target_head_sha="other-head")
        self.assertEqual([], bus.ledger)

    async def test_unknown_peer_is_rejected(self):
        bus = PeerBus({"a", "b"}, "head", "base")
        with self.assertRaisesRegex(TeamError, "invalid peer"):
            await bus.send("a", "unknown", "question", "check?", ["file:3"])

    async def test_missing_role_blocks_instead_of_faking_team(self):
        bus = PeerBus({"a", "b"}, "head", "base")
        with self.assertRaisesRegex(TeamError, "every selected role"):
            await bus.run({"a": lambda b, r: None})

    async def test_unanswered_challenge_blocks_completion(self):
        bus = PeerBus({"a", "b"}, "head", "base")

        async def sender(ctx, name):
            await ctx.send(name, "b", "challenge", "respond", ["x:1"])
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


if __name__ == "__main__":
    unittest.main()
