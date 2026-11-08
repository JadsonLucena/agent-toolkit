# Optional Agent Team Messaging Transport

\`peer_bus.py\` provides a small **provider-neutral, in-process** message
transport for the Review Team protocol defined in
\`contexts/review/skills/coordinate-review-team/skill.md\`.

It delivers real, bounded messages between role handlers and records the
challenge/response evidence thread. Handlers are supplied by the hosting
platform. Example:

\`\`\`python
import asyncio
from peer_bus import PeerBus

async def correctness(bus, role):
    await bus.send(role, "reliability", "challenge",
                   "Can retries charge twice?", ["billing.py:32"])
    answer = await bus.receive(role)
    return answer["subject"]

async def reliability(bus, role):
    question = await bus.receive(role)
    await bus.send(role, "correctness", "response",
                   "Idempotency guard is absent", ["payments.py:18"],
                   thread_id=question["thread_id"],
                   response_to=question["message_id"])

bus = PeerBus({"correctness", "reliability"}, "head-sha", "base-sha")
result = asyncio.run(bus.run({
    "correctness": correctness, "reliability": reliability,
}))
\`\`\`

The transport enforces role membership, immutable head identity, allowed
message kinds, bounded messages and completion deadlines. It does not execute
an AI model, create isolated agent sessions, run code review, approve findings,
or publish PRs. It labels its execution \`team-relayed\`, **never \`team-live\`**,
because in-process coroutine handlers do not establish independently isolated
agents. A real Cursor/Claude/custom runtime must supply isolated agent
handlers and prove peer message delivery before claiming \`team-live\`.

The lead retains the full review scope and performs verification under the
neutral contract. Peer agreement is not a substitute for source evidence.
Without any parallel execution, the canonical native-solo path remains
available. See \`tests/test_team_transport.py\` for real exchanges with
deterministic fake agent handlers and failure-path tests.
