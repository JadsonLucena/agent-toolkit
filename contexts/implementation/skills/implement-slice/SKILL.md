---
name: implement-slice
description: "Implement an authorized production-code slice with local verification and safe atomic Git handoffs. Use for feature or defect implementation; use Testing for test-only changes."
---

# Implement Slice

## Purpose

Implement one supported, independently verifiable code slice without silently modifying its requirement meaning or crossing its mutation boundary.

## Uses

* Rule: `contexts/implementation/rules/implementation.md`
* Skill: `contexts/implementation/skills/test-driven-development/SKILL.md`
* Optional input contract: `contracts/design-evidence.md`
* Optional input contract: `contracts/requirements.md`
* Optional input contract: `contracts/work-item.md`
* Optional input contract: `contracts/test-basis.md`
* Optional output contract: `contracts/test-evidence.md`

## Working State

Keep the current authorized slice, source baseline, Change Boundary, PR-plan status and boundary when material, affected files, repository state, effective local-commit permission and its authorization source, Git handoff result and commit identity, tests, intended checks, relevant decisions, unresolved risks, retry history, and observed outcomes. Preserve external-effect identifiers when material to safe resumption.

## Workflow

```mermaid
flowchart TD
    Start["Authority and Slice Integrity: inspect invoking authority, approved scope and repository"] --> ScopeGate{"Scoped implementation mutation authorized?"}
    ScopeGate -->|No or unclear| Block
    ScopeGate -->|Yes| ResolveCommit["Resolve local-commit authority from implementation permission and explicit restrictions"]
    ResolveCommit --> Strategy{"Composite change needs a PR strategy before code mutation?"}
    Strategy -->|Yes, missing| PlanPR["Git Engineer: read-only plan-pull-requests handoff"]
    PlanPR --> PlanReady{"PR Boundary and allowed slice reconciled?"}
    PlanReady -->|No| Block["Stop with evidence and responsible owner"]
    PlanReady -->|Yes| Plan["Safe Implementation: choose next coherent intention"]
    Strategy -->|Not required or existing plan valid| Plan
    Plan --> Test{"Test-first or TDD appropriate and authorized?"}
    Test -->|Yes| Prepare["Select smallest behavior and test design"]
    Test -->|No| Change["Apply minimal in-scope implementation"]
    Prepare --> Change
    Change --> Check["Verification and Feedback: execute applicable checks"]
    Check --> Gate{"Verified and coherent intention?"}
    Gate -->|Yes| CommitAuthority{"Resolved local-commit authority permits commit?"}
    CommitAuthority -->|Yes| Commit["Git Engineer: create-semantic-commits handoff"]
    Commit --> CommitVerified{"Commit SHA, intended diff and resulting state verified?"}
    CommitVerified -->|Yes| More{"More authorized intentions?"}
    CommitVerified -->|No, failed or unavailable| Block
    CommitAuthority -->|Explicitly denied| Uncommitted["Record uncommitted verified intention and restriction"]
    CommitAuthority -->|Unknown| Block
    Uncommitted --> Continuation{"Explicit permission for safe uncommitted continuation?"}
    Continuation -->|Yes| More
    Continuation -->|No| DoneUncommitted["Return uncommitted state; stop before next intention"]
    More -->|Yes| Plan
    More -->|No| Done["Completion: record evidence and status"]
    Gate -->|Actionable failure| Diagnose["Diagnose and revise only within authorized scope"]
    Diagnose -->|Material new progress possible| Change
    Diagnose -->|Unproductive or out of scope| Block
    Gate -->|Missing authority or unsafe effect| Block
```

Apply the named sections of `contexts/implementation/rules/implementation.md`. When TDD is selected, delegate its inner RED/GREEN/REFACTOR loop to `contexts/implementation/skills/test-driven-development/SKILL.md` rather than rewriting it here. Git owns semantic commit execution; Implementation supplies a completed in-scope intention and waits for verified Git evidence before selecting another intention when a local commit is permitted. Do not treat silence in an authorized implementation plan as missing commit authority. When TDD is selected, multiple RED/GREEN/REFACTOR cycles may complete the same intention; return here for integrated verification and Git handoff as soon as that intention is complete, before selecting a different intention.

## Cross-context Handoffs

* **Before mutation, if PR decomposition is material:** ask the Git Engineer to use `contexts/git/skills/manage-pull-request/SKILL.md` in read-only `plan` mode under `contexts/git/rules/pull-request.md`, unless a current plan already exists. Consume its PR Boundary, included/excluded scope, dependencies and intended base without granting additional implementation or publication authority.
* **After each verified intention:** hand the Git Engineer the current atomic change boundary (including paths/hunks and unrelated-work exclusions), actual workspace/revision, observed checks and resolved effective local-commit authorization. Git applies `contexts/git/skills/create-semantic-commits/SKILL.md` and returns an observed commit SHA, exact committed scope, resulting repository status, or a blocker. Never perform an unverified substitute commit or count a requested handoff as a completed commit.
* **Explicitly prohibited local commits:** retain the verified intention as uncommitted evidence; do not automatically begin another intention without explicit safe-continuation authorization. A PR plan does not authorize a commit, push, PR creation or merge.

## Output

Return the bounded implementation state for a separate Integration stage; do not initiate independent Code Review, Git PR preparation/creation or merge as a side effect of completing this Skill. Report implementation files and affected interfaces, source and design references where available, verification commands and observed results, verified commit SHAs and resulting Git state when authorized and completed, or explicit uncommitted/blocked handoff status; PR-plan status when material; residual risks and readiness. Use `contracts/test-evidence.md` for supported scenario coverage without inventing passed tests.

## Boundary

Only the expressly authorized source and test mutations for the selected slice. A missing or conflicting implementation mutation authorization blocks changes; do not infer it from a stage name. No implicit requirement approval, unrelated refactoring, push, PR creation, release, deploy, secrets access, destructive external operation, or claims of independent Review.

## Stop Conditions

Block the affected slice on unsupported acceptance semantics, missing material guarantees, unauthorized effects, unsafe repository state, failed/unverified required Git handoff, unproductive retries, or unavailable mandatory verification; preserve independently valid evidence.
