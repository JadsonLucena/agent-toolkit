"""Small provider-neutral peer messaging transport for Review Agent Teams.

The hosting platform supplies the actual independent agent implementations.
This in-process transport proves messaging semantics; coroutines are NOT
independent model agents and cannot establish an independent review verdict.
"""
from __future__ import annotations

import asyncio
import uuid
from collections.abc import Awaitable, Callable, Mapping
from typing import Any

KINDS = {"observation", "question", "challenge", "response", "escalation", "resolution"}


class TeamError(Exception):
    """Untrusted or incomplete agent exchange."""


class PeerBus:
    def __init__(self, roles: set[str], head_sha: str, base_sha: str, *, max_messages: int = 500):
        if len(roles) < 2 or not roles or any(not role or not isinstance(role, str) for role in roles):
            raise ValueError("at least two named specialist roles are required")
        if not head_sha or not base_sha or max_messages < 1:
            raise ValueError("review target and message budget are required")
        self.roles = frozenset(roles)
        self.max_messages = max_messages
        self.head_sha = head_sha
        self.base_sha = base_sha
        self.queues: dict[str, asyncio.Queue[dict[str, Any]]] = {r: asyncio.Queue() for r in roles}
        self.ledger: list[dict[str, Any]] = []

    async def send(
        self, sender: str, recipient: str, kind: str, subject: str,
        evidence_refs: list[str], *, thread_id: str | None = None,
        response_to: str | None = None, target_head_sha: str | None = None,
    ) -> dict[str, Any]:
        if sender not in self.roles or recipient not in self.roles or sender == recipient:
            raise TeamError("unknown or invalid peer")
        if (kind not in KINDS or not isinstance(subject, str)
                or not subject.strip() or not isinstance(evidence_refs, list)):
            raise TeamError("invalid peer message")
        if target_head_sha is not None and target_head_sha != self.head_sha:
            raise TeamError("stale review target")
        if len(self.ledger) >= self.max_messages:
            raise TeamError("message budget exceeded")
        if any(not isinstance(ref, str) or not ref for ref in evidence_refs):
            raise TeamError("invalid evidence reference")
        message_id = uuid.uuid4().hex
        message = {
            "message_id": message_id, "thread_id": thread_id or message_id,
            "review_target": {"base_sha": self.base_sha, "head_sha": self.head_sha},
            "sender_role": sender, "recipient_role": recipient,
            "kind": kind, "subject": subject,
            "evidence_refs": list(evidence_refs), "response_to": response_to,
            "status": "delivered",
        }
        self.ledger.append(message)
        await self.queues[recipient].put(message)
        return message

    async def receive(self, recipient: str, *, timeout: float = 10.0) -> dict[str, Any]:
        if recipient not in self.roles:
            raise TeamError("unknown recipient")
        try:
            return await asyncio.wait_for(self.queues[recipient].get(), timeout=timeout)
        except asyncio.TimeoutError as exc:
            raise TeamError(f"no response for {recipient} before deadline") from exc

    async def run(
        self, handlers: Mapping[str, Callable[["PeerBus", str], Awaitable[Any]]],
        *, timeout: float = 30.0,
    ) -> dict[str, Any]:
        if set(handlers) != set(self.roles) or timeout <= 0:
            raise TeamError("every selected role needs an explicit handler and positive timeout")
        tasks = {role: asyncio.create_task(handler(self, role)) for role, handler in handlers.items()}
        try:
            results = await asyncio.wait_for(
                asyncio.gather(*tasks.values()), timeout=timeout,
            )
        except (Exception, asyncio.CancelledError) as exc:
            for task in tasks.values():
                task.cancel()
            await asyncio.gather(*tasks.values(), return_exceptions=True)
            raise TeamError(f"peer exchange did not complete: {type(exc).__name__}") from exc
        # Only the Code Review Lead owns review coverage and PASS/FAIL.
        return {
            "transport": "inprocess", "execution_mode": "team-relayed",
            "independent_agents_executed": False, "review_performed": False,
            "review_verdict": None, "participants": sorted(self.roles),
            "peer_threads": list(self.ledger),
            "results": dict(zip(tasks.keys(), results)),
        }
