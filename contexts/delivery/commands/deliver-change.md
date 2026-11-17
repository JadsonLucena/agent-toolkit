# Deliver Change

## Intent

Coordinate a bounded change from its current evidence state toward one explicitly requested SDLC/SDD delivery stage.

## Invocation

Select the Delivery Coordinator and its cross-context workflow. If `target_stage` or authorized mutation scope is absent, operate read-only to assess readiness and next actions. Explicit stage/operation authorization is required for implementation, source/test edits and local commits; independently authorize remote PR creation, push, merge, release or deployment. Routing never grants permissions owned by the invoked specialty.

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

## Inputs

* Change objective, approved scope and current artifacts or source references.
* Explicit `target_stage`: `planned`, `designed`, `implemented`, `reviewed`, `pr-prepared`, `pr-created`, or `integrated`, plus applicable operation-level permissions. `pr-created` requires explicit PR-creation authority; `integrated` additionally requires merge authority and all repository prerequisites.
* Existing repository snapshot, stage evidence, accepted source and scenario references with revision identity, Git-owned PR plan/Boundary when available, local-commit restrictions and blockers when known. Missing source material is retrieved only when relevant and authorized.
* Runtime capabilities, intended PR base/head and PR publication state, review/check/approval evidence, repository branch protections, and resource/approval limits when known.

## Output

Actual completed stage and source/revision identity, next safe required capability, routed specialist results, PR-plan evidence where material, verified commit identities or explicit uncommitted/blocked state, current verification and independent Review evidence, prepared/published PR identity when observed, post-PR checks and approvals, verified merge target only when integration actually occurred, blockers, pending decisions, and evidence of operations actually executed.

## Boundary

Default is read-only assessment. No implicit code mutation, commit, push, PR publication, merge, release, deployment, third-party transmission or acceptance of a business outcome. A PR ready for review requires current applicable tests/lint and independent advisory Review PASS under Git policy; an explicitly authorized Draft can disclose gaps without claiming ready. A target stage expresses intent, not blanket tool authorization; escalate missing permission before effects.
