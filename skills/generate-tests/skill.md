# Generate Automated Tests

## Purpose

Use when creating, extending, or modifying automated tests. Generate complete, maintainable tests while applying `rules/testing.md`.

## Workflow

1. **Understand the context**

   * Read the behavior under test, its public contract, immediate collaborators, and nearby test conventions before making changes.
   * Determine expected behavior, scope, and boundaries.
   * Identify and follow the project's testing framework, assertion library, mocking tools, test commands, and conventions from repository evidence such as existing tests, configuration, manifests, and scripts.
   * State material assumptions explicitly. If ambiguity can materially change the expected behavior, ask rather than guess.

2. **Map behavior and risk**

   * Identify and prioritize scenarios by behavior criticality and risk, including critical paths, edge cases, invariants, boundaries, decisions, states, side effects, failure modes, and realistic misuse.
   * Select relevant techniques such as Equivalence Partitioning, Boundary Value Analysis, Decision Tables, State Transition, Use Case-Based, Path Analysis, Pairwise, Negative Testing, Property-Based Testing, or Fuzz Testing.

3. **Review design and testability**

   * Evaluate the Design and Testability Smells in `rules/testing.md`.
   * If a probable issue materially harms testability, maintainability, predictability, or architectural integrity, output a **Developer Alert** before generating the full test suite and explain the issue concisely.
   * For legacy or constrained code, prefer characterization tests when needed to make change safe.

4. **Select the test strategy**

   * Define the success criteria the tests must prove.
   * Choose the lowest test level that provides sufficient confidence.
   * Define the required scenarios and whether specialized testing is relevant.
   * Select appropriate doubles and isolation boundaries.

5. **Generate the tests**

   * Follow project conventions and `rules/testing.md`.
   * Keep setup minimal and explicit.
   * Use realistic, non-sensitive data.
   * Generate complete, runnable tests.

6. **Validate the result**

   * Confirm the tests protect intended contracts, rules, invariants, or outcomes.
   * Confirm relevant success, failure, edge, boundary, state, side-effect, retry, replay, idempotency, and substitutability concerns were considered.
   * Confirm determinism, isolation, reproducibility, and CI suitability.
   * Confirm the tests avoid shallow assertions, over-mocking, brittle implementation checks, and unnecessary complexity.
   * Run the narrowest relevant verification first, then the applicable project quality gates.
   * Read verification evidence and diagnose failures before changing code.
   * When the project uses quality baselines or ratcheted metrics, preserve or improve them; do not introduce measurable regressions.
   * Record the verification commands executed and their outcomes.
   * Ensure a developer can understand the test intent and likely failure reason from its name, setup, and assertions.
   * If verification fails, diagnose and fix the root cause within scope, then rerun the affected checks until the success criteria pass or further progress is blocked by unavailable verification, a material blocker, an out-of-scope fix, or unproductive repeated attempts.

## Output

* Start with a brief summary of the test strategy and material risks.
* If a **Developer Alert** is required, present it before the tests.
* Provide complete, copy-pasteable test code in standard Markdown code blocks.
* Report verification commands and outcomes, including failing, skipped, blocked, or unexecuted checks, measurable regressions, and material uncertainty; never imply successful validation when verification is incomplete.
* Keep explanations concise; let test names and assertions describe the behavior.
