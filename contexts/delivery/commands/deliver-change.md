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
* Optional output contract: `contracts/outcome-evidence.md`

## Inputs

* Change objective, approved scope and current artifacts or source references.
* Explicit `target_stage`: `planned`, `designed`, `implemented`, `reviewed`, or `pr-prepared`, plus applicable operation-level permissions.
* Existing repository snapshot, stage evidence and blockers when known.
* Runtime capabilities and resource/approval limits when known.

## Output

Actual completed stage and source/revision identity, next safe required capability, routed specialist results, checks, review status where performed, blockers, pending decisions, and evidence of operations actually executed.

## Boundary

Default is read-only assessment. No implicit code mutation, commit, push, PR publication, merge, release, deployment, third-party transmission or acceptance of a business outcome. A target stage expresses intent, not blanket tool authorization; escalate missing permission before effects.
