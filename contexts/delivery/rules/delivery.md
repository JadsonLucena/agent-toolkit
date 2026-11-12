# Delivery Rules

## Composition and Ownership

* Delivery coordinates an explicitly multi-context engineering workflow; it does not own Requirements specification, Design decisions, Implementation code, Testing standards, Review verdicts or Git repository operations.
* Select only the next material capability from evidence actually available. A complete specification need not exist for unrelated slices; preserve shared guarantees and stop only dependencies affected by a material unknown.
* Consume neutral cross-context contracts and explicit inputs. Do not invoke another context's internal Agent or Skill merely to extract data, or duplicate their procedures.
* Distinguish specification validated, design ready, slice implemented, tests observed, Review verdict, PR ready, deployed and outcome demonstrated. A later claim requires independent evidence, not inferred progression.

## Authorization and Gate Integrity

* A Delivery request carries an explicit `target_stage` and operation-specific authorization. Default to read-only assessment when execution scope is unspecified; do not infer code mutation, local commit, push, PR creation, merge, deploy or release from workflow naming.
* Route each authorized operation to its owning capability and honor its more specific boundary. A stage transition must not broaden permissions automatically, even when needed to finish the objective.
* Review is the **single technical review verdict**. Apply the existing review profile and Git PR readiness policies. Local verification, independent review and remote PR creation remain distinct actions with distinct evidence and authority.
* Freeze and revalidate applicable source baseline, changed-file state, tests, review target and approvals before consuming evidence. Invalidate only affected downstream claims when authoritative inputs change.

## Controlled Coordination and Recovery

* Preserve the current Change Boundary, target stage, authoritative source IDs, decisions, observed checks, side effects, blockers, completed stages and next owner when material. A host may persist these facts; no vendor-specific checkpoint format is canonical.
* A retry requires actionable new evidence or a changed, safe strategy and may not override a blocking decision, safety bound or cost/attempt budget. Stop and report when no material progress can be made.
* Checkpoints cannot undo commits, data writes or external effects. Resume only after reconciling actual repository and external state; do not replay a potentially non-idempotent mutation without confirming its effect.
* Prefer serial execution as the baseline. Parallelize only independent investigations or isolated slices with stable inputs, no uncontrolled shared writes, and an explicit reconciliation point. Runtime absence of safe concurrency does not reduce workflow completeness.

## Outcome Handoff

Use the optional `contracts/outcome-evidence.md` semantics to preserve actual post-delivery observations separately from technical completion. Delivery must not create an operations capability or assume business outcome authority.

* A successful technical review or PR-ready state is not proof that deployment occurred or the original business problem was resolved. Preserve the original objective, expected measurement and responsible observer when supplied.
* Post-delivery effectiveness and PDCA feedback require real operational observations and their authority; absent observations remain pending or unknown. Do not fabricate metrics or mandate a deployment/observability integration.
* Scope changes, requirements contradictions, unverified guarantees, material side effects and unresolved cross-context decisions route back to their actual owners, not to an unbounded coordinator loop.

## Foundational Guidance

Use the SDLC as a coverage model, SDD as a conformance discipline, PDCA as an outcome feedback loop, and dependency-aware flow as a scheduling strategy. None creates an extra canonical source of requirements or a mandatory full-document waterfall.
