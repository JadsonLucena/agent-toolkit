---
description: "Apply when implementing an authorized bounded code change, including safety checks, optional test-driven work, and Git handoffs."
alwaysApply: false
---

# Implementation Rules

## Authority and Slice Integrity

* Implement only the bounded change the invoked command authorizes. Source of truth is the applicable accepted specification, Change Boundary, approved design and actual repository state; do not invent product policy to keep moving.
* A selected slice must have coherent intent, supported acceptance or verification evidence, material guarantees and a safe intermediate state. Work on the smallest independently verifiable increment without fragmenting an invariant.
* Inspect repository conventions, existing behavior, relevant tests and actual working-tree changes before mutation. Preserve unrelated work; never reset, discard or overwrite it without explicit authorization.
* If requirement, interface, acceptance or security semantics are materially ambiguous, stop the affected work and return the decision to its owner. An implementation preference never silently authorizes a requirements change.

## Safe Implementation

* Prefer established patterns, minimal necessary code and compatibility-preserving changes. Explicitly assess data migration, authorization, state transitions, idempotency, time, concurrency, timeouts, retries, financial integrity, and external side effects when material.
* Maintain buildability and required guarantees at each integrable boundary; when incomplete behavior is safely parked, keep it inactive until activation is authorized. Feature flags are an option, not a universal requirement.
* Evaluate rollback, forward-fix, compensation or reconciliation for material irreversible or durable effects. Git revert does not reverse external outcomes or schema/data changes automatically.
* Do not run unapproved external services, deployments, destructive migrations, secret-dependent checks, network actions or data exposure. Use explicit host/runtime policy at the effect boundary.

## Test-Driven Execution

* Test-driven development is a conditional, authorized implementation strategy, not a prerequisite for all tasks. Select it where an executable small-behavior test can provide valuable feedback.
* The selected behavior must come from a supported requirement, scenario, observable contract, or existing characterization target; never invent acceptance semantics to make a convenient test.
* RED: write the smallest relevant failing test and execute it. Confirm failure is for the **expected behavioral reason**, not a setup error, unrelated regression or missing dependency. A test that already passes is not RED evidence.
* GREEN: change only the in-scope production code necessary to satisfy the selected behavior, while retaining existing material guarantees. Run the focused test and applicable regression checks.
* REFACTOR: improve structure without changing expected behavior; rerun relevant tests. A refactor with unverified preservation is not a completed TDD cycle.
* Repeat for another small behavior only after the current cycle's evidence is established. Persist the failure/output, actual commands, revision and supported scenario mapping when material.
* Repeated failures without a new actionable diagnosis, uncertainty in the expected behavior, a scope change or unsafe side effects stop the affected cycle and require the responsible decision owner. Automated test generation remains independently available in Testing.
* TDD cycle completion is not integrated verification, independent Code Review, deployment or business acceptance.

## Verification and Feedback

* Use supported tests and `contracts/test-basis.md`/`contracts/test-evidence.md` when supplied; scenarios remain semantic, not necessarily identical to test identifiers. Respect canonical `contexts/testing/rules/testing.md` as a quality reference without taking ownership of Testing's separate workflow.
* Execute applicable project verification after each completed intention: fast targeted checks first, then required integrated checks. Record exact commands, result, tested revision and why applicable checks were not run.
* A failing check is evidence to diagnose, not permission to rewrite expected business behavior. Repetition requires new evidence or a changed hypothesis. Stop when an attempt is unproductive, unsafe or out of authorized scope.
* A passing local check does not imply independent Code Review, deployment, acceptance, or measured outcomes. Review remains read-only and independently owned.

## Git Handoff Integrity

* Git owns commit atomicity, timing, staging and verification through `contexts/git/rules/semantic-commit.md`, `contexts/git/rules/git.md` and `contexts/git/skills/create-semantic-commits/SKILL.md`. Implementation owns the completed code intention and the handoff, not Git's internal procedure.
* Before the first code mutation of a plausibly multi-PR change, consume an existing valid PR strategy or request the Git Engineer's **read-only** PR-plan capability. A direct Implementation invocation must not silently bypass this condition merely because Delivery was not invoked. Use the Git-owned `contexts/git/rules/pull-request.md` policy; the resulting PR plan is evidence, not authorization to implement additional slices.
* For each verified atomic intention, provide the Git capability with the exact authorized change scope, actual repository/workspace identity, relevant verification results and local-commit permission. A completed code change is not a verified commit.
* Do not advance automatically to another atomic intention when an authorized Git commit is blocked, failed, unverified, or lacks a confirmed matching commit identity. When commits are prohibited, preserve the uncommitted state and stop before the next intention unless the caller separately authorizes a safe uncommitted continuation.
* A PR strategy, a successful commit and an implemented slice are distinct results. Planning, preparing and creating PRs remain Git-owned operations with separate authorization; local commits do not imply push, remote PR publication or merge.

## Atomic Delivery and Recovery

* Close completed, verified atomic intentions using the Git context's existing commit capability and policy when the invocation authorizes local commits; do not duplicate staging, message derivation or hook procedures here.
* Commit locally only in-scope changes after required checks. Implementation authorization never implies push, PR creation, merge, release or deployment.
* When resumed after interruption, validate the authoritative specification, repository snapshot, existing commits, test evidence and already-performed effects. A checkpoint is not a transaction or an automatic rollback.
* Parallel code work requires isolated write scopes or worktrees with stable interfaces and post-integration verification; do not parallelize mutually dependent RED/GREEN/REFACTOR steps.

## Completion

* Report changed files, requirement/scenario and design references when known, observed checks, unresolved blockers, side-effect/recovery risks, and the current revision/scope. A completed slice is not a completed product outcome.
* Leave work with explicit status `implemented`, `blocked`, or `incomplete`, with limitations and next owner; never claim acceptance or independent review solely from self-verification.

* Completing Implementation means the bounded slice and its local verification and Git handoff state are reported. It does not imply independent Review, PR readiness, PR publication, merge, or integration into the target branch. Forward the exact implementation revision, tests and known limits for a separate integration-stage decision.

## Foundational Guidance

Use change-by-change feedback from test-first development, continuous integration and evolutionary design, with risk-based verification and atomic changes. These approaches inform procedures; they are not a universal TDD requirement or a license to bypass project conventions.
