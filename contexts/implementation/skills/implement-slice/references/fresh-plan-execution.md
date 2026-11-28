# Fresh Plan Execution (optional, sequential)

Use only when a caller has selected more than one bounded implementation plan or
has explicitly requested a fresh agent context for a single plan. This is a
supporting reference for implement-slice, **not** an independent Skill, Agent,
Command, policy owner, or a requirement to use a particular model.

## Ownership and routing

- Delivery selects the next authorized plan and waits for its observed
  completion before selecting the next. Never create execution waves here.
- Implementation retains its native pre-edit intention separation, TDD preference,
  verification, and Git-owned atomic commit handoff. A plan is not a commit.
- A host may start **one new, non-resumed model session** per plan with scoped
  applicable sources, critical guarantees, current Git state, and explicit
  operation-level authority. A smaller prompt in the original session is not
  an isolated new session.
- The host must report a concrete session/thread identifier and observable
  spawn and exit events. Distinct session identities must be checked across
  plans; model assertions alone are not evidence of isolation.
- Select sources using the original accepted Change Boundary and source
  identifiers. Re-read and verify critical sources before launch. A reference
  is not itself a loaded or verified source. Do not copy complete conversations.
- At handoff, require observed successful mandatory plan-check commands, and verify the actual repository revision, file scope, tests,
  completed atomic commits, and known external effects. Do not trust a
  success-shaped message as passing verification or independent Review.
- If a host is unavailable, default to the existing native Implementation
  procedure with an explicit `no fresh session` limitation. With a caller
  requiring isolation, stop instead; do not silently simulate a session.
- On timeout, missing session proof, uncommitted state, unauthorized edits,
  stale evidence, or unknown external effects: **stop before the next plan**
  and return to the appropriate owner for reconciliation. Never automatically
  replay potentially non-idempotent steps.

## When to stop

Do not perform a second plan while a previous one has an unresolved commit,
failed check, material source change, unknown external effect, or unverified
scope. Fresh session creation never authorizes PR creation, push, merge,
deployment, access to secrets, or a new business decision. Host tool-level
enforcement is required for sensitive operations; Markdown cannot enforce it.
