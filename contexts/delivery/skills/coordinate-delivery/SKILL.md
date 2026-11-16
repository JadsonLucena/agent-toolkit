---
name: coordinate-delivery
description: "Coordinate an authorized SDD change across existing contexts, with evidence-gated handoffs and safe stopping or resumption."
---

# Coordinate Delivery

## Purpose

Carry a change toward the explicitly authorized target stage, selecting only the required specialist capabilities and preserving decisions and evidence across handoffs.

## Uses

* Rule: `contexts/delivery/rules/delivery.md`
* Input contract: `contracts/requirements.md` when available
* Input contract: `contracts/work-item.md` when available
* Input contract: `contracts/design-evidence.md` when available
* Input/output contract: `contracts/test-basis.md` when available
* Input/output contract: `contracts/test-evidence.md` when available
* Input/output contract: `contracts/review-evidence.md` when available
* Optional output contract: `contracts/outcome-evidence.md`

## Working State

Track `target_stage`, authorized operations and restrictions, Change Boundary, existing or planned Git PR Boundary, available accepted baselines, per-slice dependencies/readiness, source and repository snapshot identities, commit authorization and observed SHA or uncommitted/blocked state, owned specialist outputs, verification and review evidence, external effects, pending decisions, and current outcome status. Never invent checkpoint persistence.

## Workflow

```mermaid
flowchart TD
    Start["Composition and Ownership: inspect scope, stage, evidence"] --> Auth["Authorization and Gate Integrity: determine allowed steps"]
    Auth --> Strategy{"Composite PR strategy unresolved before implementation?"}
    Strategy -->|Yes| GitPlan["Git Engineer: read-only manage-pull-request plan"]
    GitPlan --> PlanReady{"PR Boundary and authorized slice reconciled?"}
    PlanReady -->|No| Block["Stop with blocker and owner"]
    PlanReady -->|Yes| Need{"Next missing applicable stage?"}
    Strategy -->|No, or already planned| Need
    Need -->|Requirements| Requirements["Route to Requirements owner"]
    Need -->|Design| Design["Route to Design owner"]
    Need -->|Implementation| Implementation["Pass PR Boundary and commit policy to Implementation owner"]
    Need -->|Testing evidence| Testing["Route to Testing owner or checks"]
    Need -->|Independent review| Review["Route to Review owner"]
    Need -->|PR preparation| Git["Route to Git owner"]
    Need -->|Reached target| Done["Outcome Handoff: report actual stage"]
    Need -->|Unapproved operation| Block
    Requirements --> Reconcile
    Design --> Reconcile
    Implementation --> Reconcile
    Testing --> Reconcile
    Review --> Reconcile
    Git --> Reconcile
    Reconcile["Controlled Coordination and Recovery: validate current evidence and Git status"] --> Decision{"Valid progress, commits and permission?"}
    Decision -->|Yes| Need
    Decision -->|Stale or source conflict| Source["Return to responsible owner"]
    Decision -->|Unsafe, missing required commit or unproductive| Block
    Source --> Block
```

This explicit cross-context workflow permits **routing** existing specialist capabilities; they continue to own their procedures and authorization gates. `/requirements/specify-and-plan-change` (where available; legacy hosts may still expose `shape-change`) performs Requirements-only composition, not the full delivery sequence. Review keeps the sole technical verdict. No tool execution is implied merely by this Markdown procedure.

## Git Planning and Commit Handoffs

* Before any implementation mutation of a composite initiative, request Git's read-only `plan` via `contexts/git/skills/manage-pull-request/SKILL.md` unless the PR Boundary is already current. Pass the resulting scope, base and dependencies to Implementation without expanding authorization.
* During Implementation, pass the caller's local-commit permission and await the Git Engineer's actual verified commit SHA or explicit blocked/uncommitted state. A requested commit or passing check alone never establishes commit success.
* After Implementation, use independent Review and the Git `prepare` operation as separate stages. `create`, push, merge, release and deployment require separate permissions.

## Output

Report the actual reached stage, per-slice completed and blocked work, applicable source and code identities, PR Boundary, Git-verified commits or explicit uncommitted/blocked state, specialist evidence, checks, Review verdict where performed, pending authorizations, recovery risks, next owners and unresolved outcome observations. When supplied, report an optional `contracts/outcome-evidence.md`-compatible observation handoff; never fabricate deployment or results.

## Boundary

Never silently expand scope, execute an unapproved mutation, promote self-review to independent gate, replay unsafe side effects, push, create/merge PRs, deploy, release or claim operational effectiveness without corresponding explicit authorization/evidence.

## Stop Conditions

Stop the affected path on missing material authority or source meaning, stale evidence that cannot be refreshed, unsafe shared writes, unknown side effects, repeated non-progress, or mandatory checks that cannot run. Preserve completed independent work.
