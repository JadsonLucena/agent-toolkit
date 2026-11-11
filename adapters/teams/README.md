# Optional Agent Team Messaging Transport

\`adapters/teams/peer_bus.py\` supplies a bounded, provider-neutral,
**in-process** transport for host-provided Review specialist handlers. It
implements the collaboration envelope of
\`contexts/review/skills/coordinate-review-team/SKILL.md\`:

* \`review_id\`, immutable \`target_head_sha\` / \`target_base_sha\`,
  \`message_id\`, \`thread_id\`, \`sender_role\` / \`recipient_role\`;
* \`kind\`, \`subject\`, \`evidence_refs\`, \`requested_action\`,
  \`response_to\` and message delivery status;
* **open → responded → resolved** thread lifecycle for questions, challenges
  and escalations.

Each question/challenge/escalation starts a new thread with an actionable
request; the intended peer responds with evidence and the original requester
**explicitly resolves** the response. Unknown IDs, mismatched participants,
stale identities, inappropriate resolutions or unresolved threads are
rejected. Completion cannot be reported while material questions remain open
or merely answered but unacknowledged.

Example:

\`\`\`python
import asyncio
from peer_bus import PeerBus

async def correctness(bus, role):
    await bus.send(role, "reliability", "challenge",
                   "Can retries charge twice?", ["billing.py:32"],
                   requested_action="Inspect idempotency")
    answer = await bus.receive(role)
    await bus.send(role, "reliability", "resolution",
                   "Verified against the evidence", ["payments.py:18"],
                   response_to=answer["message_id"])
    return answer["subject"]

async def reliability(bus, role):
    question = await bus.receive(role)
    await bus.send(role, "correctness", "response",
                   "Idempotency guard is absent", ["payments.py:18"],
                   response_to=question["message_id"])
    await bus.receive(role)

bus = PeerBus({"correctness", "reliability"}, "head-sha", "base-sha",
              review_id="review-123")
result = asyncio.run(bus.run({
    "correctness": correctness, "reliability": reliability,
}))
\`\`\`

Only the Code Review Lead can consolidate verified findings into a review
verdict. Handler coroutines **are not isolated model agents**. This bridge
truthfully reports \`team-relayed\`, \`review_performed=false\` and
\`review_verdict=null\`; a separate real Agent Teams runtime is needed for
\`team-live\` (independent sessions, actual peer-to-peer delivery, evidence
collection and authorization controls).

\`tests/test_team_transport.py\` covers genuine in-process exchanges and
failure paths. It does **not** assert a live provider/model integration.


## Risk-sized Task orchestration versus the message bus

The in-process `peer_bus.py` is a deterministic **transport test double**,
not isolated subagents. For production-grade collaboration, the reference
orchestrator lives in [`adapters/review/team_orchestration.py`](../review/team_orchestration.py).
It accepts host-created **isolated** `Task` identities and launches all
first-pass roles as one `task_batch`, enforcing R2=2–4 and R3=3–5 relevant
lenses, followed by an isolated `finding-verifier` for R3.

If a provider such as Cursor exposes Task/resume but no direct peer messages,
use `team-relayed` and record each lead-forwarded challenge and response.
Only a provider's direct-delivery audit may establish `team-live`.
An Agent Team's votes never create a review `PASS` without an independent
lead's complete file coverage and source verification.
