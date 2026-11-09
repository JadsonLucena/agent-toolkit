# Coordinate Review Team

## Purpose

Own the **Code Review Lead**'s risk-proportionate orchestration. Prefer
`team-live` only when isolated peers directly exchange messages **observed
by the runtime**. Otherwise prefer `team-relayed` whenever isolated
`Task`/subagents exist; use `native-solo` only if subagents are unavailable
or R0/R1 has no distinct investigation worth delegating. Never use consensus
or helper output to manufacture one `PASS`.

## Uses

* Rule: `contexts/review/rules/code-review.md`
* Skill: `contexts/review/skills/verify-findings/skill.md`
* Output contract: `contracts/review-evidence.md`
* Optional input contract: `contracts/requirements.md`
* Optional input contract: `contracts/test-basis.md`
* Optional input contract: `contracts/test-evidence.md`

## Working State

Before any spawn, freeze `review_id`, repository identity, resolved base/head
SHA (or a read-only workspace fingerprint), complete Git changed-file inventory,
`risk_profile` R0–R3, separable concerns, selected/omitted specialist roles,
and applicable acceptance/risk questions. Every specialist **including the
verifier** must receive the same identity and read-only boundary.

For a workspace review, hash HEAD, index, tracked changes and untracked file
content and recheck at the end. A moving target makes evidence `INCOMPLETE`.

## Team Activation

Use one isolated subagent per distinct concern, with the actual corresponding
`contexts/review/agents/{role}.md` as its role prompt. Lead is NOT a lens.

| Risk | First-pass specialist N | Finding verifier |
| --- | --- | --- |
| R0 | 0 (native lead) | not required |
| R1 | 0, or 1 with a distinct concern | only if that one identifies a blocker |
| R2 | 2–4, one per separable concern | if there is a material finding |
| R3 | 3–5 relevant roles | **always** an isolated verifier when subagents exist |

**Never** dispatch one all-purpose specialist at R2/R3 because peer messaging
is unavailable; **never** dispatch all seven by default. At most the six
investigation roles plus one `finding-verifier`. If R2/R3 has fewer distinct
concerns than the minimum, revisit scope/risk or report the planning gap
`INCOMPLETE`; do not manufacture concerns to fill quotas.

Concern mapping:

* contract / OpenAPI / AC → `specification-reviewer`
* correctness / behavior / regression → `correctness-reviewer`
* security / auth / PII / injection → `security-reviewer`
* reliability / locks / idempotency / data / partial failure → `reliability-reviewer`
* testing / scenario adequacy → `testing-reviewer`
* architecture / service boundaries / operations → `architecture-reviewer`

Record each omission and why it was not relevant. R3 with a runtime that has
no isolated verifier may use the lead's documented native falsification pass,
but must label it `native-second-pass` (never independent agent verification).
If the implementation author is the lead, switching roles does not establish
independence: all investigative specialists and the verifier must be isolated,
and the final `PASS` still requires a genuinely independent lead/session.

## Mode Selection — Strict Precedence

1. `team-live` only if the runtime isolates agents **and** an independent
   host audit observes direct **peer-to-peer** question/challenge **and**
   response delivery between the corresponding subagent IDs. A capability
   flag, shared memory, ordinary parallel Task calls, or in-process queues
   do not qualify.
2. `team-relayed` is the **default fallback when isolated subagents exist**
   but direct messages cannot be observed. Launch all selected sibling Tasks
   in the same turn; the lead acts as the actual message bus.
3. `native-solo` only when subagents cannot be used, or R0/R1 has no
   separable concern. Native solo still covers every applicable lens.

In Cursor Agent, sibling `Task` calls do **not** inherently communicate.
`resume` on an existing subagent ID is a lead → specialist delivery and
remains `team-relayed`. If resume is unsupported, the lead may create a
new isolated `Task` with the narrow question and original immutable target,
recording the new task ID and transfer; do not invent a prior conversation.
No platform-specific APIs are made canonical.

## Collaboration Protocol

All messages are bounded, read-only, evidence-linked and anchored to the
same snapshot:

* `review_id`, `target_head_sha` (or workspace fingerprint), `message_id`,
  `thread_id`, `sender_role`, `recipient_role`, `kind`, `subject`,
  `evidence_refs`, `requested_action`, `response_to`, `status`.
* Kinds: `observation`, `question`, `challenge`, `response`,
  `escalation`, `resolution`.
* Evidence must identify file:line or bounded source, expected versus observed
  behavior, and provenance; never forward whole transcripts, irrelevant
  context or secrets.

A material question/challenge/escalation opens a thread, the recipient replies
with inspected evidence and the original requester resolves it. Merely
responded threads are not resolved. Failed Task, missing replies, stale target
or material disagreement remain open and prevent a clean verdict.

## Workflow

1. **Freeze before Task:** repository, full inventory, resolved target/fingerprint,
   risk profile, separable concerns and allocation plan. Use
   `adapters/review/team_orchestration.py` or an equivalent approved host
   adapter; require the same target on every specialist response.
2. **Select mode and N:** apply the strict precedence and table above.
   `team-live` is only a candidate until direct peer delivery is observed;
   otherwise report `team-relayed`. No Task -> `native-solo`.
3. **First pass — one simultaneous Task batch:** dispatch one independent
   subagent per activated lens in the **same host turn**, using its canonical
   agent file and common frozen SHA. Return candidate findings, reviewed
   file paths and uncertainties; specialists do not issue PASS/FAIL.
4. **Second pass — relayed cross-lens exchange:** for each material dependency,
   the lead creates a structured message with a target and action and delivers
   it via `Task resume` to the recipient's ID (or a new narrow Task).
   Relay the evidence-backed response to the original requester and record
   its resolution. Example: correctness raises duplicate payment; relay a
   challenge to reliability about idempotency and testing about assertions.
   Preserve the actual transport, IDs and exact thread status. Never pretend
   agent-to-agent delivery occurred without it.
5. **Third pass — independent falsification:** R3 **always** requests an
   isolated `finding-verifier` even when initial findings are empty; R2
   requests one for material findings; R1 only for blocker candidates.
   Verification means independent **source inspection**, not vote counting.
   If no isolated verifier exists, perform a separate source-backed native
   falsification pass and honestly mark `native-second-pass`.
6. **Reconcile:** the lead checks every original Git changed file, including
   paths OCR or specialists excluded, and verifies any raw candidate's
   explicit disposition. Recheck the frozen snapshot. Missing file,
   unresolved challenge or unknown high-impact claim => `INCOMPLETE`.
7. **One verdict and report:** the lead alone issues `PASS`, `FAIL`,
   or `INCOMPLETE` using `contracts/review-evidence.md`.
   A team quorum, shared confidence or successful tool exit cannot grant
   PASS. Independence of the lead remains a separate prerequisite.

## Output

Report `execution_mode`, `risk_profile`, `team_members` (role, concern
reason, actual subagent ID), `coordination` (actual direct audit vs
`Task+resume`/narrow Task/no bus), `peer_threads` (bounded relayed
questions/challenges, not full chats), `independent_verification`
(isolated-agent vs native-second-pass), complete file inventory/coverage,
and `n_justification` (concerns, selected/omitted roles and N).

`adapters/review/team_orchestration.py` is a provider-neutral reference
implementation whose host-supplied `TaskRuntime` protocol requires an actual
isolated Task batch, resume and optional direct-message audit. It never
spawns an AI model itself; `run_review.py` freezes the plan for that host.
Configuration in Cursor/another agent runtime must implement the Task adapter
to perform the actual parallel sessions.

## Boundaries

* All roles are **read-only**; no edits, code generation, staging, commits,
  pushes, PR creation, reviews, approvals, merges or external distribution.
* No installation, OCR requirement, prohibited provider or extra permissions.
* No false `team-live`, fake Task IDs, fabricated dialogue, all-role
  fan-out, one all-purpose R2/R3 Task, or PASS by consensus.
* Never replace independence with a different role in the implementer's session.

## Stop Conditions

Report `INCOMPLETE` when the target changes, required files or Task
evidence are missing, R2/R3 allocation cannot satisfy distinct concerns,
material threads remain unresolved, an R3 verifier with available subagents
cannot be established, or independent review cannot be established.
An unavailable team runtime alone does not invalidate a **complete,
separately independent** native review.
