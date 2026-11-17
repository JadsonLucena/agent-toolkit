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

## Pre-Implementation PR Strategy and Git Handoffs

* On a composite initiative with plausible independent or stacked PRs, route the Git Engineer's read-only `contexts/git/skills/manage-pull-request/SKILL.md` `plan` mode **before the first implementation mutation**, following `contexts/git/rules/pull-request.md`. Reuse a current plan when valid; do not impose ceremony on a single coherent PR.
* Give Implementation the PR Boundary, authorized slice, intended base, dependencies, checks and permission restrictions as **evidence inputs**. Git's plan does not authorize implementing every proposed PR or any remote publication.
* When code already exists without a prior PR plan, ask Git to assess the actual diff during `prepare`; never claim that planning happened before mutation.
* Implementation detects each completed atomic intention; Git executes `contexts/git/skills/create-semantic-commits/SKILL.md` and returns a verified commit SHA or blocker. Delivery must not schedule dependent work from a merely requested, failed, stale or unverified commit handoff.
* Planning, local commits, pushing, creating PRs and merging remain separate operations with separate authorization and evidence.

## Integration Readiness and PR Lifecycle

* After a bounded Implementation result, Integration verifies the actual intended head/base and applicable tests, lint, independent Code Review, PR readiness, remote PR state, and eventual merge eligibility as **distinct evidence claims**. Implementation completion, a PR created and a change integrated into the target branch are not interchangeable.
* The independent Review owner issues the **single Code Review verdict**. For a **ready** PR, use the Git-owned `contexts/git/rules/pull-request.md` pre-creation floor: current applicable tests/lint and complete `review_profile=advisory` `PASS` evidence on the intended head/base. An advisory PASS is not a signed `gate` attestation.
* After a failed or incomplete independent Review or verification, return the affected defect or decision to its actual owner (Implementation, Design or Requirements). Reverify the resulting code and revalidate the Review evidence for the changed scope and final revision before claiming readiness. Do not silently modify a requirement merely to satisfy Review.
* An **explicitly authorized Draft PR** may still be published with failed, missing, stale or incomplete evidence when the Git-owned pre-creation policy allows it. State those gaps truthfully; do not label the Draft ready or gate-approved. This exception is not a bypass for a ready PR.
* Git owns `manage-pull-request` `prepare` and authorized `create` operations; Delivery sequences them **after** code implementation and applicable readiness investigation, without copying their internal verification or template procedure. A prepared PR is not a created PR, and a created PR is not merged.
* After remote PR creation, recheck required post-publication CI/checks, repository branch protections, independent approvals where required, and evidence freshness for the actual PR head/base. A changed head or relevant base requires proportionate revalidation; upstream checks are reusable only if still equivalent for the integration target.
* A merge requires separately authorized Git integration, all applicable repository protections and readiness evidence, and verification of the observed target state. Route the operation to Git's established branch/integration capability; do not make Delivery a new merge engine. When checks are unavailable or failed, or approval is missing, report the blocking status instead of merging.
* The target stage `reviewed`, `pr-prepared`, `pr-created`, or `integrated` reports only that specific observed milestone. Stop on the requested stage instead of automatically publishing or merging. Post-PR review/checks do not create a second Code Review owner or automatic merge authorization.

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
