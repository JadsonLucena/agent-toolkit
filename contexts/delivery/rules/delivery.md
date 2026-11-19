---
description: "Apply when coordinating an explicitly authorized, multi-context engineering delivery or handoff; preserve stage gates and specialist ownership."
alwaysApply: false
---

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

## Slice-Scoped Context Integrity

* Select context for the **next authorized slice and decision**, not every available document or an arbitrary fixed token quota. Start with source identity, the accepted Change Boundary, objective, relevant scenario/acceptance and critical-guarantee references, actual repository/decision versions, and current evidence or blockers when these are material.
* Reuse the neutral identities and evidence references in `contracts/work-item.md`, `contracts/requirements.md`, `contracts/design-evidence.md`, `contracts/test-basis.md`, and downstream evidence rather than inventing a mandatory slice-context schema or copying full source documents into every handoff.
* Prefer references to authoritative sources and **progressive, authorized retrieval** of affected code, dependencies, decisions, variants and test results when the next step requires detail. A reference alone is not evidence that the content was retrieved or verified.
* Context reduction must never remove relevant domain, security, privacy, financial, authorization, compatibility, data-integrity or operability guarantees required for the slice. If a critical source is missing, inaccessible, contradictory or stale, expose that limitation and stop or escalate the affected decision instead of guessing.
* At every material handoff or resumption, compare source baselines, shared contracts, repository revisions and decision authority. Invalidate only affected derived evidence when upstream meaning changes; do not substitute an old summary for a newly authorized source.
* Context selection and retrieval do not authorize broader investigation, source mutation, secret access or external data transfer; platform/tool permissions remain authoritative.

## Product Slice Continuity and Completion Evidence

* A Product Slice or use-case slice remains the supported behavioral or learning objective across its work items, Architectural Slices, implementation intentions, commits, and one or more PR Boundaries. These units have different completion and authorization semantics; one-to-one identity or size is not required.
* Where multiple PRs contribute to one Product Slice, preserve the original objective and the applicable scenario, acceptance, rule, quality, and critical-guarantee references. Determine which PRs are required for the currently authorized slice, which are integrated, still pending, intentionally deferred, or superseded; a PR merged alone never proves the overall slice is complete.
* For a material technical slice-completeness claim, reconcile the **integrated target revision(s)**, coverage of every committed obligation, and relevant cross-PR or cross-component interaction verification. Independent PR-level tests and Review verdicts do not prove the combined behavior. Report omitted scenarios, conflicting interfaces, inaccessible repositories, or missing integrated verification as incomplete or unverified—not as satisfied.
* Technical verification of the whole slice is distinct from stakeholder acceptance, activation, release, deployment, and observed business value. A learning slice may be complete through a supported experiment and recorded decision even without a new deployed feature; do not invent behavioral acceptance for learning work.
* An authorized merge need not be blocked merely because the larger Product Slice is unfinished, provided the PR independently satisfies integration safety and repository gates. Report **PR integrated / Product Slice still incomplete or unverified** and keep remaining obligations visible. Do not silently change the approved Change Boundary or drop guarantees to manufacture completion.

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

## Feedback and Learning Integrity

* Feedback may arise during any SDLC stage or from later operational observation. Assess it only when it can inform a material decision; do not impose mandatory post-task retrospectives, a second Review verdict, or a new delivery-completion stage.
* Keep observations, expected behavior, source and revision identities, provenance, relevant safeguards, hypotheses, decisions and post-change validation distinct. An agent's self-report, a passing check and an outcome metric have different evidentiary meanings.
* Separate **operational feedback** about agents, tools, instructions and workflow from **outcome feedback** about product/organizational effects. Preserve `contracts/outcome-evidence.md` as the optional source-linked outcome handoff; no duplicate contract or provider-dependent memory store is required.
* Do not treat a recurring symptom as a proven root cause or a before/after correlation as causal proof. Assess representativeness, confounders, stale baselines, duplicate incidents and counterevidence at rigor proportionate to risk.
* Single-loop correction (execution under current rules) and double-loop inquiry (reconsidering governing assumptions, objectives or responsibility boundaries) are competing lines of investigation, not automatic reasons to rewrite canonical policy.
* A feedback hypothesis or proposed lesson has no normative authority. Route requirement meaning to Requirements/stakeholders, design to Design, code to Implementation, tests to Testing, review findings to Review, Git actions to Git, and business outcomes to the accountable observer/decision owner. Changing source, instructions, policy, tooling, remote state or external effects requires the separately applicable authorization and verification.
* Label an observed issue, an inferred cause, an authorized decision, an executed corrective action and an **independently observed effect** separately. A change without follow-up evidence is a hypothesis under test, not a proven improvement; missing or inconclusive evidence must remain explicitly unresolved.
* Reuse evidence IDs and source references; keep feedback records concise, avoid unnecessary retention of private transcripts and secrets, and do not promote unverified memories or agent self-reflections over authoritative sources.

## Foundational Guidance

Use the SDLC as a coverage model, SDD as a conformance discipline, PDCA as an outcome feedback loop, and dependency-aware flow as a scheduling strategy. None creates an extra canonical source of requirements or a mandatory full-document waterfall.
