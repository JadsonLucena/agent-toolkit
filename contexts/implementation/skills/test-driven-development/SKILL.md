---
name: test-driven-development
description: "Run RED/GREEN/REFACTOR for the next small authorized behavior during an Implementation slice."
---

# Test-Driven Development

## Purpose

Guide implementation through one small executable behavior at a time with verifiable RED, GREEN and REFACTOR evidence when TDD is selected.

## Uses

* Rule: `contexts/implementation/rules/implementation.md`
* Optional input contract: `contracts/test-basis.md`
* Optional output contract: `contracts/test-evidence.md`
* Optional input contract: `contracts/design-evidence.md`

## Working State

Preserve the authorized slice, selected behavior and scenario identity when present, test and production change scope, current source revision, commands/results at each phase, newly discovered risks, and unresolved decisions.

## Workflow

```mermaid
flowchart TD
    Select["Test-Driven Execution: choose supported small behavior"] --> Red["RED: author and run focused failing test"]
    Red --> Why{"Failed for expected behavioral reason?"}
    Why -->|No| Diagnose["Diagnose setup, assumption or mismatch"]
    Diagnose --> Decision{"Valid correction remains in scope?"}
    Decision -->|No| Stop["Record uncertainty and stop"]
    Decision -->|Yes| Red
    Why -->|Yes| Green["GREEN: minimal production change"]
    Green --> Check{"Focused tests and relevant checks pass?"}
    Check -->|No, actionable| Green
    Check -->|No, blocked or unproductive| Stop
    Check -->|Yes| Refactor["REFACTOR: safe structure improvement or explicit no-op"]
    Refactor --> Verify{"Relevant tests still pass?"}
    Verify -->|No| Fix["Restore behavior within authorized scope"]
    Fix --> Verify
    Verify -->|Yes| Evidence["Record phase results and test-evidence handoff"]
    Evidence --> More{"Next supported behavior?"}
    More -->|Yes| Select
    More -->|No| Done["Return to implement-slice for integrated verification"]
```

The workflow implements `contexts/implementation/rules/implementation.md` sections **Test-Driven Execution** and **Verification and Feedback**; the rule is the single source for invariants. Return control to the owning Implementation workflow for holistic verification and atomic commit handoff. Do not make the RED test pass by redefining a governing specification.

## Output

Observed RED cause, GREEN passing tests, REFACTOR verification, code/test changes, related scenario identifiers where available, relevant commands and results, incomplete work or blockers. Preserve `contracts/test-evidence.md` semantics; do not label unrun or failed tests passed.

## Boundary

Only test and production edits within the authorized Implementation slice; no upstream requirement approvals, unrelated refactoring, independent Review verdict, Git push, PR publication, deployment or unapproved external side effect.

## Stop Conditions

Stop when the expected behavior is ambiguous, RED cannot be demonstrated for its expected reason, required verification is unavailable, retry has no new progress, or the next fix requires unapproved scope or side effects.
