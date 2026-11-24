---
name: deliver-change
description: "Deliver a software change end-to-end, from requirements and backlog through design, implementation, tests, code review, and pull requests. Use for a requested delivery target; each mutation requires appropriate authorization."
---

# Deliver Change

## Intent

Coordinate a change from Requirements and backlog through Design, Implementation, Testing, Review, and PR creation, or stop at the requested delivery stage.

## Invocation

Select the Delivery Coordinator and its cross-context workflow. An explicit end-to-end objective such as "from requirements through PR creation" selects `target_stage=pr-created`; a requested stopping point selects its matching stage. If the target or authorized mutation scope is absent, assess readiness read-only. An explicit feedback request without a delivery target routes only the read-only `assess-feedback` capability. A target stage alone does not authorize code mutation. Once implementation mutation is authorized, verified in-scope atomic intentions may be locally committed under Git rules unless expressly prohibited; no separate commit phrase is needed. PR creation, push, merge, release, and deployment require separate authorization; implementation never implies push. Every routed specialist retains its own checks and authority gates.

## Uses

* Agent: `contexts/delivery/agents/delivery-coordinator.md`
* Skill: `contexts/delivery/skills/coordinate-delivery/SKILL.md`
* Rule: `contexts/delivery/rules/delivery.md`
* Optional input contract: `contracts/requirements.md`
* Optional input contract: `contracts/work-item.md`
* Optional input contract: `contracts/design-evidence.md`
* Optional input contract: `contracts/test-basis.md`
* Optional input contract: `contracts/test-evidence.md`
* Optional input contract: `contracts/review-evidence.md`
* Optional output contract: `contracts/outcome-evidence.md`

## Inputs

* Change objective, approved scope and current artifacts or source references.
* Optional operational feedback or observed outcome references, with expected/actual behavior and source/revision identity when known; feedback assessment alone is read-only.
* Explicit `target_stage`: `planned`, `designed`, `implemented`, `reviewed`, `pr-prepared`, `pr-created`, or `integrated`, plus applicable operation-level permissions. `pr-created` requires explicit PR-creation authority; `integrated` additionally requires merge authority and all repository prerequisites.
* Existing repository snapshot, stage evidence, accepted source and scenario references with revision identity, Git-owned PR plan/Boundary when available, local-commit restrictions and blockers when known. Missing source material is retrieved only when relevant and authorized.
* Runtime capabilities, intended PR base/head and PR publication state, review/check/approval evidence, repository branch protections, and resource/approval limits when known.

## Output

Actual completed stage and source/revision identity, next safe required capability, routed specialist results, PR-plan evidence where material, verified commit identities or explicit uncommitted/blocked state, current verification and independent Review evidence, prepared/published PR identity when observed, post-PR checks and approvals, verified merge target only when integration actually occurred, blockers, pending decisions, and evidence of operations actually executed.

## Boundary

Default is read-only assessment. A target stage alone does not authorize code mutation or commits. Authorized implementation may include verified local commits as defined above, but never implies push, PR publication, merge, release, deployment, third-party transmission or acceptance of a business outcome. A PR ready for review requires current applicable tests/lint and a complete Review advisory PASS under Git policy; an explicitly authorized remote Draft still requires passing pre-publication tests/lint and Code Review; local preparation may disclose unresolved gaps without publication. A target stage expresses intent, not blanket tool authorization; escalate missing permission before effects.
