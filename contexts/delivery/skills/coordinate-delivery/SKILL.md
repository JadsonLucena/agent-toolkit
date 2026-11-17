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

## Working State

Track `target_stage`, authorized operations and restrictions, Change Boundary, existing or planned Git PR Boundary, available accepted baselines, per-slice dependencies/readiness, intended and actual PR head/base, local verification and independent Review evidence identity, review profile and verdict, preparation state, published PR status, post-publication checks/approvals, merge authorization and observed target state, commit authorization and observed SHA or uncommitted/blocked state, owned specialist outputs, external effects, pending decisions, and current outcome status. Never invent checkpoint persistence.

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
    Need -->|Integration after Implementation| Preflight["Integration: inspect final head/base and applicable tests/lint"]
    Need -->|Existing published PR requires integration| PostTarget
    Need -->|Reached authorized target| Done["Outcome Handoff: report actual stage"]
    Need -->|Unapproved operation| Block
    Requirements --> Reconcile
    Design --> Reconcile
    Implementation --> Reconcile
    Preflight --> Checks{"Applicable local checks current and passing?"}
    Checks -->|Missing or stale| Testing["Testing owner or authorized checks: collect actual evidence"]
    Testing --> ChecksResult{"Required checks now pass?"}
    ChecksResult -->|Yes| Review["Review owner: independent Code Review"]
    ChecksResult -->|No, correctable| Fix["Route defect to Implementation or responsible owner"]
    ChecksResult -->|No, explicit draft intent| DraftPrepare["Git: prepare truthful draft with stated gaps"]
    Checks -->|Yes| Review
    Review --> ReviewResult{"Advisory PASS for final head/base?"}
    ReviewResult -->|PASS, reviewed stage reached| DoneReviewed["Report independent Review evidence; stop before PR preparation"]
    ReviewResult -->|PASS, PR stage authorized| ReadyPrepare["Git: prepare ready PR under existing Git floor"]
    ReviewResult -->|No, correctable| Fix
    ReviewResult -->|No, explicitly authorized draft| DraftPrepare
    ReviewResult -->|No, cannot proceed| Block
    Fix --> Reconcile
    ReadyPrepare --> PublishDecision{"Prepared state permits target action?"}
    DraftPrepare --> PublishDecision
    PublishDecision -->|Only prepare requested or no creation authority| Prepared["Report pr-prepared status and limits"]
    PublishDecision -->|Blocked by Git policy| Block
    PublishDecision -->|Ready and separately authorized creation, or explicitly authorized draft| GitCreate["Git: create PR under Git readiness policy"]
    GitCreate --> Created["Verify published PR identity, head/base and draft/ready state"]
    Created --> PostTarget{"PR-created is target stage?"}
    PostTarget -->|Yes| Done
    PostTarget -->|No, integration requested| PostChecks["Check actual post-PR CI, approvals, branch protection, evidence freshness"]
    PostChecks --> PostGate{"All merge prerequisites valid for current PR head/base?"}
    PostGate -->|Changed code or correctable failure| Fix
    PostGate -->|Missing approval or permission| Block
    PostGate -->|Yes and explicit merge authorization| GitMerge["Git: authorized branch integration under repository policy"]
    GitMerge --> Confirm["Verify merged target revision and resulting integration state"]
    Confirm -->|Verified| Done
    Confirm -->|Failed or unknown| Block
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

## Integration Handoffs

* After Implementation, route final code/commit identity and verification evidence into Integration; collect missing authorized tests/lint with their actual execution scope, then request independent Code Review through Review's existing capability. Review owns the single verdict; the Git PR readiness rule decides which evidence permits a ready PR.
* An advisory `PASS` on the current intended head/base permits Git `prepare` for ready status when other checks pass. On `FAIL`, `INCOMPLETE`, or stale evidence, route correctable work to its owner and reverify affected outputs, or prepare/publish **only an explicitly authorized Draft** with truthful limitations under the Git rule.
* Git owns PR `prepare` and separately authorized `create`. A request for `pr-prepared` stops before publication; a request for `pr-created` stops after verifying the remote PR. Do not infer push from create authorization or merge from a created PR.
* After creation, collect actual post-PR checks and required approvals for the current PR head/base. If code changes, return affected work to Implementation and revalidate necessary checks and independent Review. Merge only through separately authorized Git integration when repository protections are satisfied, and verify the resulting target branch before reporting `integrated`.

## Output

Report the actual reached stage, per-slice completed and blocked work, applicable source, implementation and PR head/base identities, PR Boundary, Git-verified commits or explicit uncommitted/blocked state, specialist evidence, independent Review profile/verdict and tested scope where performed, readiness and remote PR status when available, post-PR checks/approvals, merge verification only when observed, pending authorizations, recovery risks, next owners and unresolved outcome observations.

## Boundary

Never silently expand scope, execute an unapproved mutation, promote self-review to independent gate, replay unsafe side effects, push, create/merge PRs, deploy, release or claim operational effectiveness without corresponding explicit authorization/evidence.

## Stop Conditions

Stop the affected path on missing material authority or source meaning, stale evidence that cannot be refreshed, unsafe shared writes, unknown side effects, repeated non-progress, or mandatory checks that cannot run. Preserve completed independent work.
