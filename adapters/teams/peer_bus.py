"""Bounded, provider-neutral Review Team peer communication.

Handlers supplied by the host are NOT independent model agents. In-process
coroutines cannot establish independent review or a team-live verdict.
"""
from __future__ import annotations

import asyncio
import uuid
from collections.abc import Awaitable, Callable, Mapping
from typing import Any

KINDS = {"observation", "question", "challenge", "response", "escalation", "resolution"}
OPEN_REQUESTS = {"question", "challenge", "escalation"}


class TeamError(Exception):
    """Untrusted, unresolved or incomplete agent collaboration."""


class PeerBus:
    def __init__(
        self, roles: set[str], head_sha: str, base_sha: str,
        *, review_id: str | None = None, max_messages: int = 500,
    ):
        if len(roles) < 2 or any(not isinstance(r, str) or not r.strip() for r in roles):
            raise ValueError("at least two named specialist roles are required")
        if not head_sha or not base_sha or max_messages < 1 or (review_id is not None and not review_id):
            raise ValueError("review identity, target and message budget are required")
        self.roles = frozenset(roles)
        self.review_id = review_id or uuid.uuid4().hex
        self.max_messages = max_messages
        self.head_sha = head_sha
        self.base_sha = base_sha
        self.queues: dict[str, asyncio.Queue[dict[str, Any]]] = {r: asyncio.Queue() for r in roles}
        self.ledger: list[dict[str, Any]] = []
        self.by_id: dict[str, dict[str, Any]] = {}
        self.threads: dict[str, dict[str, Any]] = {}

    async def send(
        self, sender: str, recipient: str, kind: str, subject: str,
        evidence_refs: list[str], *, thread_id: str | None = None,
        response_to: str | None = None, requested_action: str | None = None,
        target_head_sha: str | None = None, review_id: str | None = None,
    ) -> dict[str, Any]:
        if sender not in self.roles or recipient not in self.roles or sender == recipient:
            raise TeamError("unknown or invalid peer")
        if kind not in KINDS or not isinstance(subject, str) or not subject.strip():
            raise TeamError("invalid peer message")
        if len(subject) > 5000 or not isinstance(evidence_refs, list) or len(evidence_refs) > 40:
            raise TeamError("message is not bounded")
        if any(not isinstance(ref, str) or not ref or len(ref) > 1000 for ref in evidence_refs):
            raise TeamError("invalid evidence reference")
        if target_head_sha is not None and target_head_sha != self.head_sha:
            raise TeamError("stale review target")
        if review_id is not None and review_id != self.review_id:
            raise TeamError("stale review identity")
        if len(self.ledger) >= self.max_messages:
            raise TeamError("message budget exceeded")
        if requested_action is not None and (not isinstance(requested_action, str) or len(requested_action) > 2000):
            raise TeamError("invalid requested_action")
        if kind in OPEN_REQUESTS and not (requested_action and requested_action.strip()):
            raise TeamError("question, challenge or escalation requires requested_action")
        previous = self.by_id.get(response_to) if response_to else None
        if response_to and not previous:
            raise TeamError("response_to references unknown message")

        if previous and thread_id is None:
            thread_id = previous["thread_id"]
        thread = self.threads.get(thread_id)
        if kind in OPEN_REQUESTS:
            if thread_id is not None or response_to is not None:
                raise TeamError("new review requests must open their own thread")
            thread_id = uuid.uuid4().hex
            thread = {
                "thread_id": thread_id, "requester_role": sender,
                "responder_role": recipient, "status": "open",
                "request_kind": kind, "messages": [],
            }
        elif kind in ("response", "resolution"):
            if not thread or not previous or previous["thread_id"] != thread["thread_id"]:
                raise TeamError("response or resolution requires a linked thread and message")
            if kind == "response":
                if (thread["status"] != "open" or sender != thread["responder_role"]
                        or recipient != thread["requester_role"]
                        or previous["kind"] not in OPEN_REQUESTS):
                    raise TeamError("response does not match an open peer request")
            else:
                if (thread["status"] != "responded" or sender != thread["requester_role"]
                        or recipient != thread["responder_role"]
                        or previous["kind"] != "response"):
                    raise TeamError("resolution requires requester acknowledgment of the response")
        elif kind == "observation":
            if thread_id is not None or response_to is not None:
                raise TeamError("standalone observations must not impersonate thread resolution")
            thread_id = uuid.uuid4().hex
        message_id = uuid.uuid4().hex
        message = {
            "review_id": self.review_id, "target_head_sha": self.head_sha,
            "target_base_sha": self.base_sha,
            "message_id": message_id, "thread_id": thread_id,
            "sender_role": sender, "recipient_role": recipient,
            "kind": kind, "subject": subject, "evidence_refs": list(evidence_refs),
            "requested_action": requested_action, "response_to": response_to,
            "status": "delivered",
        }
        if kind in OPEN_REQUESTS:
            self.threads[thread_id] = thread
        if thread:
            thread["messages"].append(message_id)
            if kind == "response":
                thread["status"] = "responded"
            elif kind == "resolution":
                thread["status"] = "resolved"
        self.by_id[message_id] = message
        self.ledger.append(message)
        await self.queues[recipient].put(message)
        return dict(message)

    async def receive(self, recipient: str, *, timeout: float = 10.0) -> dict[str, Any]:
        if recipient not in self.roles:
            raise TeamError("unknown recipient")
        try:
            message = await asyncio.wait_for(self.queues[recipient].get(), timeout=timeout)
        except asyncio.TimeoutError as exc:
            raise TeamError(f"no response for {recipient} before deadline") from exc
        message["status"] = "received"
        return dict(message)

    async def run(
        self, handlers: Mapping[str, Callable[["PeerBus", str], Awaitable[Any]]],
        *, timeout: float = 30.0,
    ) -> dict[str, Any]:
        if set(handlers) != set(self.roles) or timeout <= 0:
            raise TeamError("every selected role needs an explicit handler and positive timeout")
        tasks = {role: asyncio.create_task(handler(self, role)) for role, handler in handlers.items()}
        try:
            results = await asyncio.wait_for(asyncio.gather(*tasks.values()), timeout=timeout)
        except (Exception, asyncio.CancelledError) as exc:
            for task in tasks.values():
                task.cancel()
            await asyncio.gather(*tasks.values(), return_exceptions=True)
            raise TeamError(f"peer exchange did not complete: {type(exc).__name__}") from exc
        unresolved = sorted(t for t, data in self.threads.items() if data["status"] != "resolved")
        if unresolved:
            raise TeamError(f"unresolved peer threads: {', '.join(unresolved)}")
        return {
            "transport": "inprocess", "execution_mode": "team-relayed",
            "independent_agents_executed": False, "review_performed": False,
            "review_verdict": None, "review_id": self.review_id,
            "participants": sorted(self.roles), "peer_threads": list(self.ledger),
            "thread_states": {k: v["status"] for k, v in self.threads.items()},
            "results": dict(zip(tasks.keys(), results)),
        }
