---
name: create-semantic-commits
description: "Turn an explicitly authorized change into the smallest sequence of atomic commits. Use when the task authorizes creating commits."
---

# Create Semantic Commits

## Purpose

Use when a task explicitly authorizes creating one or more commits. Convert an authorized set of changes into the smallest coherent sequence of atomic commits while applying the Git and semantic-commit rules.

## Uses

* Rule: `contexts/git/rules/git.md`
* Rule: `contexts/git/rules/semantic-commit.md`

## Preconditions

* Creating commits is explicitly authorized for a defined change scope.
* The repository is inspectable.
* No unresolved Git operation or conflict makes committing unsafe.
* The authorized change set can be distinguished from unrelated work.

## Workflow

```mermaid
stateDiagram-v2
    [*] --> InspectRepository
    InspectRepository --> IdentifyIntentions

    state IntentEvidence <<choice>>
    IdentifyIntentions --> IntentEvidence
    state "Atomicity in semantic-commit.md" as PartitionChanges
    IntentEvidence --> PartitionChanges: sufficiently supported
    IntentEvidence --> NeedDeveloperInput: materially ambiguous
    NeedDeveloperInput --> IdentifyIntentions: clarification received

    PartitionChanges --> StageUnit
    StageUnit --> InspectStagedDiff

    state StagedUnit <<choice>>
    InspectStagedDiff --> StagedUnit
    StagedUnit --> CorrectStaging: incoherent / incomplete / unrelated
    CorrectStaging --> StageUnit
    StagedUnit --> DiscoverQualityGates: coherent atomic unit
    DiscoverQualityGates --> InspectPreCommit
    InspectPreCommit --> DetermineMissingChecks
    DetermineMissingChecks --> VerifyUnit

    state Verification <<choice>>
    VerifyUnit --> Verification
    Verification --> ComposeMessage: all required checks passed or hook-verified
    Verification --> DiagnoseFailure: failed / unavailable / unverified

    DiagnoseFailure --> Blocked: verification failed
    ComposeMessage --> EvaluateCommitSemantics

    state CommitSemantics <<choice>>
    EvaluateCommitSemantics --> CommitSemantics
    CommitSemantics --> CreateCommit: sufficiently supported
    CommitSemantics --> NeedDeveloperInput: materially ambiguous

    CreateCommit --> InspectCommit

    state CommitValid <<choice>>
    InspectCommit --> CommitValid
    CommitValid --> RemainingChanges: commit matches staged intent
    CommitValid --> Blocked: resulting state unexpected

    state RemainingChanges <<choice>>
    RemainingChanges --> IdentifyIntentions: more authorized logical units
    RemainingChanges --> Completed: none

    Completed --> [*]
    Blocked --> [*]
```

The diagram is the procedure. Apply the shared quality-gate discovery and evidence policy in `contexts/git/rules/git.md`. Apply atomicity and message shape in `contexts/git/rules/semantic-commit.md`. Do not restate those rules.

## Boundaries

* Commit authorization permits staging and partitioning the already-authorized changes, but it does not authorize editing production or test implementation to make verification pass.
* Commit authorization does not authorize push, merge, rebase of shared history, tag, release, branch deletion, worktree mutation, or remote-ref mutation.
* Do not bypass hooks, required checks, branch protections, signing requirements, or repository policy.
* Do not install/configure coverage tooling, create coverage thresholds, or change test policy merely to satisfy commit verification unless separately authorized.
* Hook presence alone is not verification evidence; follow the shared evidence-scope and freshness policy in `contexts/git/rules/git.md`.
* Do not amend or rewrite published history unless separately authorized and sufficiently verified.

## Output

Report the commits created, the logical intent of each commit, discovered quality gates, checks satisfied explicitly or by the effective hook, coverage mode used when applicable, remaining changes, and any blocked or unresolved state. Never claim a commit exists without repository evidence.
