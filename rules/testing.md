# Automated Testing Rules

## Core Principles

* Apply FIRST when appropriate, while keeping tests clear, focused, deterministic, and maintainable.
* Test intent through observable behavior and stable boundaries. Assertions must protect the relevant contract, rule, invariant, or outcome rather than reproduce implementation details.
* Keep each test focused on one behavior or scenario. Multiple assertions are acceptable when they validate facets of the same outcome.
* For side effects, assert relevant effects that must occur and must not occur.
* Prefer KISS and balance DRY with DAMP. Accept small duplication when it improves clarity.
* Keep relevant test data explicit and hide irrelevant defaults behind builders, factories, fixtures, or equivalent helpers.
* Use domain-relevant test data without real credentials, secrets, tokens, or PII.
* Test names must describe expected behavior, not implementation.
* Follow project conventions for language, naming, lint, formatting, and style. If none exist, prefer English.
* Add comments only for non-obvious business rules, formulas, magic values, or complex reasoning.
* Focus on behavior and risk coverage, not coverage percentage alone.

## Test Levels

* Choose the lowest test level that provides sufficient confidence at a reasonable cost. Use the Testing Pyramid as a heuristic, not a mandatory distribution.
* Consider Unit, Component, Integration, Contract, System/E2E, and Acceptance tests when applicable.
* Acceptance describes intent and may be validated at any suitable level.

## Test Structure and Design

* Use Arrange/Act/Assert for structural clarity and Given/When/Then for narrative workflows when it improves readability; follow project convention when present.
* Prefer a single Act/When phase; use multiple phases only for explicit workflows or state transitions.
* Explore and cover relevant edge cases, risks, invariants, boundaries, decisions, states, and input partitions.
* Use cyclomatic complexity only as a signal for additional path analysis.
* For decisions, defaults, fallbacks, and transformations, assert observable consequences and relevant invariants.
* Prefer parameterized tests when scenarios share behavior and differ mainly by input and expected outcome, provided readability is preserved.
* Periodically evolve scenarios, test data, assumptions, and techniques to avoid the Pesticide Paradox.

## Test Doubles and Dependencies

Use the smallest appropriate double:
* **Dummy**: required but irrelevant value
* **Stub**: predefined responses
* **Fake**: simplified working implementation
* **Spy**: records interactions for later verification
* **Mock**: verifies an expected interaction or protocol
* Prefer state or output verification when it provides equivalent confidence; verify interactions when the interaction itself is part of the contract.
* Unit tests must not depend on real external APIs, databases, networks, filesystems, or infrastructure.
* For unit tests, prefer a Fake persistence abstraction, such as an In-Memory Repository.
* When persistence-specific behavior matters, use an integration test against an isolated instance of the production database engine.
* In integration tests, use real implementations for the components whose integration is under test; dependencies outside that boundary may use doubles, simulators, emulators, or test servers.
* Tests that mutate persistent or shared resources must define an isolation and cleanup strategy.
* Prefer existing or standard testing tools; introduce new heavy test infrastructure only when requested or already justified by the project.

## Determinism and Failure Behavior

* Control relevant nondeterminism: time, timezone, randomness, UUIDs, network, filesystem, environment, process state, and concurrency scheduling.
* Randomized, fuzz, and property-based tests must preserve the seed or minimized failing input.
* Properly await, join, or resolve asynchronous operations.
* Prefer explicit synchronization, fake clocks, bounded polling, or eventual assertions over arbitrary sleeps.
* Tests must not depend on execution order or shared mutable state unless that dependency is the behavior under test.
* When dependencies fail, verify the observable result: propagation, translation, fallback, retry, compensation, or controlled failure.
* For multi-step operations, test relevant partial failures and verify invariants, rollback, compensation, recovery, or explicitly allowed partial state.
* Test idempotency, retry, replay, and duplicate execution when repeated operations can alter state or produce side effects.
* Cover the same critical risk at multiple levels only when each level provides distinct confidence.

## Specialized Testing

Apply when relevant to system risk:

* **Contract testing**: verify consistent and predictable contracts across APIs, services, SDKs, events, abstractions, and interchangeable implementations. When substitutability applies, implementations must preserve observable semantics, not strengthen declared preconditions, weaken declared postconditions, or violate declared invariants.
* **Security testing**: authentication, authorization, injection, privilege boundaries, and sensitive-data handling.
* **Concurrency testing**: race conditions, synchronization, atomicity, ordering, constraints, and shared-state invariants.
* **Resilience and fault-injection testing**.
* **Performance, load, stress, and scalability testing**.
* **Property-based testing** for invariants and algebraic properties.
* **Fuzz testing** for malformed, unexpected, or adversarial inputs.
* **Mutation testing** to assess whether tests detect meaningful behavioral changes.

For UI/component tests:

* Prefer user-observable behavior and interactions over internal component state.
* Prefer accessible queries when supported by the platform.
* Use snapshots as complementary evidence, not as a substitute for behavioral assertions.

Use quality metrics as diagnostic signals, not proof of correctness; follow project-defined thresholds instead of imposing universal targets.

## Regression and Characterization

* When fixing a defect, add a regression test that fails before the fix and passes after it whenever practical.
* For legacy or externally constrained code that must be safely changed, consider characterization tests before refactoring.
* Characterization tests capture current observable behavior; they do not legitimize poor design.
* Document the purpose of a characterization test when it is not obvious.

## Design and Testability Smells

Treat the following as signals for developer review before testing.

### Dependency and Construction

* Domain or application code directly instantiates infrastructure or concrete low-level dependencies that should normally be inverted.
* A class creates objects whose lifecycle or ownership does not naturally belong to it.
* Object construction conflicts with the intended association, aggregation, composition, dependency, or architectural boundary.
* Consider legitimate composition, aggregate ownership, Value Objects, factories, builders, composition roots, framework-managed construction, and other intentional creational patterns before flagging construction.
* Flag inappropriate ownership, lifecycle, coupling, or dependency direction, not the use of `new` itself.

### Responsibility

* A function, method, or class has multiple unrelated responsibilities, excessive branching, hidden side effects, or unclear boundaries that materially increase testing complexity.
* Consider Divergent Change and Shotgun Surgery when they indicate poor responsibility boundaries.

### Predictability

* Interfaces for similar use cases are unnecessarily inconsistent in naming, structure, semantics, or usage patterns, making them less predictable or intuitive.

### Parameter Count

* Follow the Clean Code heuristic: prefer 0–1 parameters; 2 is acceptable; avoid 3; more than 3 requires strong justification. Consider legitimate domain or technical constraints before recommending refactoring.

Legacy, externally constrained, framework-controlled, or backward-compatible code may require characterization tests before redesign.

## Quality Guardrails

* Assertions must be strong enough to prove intended behavior.
* Keep tests free of unrelated scenarios, complex test logic, over-mocking, brittle implementation assertions, hidden environmental dependencies, and irrelevant data.
* Use snapshots or golden files only when they provide meaningful behavioral value.
* Do not add tests that fail to reduce a meaningful, identifiable risk.
* Do not create abstractions solely to remove harmless duplication.
* Do not make verification pass by weakening meaningful assertions, removing relevant coverage, skipping tests, suppressing failures, or changing unrelated behavior. Address the root cause or report the blocker.
