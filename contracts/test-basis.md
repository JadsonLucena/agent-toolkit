# Test Basis Contract

## Purpose

Define an optional, vendor-neutral behavioral test basis shared with the Testing context without requiring a dependency on Requirements workflows.

This contract preserves behavioral intent and scenario identity. It does not prescribe Gherkin, Cucumber, a test framework, or a serialization format.

## Semantics

A testing handoff may include, when material and known:

* `context_id` — initiative or change context that relates the evidence to other artifacts;
* `subject` — feature, behavior, change, component, defect, slice, or work item under test;
* `source_refs` — requirement, specification, work-item, rule, use-case, decision, defect, code, or other evidence references;
* `intended_behavior` — supported observable behavior to verify;
* `acceptance_conditions` — observable evidence of satisfaction;
* `business_rules` and `invariants` — domain constraints that tests may need to protect;
* `states`, `boundaries`, and `failure_conditions` — material behavioral partitions;
* `constraints` — relevant business, technical, security, performance, compatibility, data, or operational constraints;
* `failure_model` — expected failures, partial failures, timeout/retry, duplicate/replay, dependency outage, concurrency, or other reliability assumptions when material;
* `quality_fit_criteria` — observable quality conditions and justified thresholds when supplied;
* `security_obligations` — supported authorization, information, purpose, delegation, organizational, or misuse constraints when supplied;
* `risk_notes` — evidenced risk areas, failure consequences, or verification priorities;
* `known_gaps` — unresolved or intentionally unspecified behavior that must not be silently converted into expected behavior;
* `assumptions` — material assumptions and confirmation state;
* `provenance` — enough source context to distinguish direct evidence, decisions, assumptions, and derived implications.

## Scenario Set

When scenarios are useful for behavioral understanding, the test basis may contain a Scenario Set.

The Scenario Set should preserve:

* `scenario_set_id` — stable identity within the change or requirements scope when a set identity is useful;
* `scenarios` — the behavioral scenarios relevant to the supplied test basis.

Each material scenario may contain:

* `scenario_id` — stable identifier within the scenario set;
* `title` or concise behavioral intent;
* `source_refs` — requirement, business rule, use case, slice, decision, defect, or other sources that justify the scenario;
* `dimensions` — useful classifications such as positive/negative, misuse, main/alternative/exception, interaction/context/system-internal, current/desired-state, or exploratory/explanatory/descriptive;
* `context` — relevant starting state or environmental conditions;
* `preconditions` — obligations that must already hold before the scenario starts;
* `trigger_or_action` — event, actor action, or condition that exercises the behavior;
* `expected_outcomes` — observable results and guarantees;
* `applicable_rules` and `invariants`;
* `acceptance_refs` or fit-criterion references when applicable;
* `examples` — concrete examples illustrating the scenario;
* `counterexamples` — examples that must not satisfy the behavior;
* `boundaries` — behavior-change boundaries or representative boundary cases;
* `assumptions` and `open_questions`;
* `risk_notes` — scenario-specific risk or consequence information when useful.

A scenario identifier is semantic identity, not a framework-specific test name. Do not encode a required test level, implementation component, or automation technology into the identifier.

## Scenario, Example, and Test Separation

Preserve these distinct meanings:

* **Scenario** — a meaningful behavioral situation or path that should be understood or verified.
* **Example** — a concrete instance that illustrates a scenario, rule, or boundary.
* **Automated Test** — executable verification evidence for one or more scenarios/examples.

A scenario may have multiple examples and multiple automated tests. One automated test may cover multiple related scenarios when that relationship is explicit.

Do not collapse scenarios into examples merely because a framework expresses both as executable cases.

## Integrity

* This contract carries evidence; it does not replace the authoritative requirement, code, or project source.
* Requirements, decisions, assumptions, known gaps, and unresolved questions must remain distinguishable.
* Testing may consume only the relevant subset.
* Material conflicts with implementation or other project evidence must remain explicit.
* Missing expected behavior must not be invented merely to make a scenario or test executable.
* Stable `scenario_id` values supplied upstream must be preserved by downstream consumers.
* Business examples remain business evidence; Testing may automate them but should not rewrite them into implementation-coupled behavior merely for convenience.
* The contract may support BDD, Example Mapping, or Specification by Example, but it does not require Gherkin or any particular automation framework.
* When material ambiguity changes what a correct scenario or test should assert, request clarification or report the unresolved behavior.
* Testing remains usable when this handoff or a Scenario Set does not exist.

## Test Evidence Handoff

Testing should report scenario-to-automation coverage through `contracts/test-evidence.md` when stable scenario identities are available and traceability is material.

Do not mutate the upstream Scenario Set merely to attach execution state or framework-specific test references.

## Portability

The contract defines meaning rather than a required serialization format.

Adapters may render the same Scenario Set as Gherkin scenarios, Cucumber examples, test-case-management records, Markdown, JSON/YAML, framework test cases, or another representation as long as scenario identity, source relationships, expected behavior, and unresolved uncertainty are preserved.
