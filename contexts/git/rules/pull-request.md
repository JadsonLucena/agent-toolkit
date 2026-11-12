# Pull Request Rules

## Core Principle

* A pull request (PR) must represent the smallest change that is coherent, verifiable, reviewable, and safe to integrate for one explicit primary objective.
* A PR boundary must be justified by a behavior, contract, risk-reduction step, or technical preparation that can be reviewed and verified. Line count, file count, layer count, or task boundaries are not sufficient by themselves.
* A feature, story, use-case slice, or Product Slice may require multiple PRs. A merged PR does not by itself mean that the task, Product Slice, use case, story, or release is complete.
* Keep the system safe after every merge. An incomplete larger feature may be integrated only when the merged state does not break existing behavior, contracts, data integrity, buildability, or required guarantees.
* When incomplete behavior must be merged, keep it inactive behind an appropriate safe mechanism such as a feature flag, disabled path, compatibility layer, or equivalent repository-approved strategy.

## Slice Terminology

These labels describe **scope and traceability**, not new canonical artifact types:

* **Product Slice** — a coherent increment of user/product behavior or validated learning toward a product outcome. It can require multiple independently integrable PRs.
* **Architectural Slice** — a bounded technical contribution (for example, a service, component, contract, or repository-local change) that enables or evolves a larger Product Slice. It has its own integration-safety and verification obligations but does not, by itself, prove product acceptance.

Neither term overrides a Requirements Change Boundary, a project's established slice vocabulary, or the rule that each PR must stand as one coherent, verifiable review unit.

## Pre-Implementation PR Strategy

* When a request or known roadmap contains multiple material outcomes, independently reviewable increments, or dependencies that make multiple PRs plausible, **assess the PR strategy before the first implementation mutation**. Use the read-only `plan` mode of `manage-pull-request` (or an equivalent scoped PR plan) before implementing a composite change. This assessment is conditional, not mandatory ceremony for every change.
* Compare a **single coherent PR**, **independent PRs**, and **stacked PRs** using actual dependencies, reviewability, integration safety, traceability, and the cost of intermediate states. Do not split merely by roadmap stage or count of tasks. Prefer independent bases when no actual dependency exists.
* For stacked PRs, record each intended base/head, prerequisite, review scope, and expected safe intermediate state. Do not make a later PR appear independent when it depends on unmerged work.
* An explicit request for **one increment** does not authorize implementing the entire roadmap. Record remaining stages and the proposed delivery strategy without silently broadening the current authorization; clarify only when ambiguity materially changes what may be implemented.
* If implementation already exists without prior planning, assess decomposition during `prepare`; report scope or split findings without claiming pre-implementation planning took place.
* The assessment itself is **read-only**. It does not authorize implementation, branch creation, commits, push, PR publication, merge, or release. For an evidently single coherent review unit, proceed without a separate formal plan; preserve rationale when material.

## PR Boundary

Before preparing or creating a PR, establish a PR Boundary containing, when relevant:

* the primary objective and expected observable result;
* source references such as requirement, rule, use case, scenario, work item, defect, or decision identifiers;
* the Product Slice, use-case slice, Architectural Slice, or other delivery slice to which the PR contributes, when such a slice exists;
* included changes;
* explicitly excluded or deferred changes;
* dependencies on previous or subsequent PRs;
* acceptance criteria, scenarios, invariants, or guarantees assigned to this PR;
* verification evidence expected for this PR;
* compatibility, migration, rollout, observability, rollback, security, privacy, data-integrity, idempotency, or financial-integrity concerns when applicable;
* the expected state of the larger task or slice after this PR is integrated.

The final diff must be reconciled against the PR Boundary. Material scope drift requires one of:

1. remove or split the unrelated change;
2. revise the PR plan when the broader boundary remains coherent and justified;
3. report the mismatch as unresolved.

Do not rewrite the PR description merely to disguise scope drift.

## Decomposition and Reviewability

* Prefer one primary objective per PR.
* Prefer vertical or use-case-oriented slicing when it produces a coherent, observable, and safely integrable change.
* Do not split solely by technical layer, directory, class, or arbitrary line-count threshold when that creates incoherent or unverifiable PRs.
* A technical or preparatory PR is acceptable when it has an independently reviewable purpose, preserves integration safety, and remains traceable to the larger change.
* Separate substantial refactoring from behavior changes when separation materially improves reviewability, rollback, or understanding without making either PR unsafe or incoherent.
* Keep directly related tests with the behavior they verify unless a separate prerequisite test/characterization PR is itself the coherent unit of work.
* A dependent or stacked PR must make its dependency and intended base explicit.
* When one Product Slice spans multiple repositories or independently deployable components, plan repository-local PR boundaries around coherent Architectural Slices or equivalent local changes and retain end-to-end traceability across them.
* Do not defer critical guarantees merely to make a PR smaller. Authorization, privacy, data integrity, duplicate prevention, idempotency, compliance, and minimum required observability must accompany the behavior that depends on them, or the behavior must remain inactive.

## Size and Complexity

PR size is a reviewability heuristic, not a correctness rule.

Use review-relevant changed lines as an initial signal:

* up to approximately 300 review-relevant changed lines: generally a favorable starting range when the PR is coherent;
* above approximately 400 review-relevant changed lines: explicitly reevaluate whether a cleaner decomposition exists;
* above approximately 1,000 review-relevant changed lines: require an explicit reason for retaining the PR as one review unit.

Do not approve or reject a PR from line count alone.

When evaluating complexity, consider at least:

* number of distinct behaviors, rules, scenarios, and invariants changed;
* dispersion across modules, services, bounded contexts, or repositories;
* public APIs, events, schemas, contracts, or compatibility changes;
* data migrations, backfills, or version coexistence;
* control-flow complexity and side effects;
* concurrency, retries, ordering, idempotency, duplicate execution, and recovery;
* security, privacy, compliance, and financial-integrity consequences;
* rollout, feature flags, monitoring, rollback, and operational coordination;
* amount of generated, mechanical, or low-semantic-noise change versus manually reasoned behavior.

Generated or mechanical changes may justify a larger diff, but they do not remove the need to verify their correctness, safety, and provenance.

## Readiness and Verification

Before a PR is presented as ready for review:

* inspect the final diff and remove unrelated or accidental changes;
* verify that the diff still satisfies the PR Boundary;
* verify relevant acceptance criteria, scenarios, rules, invariants, contracts, or stated outcomes;
* execute applicable project checks when available and authorized;
* report only verification results actually observed from reliable evidence;
* report checks that were not run, failed, or were blocked;
* evaluate compatibility, data integrity, operational risk, rollout, rollback, and security concerns when applicable;
* preserve repository conventions for branch, commit, title, review, signing, and required checks;
* verify that no credential, token, secret, or unnecessary personal data is exposed by the change or PR description.

A PR can be technically prepared while not ready for final review. Use a draft/review-in-progress state when the hosting platform and repository workflow support it and required work or evidence remains.

Ready for review does not mean ready for production.

## Pre-Creation Quality Gate

* **Before creating a ready-for-review pull request**, apply the shared check-discovery, hook/CI-evidence and missing-check execution policy from `contexts/git/rules/git.md`. Require passing project tests and lint where applicable (coverage-enabled tests only when established), plus a proportionate native review under `contracts/review-evidence.md` whose `review_profile=advisory` was frozen before the read, with complete coverage and `review_status=PASS` for the exact head/base. The description states `advisory` and states that gate attestation is absent or `not-applicable`. These are distinct checks; review cannot substitute for test/lint execution, and green test/lint results cannot substitute for review. A signed `review_profile=gate` attestation is not required for ready. It is required only to claim that the gate is satisfied.
* **Before creating a draft** that the user explicitly authorized, run the same discovery. A draft is the result when the floor or the applicable native review is missing, stale, failed, or `INCOMPLETE` with a material question. The description names that gap and does not record `review_profile=gate`. Opening the draft does not make the PR ready.
* Required evidence for a ready PR must correspond to the final intended head/base and review scope. A hook or CI configuration alone, a partial pre-commit result, or a workflow that will run only after PR publication cannot satisfy the pre-creation gate. Reuse only successful, completed evidence of equivalent or stronger scope; run missing checks explicitly. Any code change that invalidates review or check evidence requires fresh verification before ready creation.
* If an applicable test or lint check cannot run, fails, is skipped without an authorized applicable policy, or has stale/uncorroborated results, block ready PR creation. A draft may still be published when publication was explicitly authorized and the description states that the check did not run, failed, or is stale. If a check is genuinely not applicable, state a specific reason instead of inventing a pass. Proportionate native `review_profile=advisory` review is required before a ready PR, even for R0/documentation-only changes. Signed gate review is not this requirement.
* If review evidence is absent, request or perform the **separate read-only Review capability** through an explicitly authorized multi-context orchestration, and consume its neutral contract. Git must not duplicate Review internals or require OCR or any vendor adapter. Record the result at the profile that was frozen. Do not promote `advisory` to `gate`. When no external enforcement path is configured, gate evidence is `not-applicable`, and that absence does not block ready once the floor and the advisory review have passed.
* A `draft` preparation state may still be produced before these checks complete; preparing a description is not remote creation. Publishing a draft does not make the PR ready, and the description must not present a draft or an advisory ready PR as gate-reviewed. Claiming `review_profile=gate` without external attestation is forbidden.
* A reviewer-only Markdown instruction is not an enforcement mechanism. A configured runtime, preflight wrapper, or CI/branch protection enforces what that deployment configured; never claim enforcement from the presence of this rule alone. When a protected runtime is configured, a creation that claims gate uses that runtime's signed path and a nonzero exit is the block. An explicitly authorized draft without gate attestation uses the runtime's unsigned draft mode when that runtime provides one. That mode does not verify `review_profile=gate` and refuses a body that affirms gate `PASS`. A ready PR that has only advisory evidence uses the host pull-request command, and the description states that gate was not attested. When no runtime is configured, this rule does not stop that host command.

## Template Precedence

Before writing a PR description, inspect applicable repository and organization instructions, including when present:

* contribution or agent instructions such as `CONTRIBUTING.md` and `AGENTS.md`;
* `.github/PULL_REQUEST_TEMPLATE.md`;
* `docs/PULL_REQUEST_TEMPLATE.md`;
* `PULL_REQUEST_TEMPLATE.md` at the repository root;
* repository-supported template directories such as `PULL_REQUEST_TEMPLATE/`;
* organization-level templates when accessible and applicable.

If an applicable project template exists:

* use it as the primary structure;
* preserve its required headings, fields, checklists, and conventions;
* do not replace it with a generic template;
* add information only when compatible with local instructions.

If multiple templates exist, select one only from explicit repository rules or a clear change-type mapping. If applicability is materially ambiguous, surface the ambiguity instead of choosing arbitrarily.

Use the fallback description structure below only when no applicable template exists.

## Description Integrity

A PR description must reflect the final diff and the evidence available at preparation time, not merely the original task description.

When relevant, it must make clear:

* **Why** the change is necessary.
* **What** the final diff actually changes.
* **Validation** performed and the observed results.
* **Impact** including risks, compatibility, migration, rollout, rollback, security, data, or operational concerns.
* **Traceability** to relevant slice, requirement, rule, scenario, work item, defect, or related PR.
* **Remaining work** and whether the larger slice or story is still incomplete.

Do not:

* claim that tests or checks passed without evidence;
* describe planned behavior as implemented behavior;
* invent issue identifiers, metrics, benchmarks, approvals, decisions, reviewers, or dependencies;
* mark an acceptance criterion or scenario as covered when evidence does not support that conclusion;
* repeat trivial line-by-line diff details instead of explaining intent and consequences.

The title must follow repository conventions. When no convention exists, use a concise title that identifies the principal change.

## Fallback Description

When no applicable repository template exists, use only the sections that are relevant:

```markdown
## Context and objective

<!-- Why is this change needed? -->

## Slice and traceability

<!-- Existing identifiers only; do not invent references. -->
- Product / use-case / architectural slice:
- Requirement / rule / scenario / work item:
- Contribution of this PR:

## Changes

<!-- Describe only what the final diff implements. -->
-

## Scope

**Included**
-

**Out of scope / follow-up**
-

**State after this PR**
-

## Validation

- Acceptance criteria / scenarios covered:
- Tests / lint checks executed and observed result:
- Independent code review: verdict, head/base, coverage, findings or remaining blockers:
- Not executed / limitations:

## Impact and risks

- Compatibility / data / security / operations / rollout / rollback:

## References

- Existing task / issue / related PR / documentation:
```

## Status Semantics

Keep these states distinct:

* **PR prepared** — scope, description, and evidence have been inspected, but no remote PR necessarily exists.
* **PR created** — a remote review request exists.
* **PR ready for review** — repository-required review prerequisites are satisfied or the remaining conditions are explicitly acceptable under local policy.
* **PR merged** — the review request has been integrated.
* **Task done**, **Product Slice done**, **Story done**, **released**, and **deployed** are separate states and require their own evidence.

Do not infer one state from another.

## Remote Creation Safety

* Before ready PR creation, revalidate the floor (applicable tests/lint) and the `review_profile=advisory` review for the final intended revision. Revalidate a signed `review_profile=gate` attestation only when the creation claims gate. A draft records missing evidence instead of claiming that revalidation passed.
* Creating a PR requires explicit authorization to create the remote review object.
* Preparing or drafting a PR does not authorize remote PR creation.
* PR creation does not authorize pushing unpublished commits, rewriting history, assigning reviewers, adding labels, enabling auto-merge, merging, closing, deleting branches, releasing, or deploying unless separately authorized.
* Before creation, verify the intended head and base, repository workflow, remote publication state, and whether an equivalent open PR already exists.
* Do not create a duplicate PR for the same effective head/base change when an existing review request should be reused or updated.
* If the required head branch is not available to the remote hosting platform, report the publication blocker unless push authorization is separately available.
* Do not silently change the base branch merely to make PR creation succeed.

## Foundational Guidance

These rules synthesize the project's PR policy with established guidance on code inspection, small batches, incremental delivery, use-case slicing, and modern code review. Repository-specific policy remains authoritative over generic heuristics when it preserves safety and integrity.

Foundational references used to shape this rule include:

* Michael Fagan (1976), *Design and Code Inspections to Reduce Errors in Program Development*.
* Jason Cohen, Eric Brown, and Steven Teleki (2006), *Best Kept Secrets of Peer Code Review*.
* Donald Reinertsen (2009), *The Principles of Product Development Flow*.
* Jez Humble and David Farley (2010), *Continuous Delivery*.
* Ivar Jacobson, Ian Spence, and Kurt Bittner, *Use-Case 2.0*.
* Alberto Bacchelli and Christian Bird (2013), *Expectations, Outcomes, and Challenges of Modern Code Review*.
* Google Engineering Practices, *Small CLs* and *Writing Good CL Descriptions*.

These references inform reviewability and flow principles; the numeric size ranges in this rule remain heuristics for local calibration, not universal laws.
