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

## Operational Graph

```mermaid
stateDiagram-v2
    [*] --> InspectRepository
    InspectRepository --> IdentifyIntentions

    state IntentEvidence <<choice>>
    IdentifyIntentions --> IntentEvidence
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

## Workflow

1. Inspect the current branch, upstream, working tree, staged changes, unstaged changes, relevant diff, nearby commit conventions, and explicit developer context.
2. Identify the logical intentions and dependencies represented by the authorized changes.
3. If semantic intent or the relationship between changes is materially ambiguous, ask before partitioning or committing.
4. Partition the authorized changes into the smallest coherent set of atomic commits; do not partition by file boundaries alone.
5. Preserve unrelated pre-existing staged and working-tree changes.
6. Stage exactly one logical unit, using path- or hunk-level staging when necessary.
7. Inspect the complete staged diff.
8. Correct staging when it contains independent intents, unrelated changes, or omits changes required for a coherent and verifiable unit.
9. Apply the shared quality-gate discovery and evidence policy from `contexts/git/rules/git.md` to the staged unit: discover project lint, test, established coverage and other required checks, without assuming a hook or configured command ran.
10. Inspect the effective pre-commit hook path and repository-managed tooling; identify checks the hook will enforce on commit at equivalent or stronger scope. A hook that has not yet fired is not completed verification; confirm its execution and result during commit creation.
11. Reconcile valid existing results and reliably enforceable commit-time hooks against required checks. Run missing lint, tests, and established coverage-enabled tests explicitly when authorized; avoid duplicate runs only where equivalent checks will demonstrably be enforced and their outcomes verified.
12. If any required check fails, cannot run, is stale or cannot be verified, diagnose and block commit creation. Do not change production/test implementation or weaken a gate under commit-only authorization.
13. Derive type, scope, summary, body, breaking-change metadata, and references from the staged diff and verified context.
14. Ask before committing when material commit semantics remain ambiguous.
15. Create the commit only when the staged diff and message describe the same logical unit and all required checks either passed in preflight or will be enforced by the effective hook during commit creation; verify hook results before claiming success.
16. Inspect the resulting commit and repository status.
17. Repeat for remaining authorized logical units. Re-evaluate checks when repository state, staged content, or hook behavior materially changes.
18. Stop when repository state is ambiguous, required verification is unavailable or fails, a material blocker remains, or continuing would require changing implementation semantics beyond staging/partitioning the already-authorized change set.

## Boundaries

* Commit authorization permits staging and partitioning the already-authorized changes, but it does not authorize editing production or test implementation to make verification pass.
* Commit authorization does not authorize push, merge, rebase of shared history, tag, release, branch deletion, worktree mutation, or remote-ref mutation.
* Do not bypass hooks, required checks, branch protections, signing requirements, or repository policy.
* Do not install/configure coverage tooling, create coverage thresholds, or change test policy merely to satisfy commit verification unless separately authorized.
* Hook presence alone is not verification evidence; follow the shared evidence-scope and freshness policy in `contexts/git/rules/git.md`.
* Do not amend or rewrite published history unless separately authorized and sufficiently verified.

## Output

Report the commits created, the logical intent of each commit, discovered quality gates, checks satisfied explicitly or by the effective hook, coverage mode used when applicable, remaining changes, and any blocked or unresolved state. Never claim a commit exists without repository evidence.
