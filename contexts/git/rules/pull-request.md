---
description: "Apply when planning, preparing, creating, reviewing readiness for, or integrating a pull request; preserve scope and authorization gates."
alwaysApply: false
---

# Pull Request Rules

## Remote authorization invariant

**An explicit request to create a remote PR authorizes only its necessary first-time, non-force source-branch publication**, when the branch is not yet on the selected hosting remote and the repository, source/destination refs and exact reviewed head/base are unambiguous. Publication is a separately verified **effect within the authorized PR-creation workflow**, not blanket permission to push, update existing remote branches, create forks or change remotes. Explicit refusal of push, host permissions or repository policy take precedence and block publication. A mere proposed `target_stage`, PR planning/preparation or implementation authorization does not grant this permission. Merge, release and deployment still require distinct authorization. Markdown does not enforce remote permissions; the host must protect the actual tools.

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

A PR can be locally prepared while not ready for remote publication. Use a local `draft`/review-in-progress preparation state when required checks or Review evidence remain incomplete; that state does not authorize creating a remote Draft.

Ready for review does not mean ready for production.

## Pre-Creation Quality Gate

This is a **toolkit-specific pre-publication policy**, stricter than GitHub's default Draft PR workflow. GitHub may allow Draft creation before checks pass; required status checks usually gate [merging](https://docs.github.com/en/pull-requests/reference/status-checks), not creation. Do not present this rule as a GitHub-native constraint.

* **Before creating any remote pull request, including a Draft**, inspect the final head/base and complete diff, apply the shared check-discovery and evidence policy from `contexts/git/rules/git.md`, and require passing applicable project tests and lint (plus established coverage/other mandated checks). Require an actual Code Review under `contracts/review-evidence.md` with a pre-frozen `review_profile=advisory` or valid stronger `gate` profile, complete coverage, and `review_status=PASS` for the exact intended head/base. Checks and review are separate evidence: neither substitutes for the other. This floor applies to R0/documentation-only changes as well.
* **Missing, failed, incomplete, stale or uncorroborated evidence blocks remote creation in either state.** Do not publish a Draft to bypass tests, lint, review, or uncertain coverage. The same explicit PR-creation request authorizes requesting a separate, read-only Review evaluation with `review_profile=advisory` if a fresh matching review is missing; no second authorization is required. Git consumes `contracts/review-evidence.md`, never performs Review internals, and must not require OCR or a vendor adapter. On `FAIL` or `INCOMPLETE`, return findings or blockers to their owners; after a correction, revalidate the changed code and obtain fresh review for its final revision.
* **Local preparation is allowed without this floor.** The `prepare` mode may report `draft` or `blocked` when review/checks have not passed; it does not authorize remote publication. After the floor passes, an explicitly authorized remote Draft remains permissible for other unfinished activities, planned follow-up or reviewer discussion; describe those limitations without pretending the change is production-ready. A Draft is not a substitute for pre-publication quality evidence.
* Check results and review must correspond to the **final intended PR head/base and full scope**. A configured hook, unobserved invocation, stale commit check, partial pre-commit verification, or CI triggered only by opening the PR cannot satisfy pre-creation evidence. Reuse only successfully completed evidence of equivalent or stronger scope. Recheck before remote publication if any file, dependency, configuration, or revision affecting the decision changed.
* An `advisory` `PASS` can satisfy this publication floor; it is **not** an independently attested `gate`. A signed `review_profile=gate` attestation is not required for ready under the canonical advisory policy; it is required only to claim external gate enforcement. The PR description must truthfully identify the actual profile, evidence, and whether gate attestation is absent or `not-applicable`. Never promote advisory evidence into a signed gate claim.
* Markdown instructions alone do not enforce remote permission. A protected host, adapter or repository policy must guard the actual creation operation to prevent an agent bypass. The optional `adapters/github/guarded_pr.py` is deliberately stricter: it requires an SSH-signed independent gate review and trusted checks for **both ready and Draft** creation. An ordinary host PR API can use validated advisory evidence under this canonical rule only if the host enforces the same pre-creation floor; other GitHub clients remain outside this adapter's control.

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
- Code Review: profile, verdict, head/base, coverage, findings or remaining blockers:
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

* Before **any** remote PR creation (ready or Draft), revalidate applicable tests/lint and a complete Code Review `PASS` for the exact final head/base and full diff. Revalidate signed `review_profile=gate` evidence only when claiming an externally enforced gate or using a runtime that requires it. Missing, failed, incomplete or stale evidence blocks publication; local Draft preparation remains available.
* Creating a PR requires explicit authorization to create the remote review object.
* Preparing or drafting a PR does not authorize remote PR creation.
* PR-creation authority permits only the scoped initial source-branch publication described above, not force-push, updating an existing remote branch, rewriting history, changing protected/default branches, selecting another remote/fork, assigning reviewers, adding labels, enabling auto-merge, merging, closing, or deleting branches, releasing, or deploying without separately applicable authority.
* Before creation, verify the intended head and base, repository workflow, remote publication state, and whether an equivalent open PR already exists.
* Do not create a duplicate PR for the same effective head/base change when an existing review request should be reused or updated.
* If the required head is unpublished, inspect the exact remote branch and apply the scoped first-publication conditions in the Remote Authorization Invariant. Perform necessary non-force publication only when those conditions hold, then verify the remote SHA before creating the PR. An ambiguous or unexpected remote ref, explicit no-push restriction or insufficient host permission blocks the step. If the remote branch already exists at a different SHA, never update it under implicit first-publication authority.
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
