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

Track `target_stage`, authorized operations and restrictions, Change Boundary, available accepted baselines, per-slice dependencies/readiness, source and repository snapshot identities, owned specialist outputs, verification and review evidence, external effects, pending decisions, and current outcome status. Never invent checkpoint persistence.

## Workflow

```mermaid
flowchart TD
    Start["Composition and Ownership: inspect scope, stage, evidence"] --> Auth["Authorization and Gate Integrity: determine allowed steps"]
    Auth --> Need{"Next missing applicable stage?"}
    Need -->|Requirements| Requirements["Route to Requirements owner"]
    Need -->|Design| Design["Route to Design owner"]
    Need -->|Implementation| Implementation["Route to Implementation owner"]
    Need -->|Testing evidence| Testing["Route to Testing owner or checks"]
    Need -->|Independent review| Review["Route to Review owner"]
    Need -->|PR preparation| Git["Route to Git owner"]
    Need -->|Reached target| Done["Outcome Handoff: report actual stage"]
    Need -->|Unapproved operation| Block["Report required authorization; stop"]
    Requirements --> Reconcile
    Design --> Reconcile
    Implementation --> Reconcile
    Testing --> Reconcile
    Review --> Reconcile
    Git --> Reconcile
    Reconcile["Controlled Coordination and Recovery: validate current evidence"] --> Decision{"Valid progress and permission?"}
    Decision -->|Yes| Need
    Decision -->|Stale or source conflict| Source["Return issue to responsible owner"]
    Decision -->|Unsafe or unproductive| Block
    Source --> Block
```

This explicit cross-context workflow permits **routing** existing specialist capabilities; they continue to own their procedures and authorization gates. `/requirements/specify-and-plan-change` (where available; legacy hosts may still expose `shape-change`) performs Requirements-only composition, not the full delivery sequence. Review keeps the sole technical verdict. No tool execution is implied merely by this Markdown procedure.

## Output

Report the actual reached stage, per-slice completed and blocked work, applicable source and code identities, specialist evidence, checks, Review verdict where performed, pending authorizations, recovery risks, next owners and unresolved outcome observations. When supplied, report an optional `contracts/outcome-evidence.md`-compatible observation handoff; never fabricate deployment or results.

## Boundary

Never silently expand scope, execute an unapproved mutation, promote self-review to independent gate, replay unsafe side effects, push, create/merge PRs, deploy, release or claim operational effectiveness without corresponding explicit authorization/evidence.

## Stop Conditions

Stop the affected path on missing material authority or source meaning, stale evidence that cannot be refreshed, unsafe shared writes, unknown side effects, repeated non-progress, or mandatory checks that cannot run. Preserve completed independent work.
