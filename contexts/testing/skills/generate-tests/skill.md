# Generate Automated Tests

## Purpose

Use when creating, extending, or modifying automated tests. Generate complete, maintainable tests while applying `contexts/testing/rules/testing.md`.

## Operational Graph

```mermaid
flowchart TD
    START --> Understand
    Understand --> Infer
    Infer --> DefineSuccess
    DefineSuccess --> Review

    Review -->|No material issue| Generate
    Review -->|Material issue| DeveloperAlert

    DeveloperAlert -->|Can continue safely| Generate
    DeveloperAlert -->|Requires developer decision| Stop

    Generate --> Verify

    Verify -->|Success criteria satisfied| Done
    Verify -->|Actionable in-scope failure| Diagnose
    Verify -->|Verification unavailable or blocked| Report
    Verify -->|Required fix out of scope| Report

    Diagnose -->|Test-artifact defect can be fixed| Generate
    Diagnose -->|Production or out-of-scope defect| Report
    Diagnose -->|Material blocker or unproductive attempts| Report

    Report --> Stop
```

## Working State

The workflow progressively establishes and refines:

* Behavioral context, contract, scope, and boundaries.
* Optional requirement specification, acceptance/fit criteria, business examples, counterexamples, boundaries, failure model, or `contracts/test-basis.md` evidence when supplied.
* Material assumptions and unresolved uncertainty.
* Project testing tooling and conventions.
* Risks, examples, counterexamples, scenario partitions, failure assumptions, and relevant test techniques.
* Success criteria and test strategy.
* Generated or modified tests.
* Verification evidence and quality-gate outcomes.
* Blockers, out-of-scope requirements, or unresolved failures.

## Execution Contracts

### Understand

**Produces:** behavioral contract, scope, boundaries, and material assumptions.

### Infer

**Requires:** understood context.

**Produces:** project testing tooling, conventions, prioritized risks, scenarios, and relevant techniques.

### Define Success

**Requires:** behavior, risks, and project context.

**Produces:** observable success criteria, test level, required scenarios, doubles, and isolation boundaries.

### Review

**Requires:** understood behavior and proposed test strategy.

**Produces:** continue, **Developer Alert**, or a blocker requiring developer decision.

### Generate

**Requires:** success criteria and test strategy.

**Produces:** complete, runnable tests consistent with the project and `contexts/testing/rules/testing.md`.

### Verify

**Requires:** generated or modified tests.

**Produces:** verification evidence and one of:

* success;
* actionable in-scope failure;
* unavailable or blocked verification;
* required fix outside scope.

### Diagnose

**Requires:** failed verification evidence.

**Produces:** a correction limited to test artifacts, or a reported production/out-of-scope defect or material blocker.

## Workflow

1. **Understand the context**

   * Read the behavior under test, its public contract, immediate collaborators, and nearby test conventions before making changes.
   * When requirement specifications, acceptance/fit criteria, business rules, invariants, examples, counterexamples, boundaries, quality/security obligations, or a `contracts/test-basis.md` artifact are supplied, use them as additional behavioral evidence without requiring the Requirements context or invoking its internal skills.
   * Preserve business examples as business evidence. Do not rewrite them into UI, transport, persistence, or framework details unless those details are part of the required behavior.
   * Determine expected behavior, scope, and boundaries.
   * Reconcile supplied planning evidence with observable implementation and project evidence. Surface material conflicts instead of silently choosing one source.
   * State material assumptions explicitly. If ambiguity can materially change the expected behavior, ask rather than guess.

2. **Infer project context and map behavior and risk**

   * Identify and follow the project's testing framework, assertion library, mocking tools, test commands, and conventions from repository evidence such as existing tests, configuration, manifests, and scripts.
   * Start from supplied rules/examples when available, then identify uncovered behavior by criticality and risk, including critical paths, counterexamples, edge cases, invariants, boundaries, decisions, states, side effects, failure modes, and realistic misuse.
   * When a failure model is supplied or can be supported from project evidence, include relevant timeout, retry, partial-failure, duplicate/replay, dependency-outage, ordering, idempotency, or concurrency scenarios.
   * Select relevant techniques such as Equivalence Partitioning, Boundary Value Analysis, Decision Tables, State Transition, Use Case-Based, Path Analysis, Pairwise, Negative Testing, Property-Based Testing, or Fuzz Testing.

3. **Define success and test strategy**

   * Define the observable success criteria the tests must prove, preserving the distinction between business specification and the automation layer.
   * Choose the lowest test level that provides sufficient confidence.
   * Define the required scenarios and whether specialized testing is relevant.
   * Select appropriate doubles and isolation boundaries.

4. **Review design and testability**

   * Evaluate the Design and Testability Smells in `contexts/testing/rules/testing.md`.
   * If a probable issue materially harms testability, maintainability, predictability, or architectural integrity, output a **Developer Alert** before generating the full test suite and explain the issue concisely.
   * Continue only when the issue can be handled safely within scope; otherwise report the blocker or required developer decision.
   * For legacy or constrained code, prefer characterization tests when needed to make change safe.

5. **Generate the tests**

   * Follow project conventions and `contexts/testing/rules/testing.md`.
   * Keep setup minimal and explicit.
   * Use realistic, non-sensitive data.
   * Generate complete, runnable tests.
   * When the project uses BDD or Specification by Example, preserve domain-oriented examples and living-documentation value without assuming Gherkin is required.

6. **Verify the result**

   * Confirm the tests protect intended contracts, rules, invariants, or outcomes.
   * Confirm relevant success, failure, counterexample, edge, boundary, state, side-effect, retry, replay, idempotency, and substitutability concerns were considered.
   * When the change modifies previously verified behavior, run or identify the relevant regression checks rather than validating only the new slice.
   * Confirm determinism, isolation, reproducibility, and CI suitability.
   * Confirm the tests avoid shallow assertions, over-mocking, brittle implementation checks, and unnecessary complexity.
   * Run the narrowest relevant verification first, then the applicable project quality gates.
   * Read verification evidence before deciding whether the work is complete or requires diagnosis.
   * When the project uses quality baselines or ratcheted metrics, preserve or improve them; do not introduce measurable regressions.
   * Record the verification commands executed and their outcomes.
   * Ensure a developer can understand the test intent and likely failure reason from its name, setup, and assertions.

7. **Diagnose and iterate**

   * When verification exposes an actionable failure, diagnose the root cause before changing anything.
   * Correct the failure automatically only when the required change is confined to test artifacts authorized by this testing workflow.
   * When the root cause is production code, configuration, schema, infrastructure, or another non-test artifact, report the defect and evidence instead of modifying it unless separate explicit authorization exists.
   * Rerun the affected checks after an authorized test-artifact correction.
   * Continue only while meaningful progress is being made.
   * Stop and report when required verification is unavailable, a material blocker remains, a production or other out-of-scope fix is required, or repeated attempts are not producing meaningful progress.

## Boundary

This skill may create or modify test artifacts. It may diagnose defects outside testing scope, but must not change production code or other non-test artifacts unless a separate explicit authorization grants that mutation.

## Output


* Start with a brief summary of the test strategy and material risks.
* If a **Developer Alert** is required, present it before the tests.
* Provide complete, copy-pasteable test code in standard Markdown code blocks.
* Report verification commands and outcomes, including failing, skipped, blocked, or unexecuted checks, regression evidence, measurable regressions, and material uncertainty; never imply successful validation when verification is incomplete.
* Keep explanations concise; let test names and assertions describe the behavior.
