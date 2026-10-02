# Test Basis Contract

## Purpose

Define an optional, vendor-neutral test basis shared with the Testing context without requiring a dependency on Requirements workflows.

## Semantics

A testing handoff may include, when material and known:

* `context_id` — initiative or change context that relates the evidence to other artifacts;
* `subject` — feature, behavior, change, component, defect, or work item under test;
* `source_refs` — requirement, specification, work-item, decision, defect, code, or other evidence references;
* `intended_behavior` — supported observable behavior to verify;
* `acceptance_conditions` — observable evidence of satisfaction;
* `business_rules` and `invariants` — domain constraints that tests may need to protect;
* `examples` — concrete domain examples that illustrate a rule or expected behavior;
* `counterexamples` — concrete examples that should not satisfy the rule or behavior;
* `states`, `boundaries`, and `failure_conditions` — material behavioral partitions;
* `scenario_dimensions` — relevant positive/negative, misuse, main/alternative/exception, interaction/context, current/desired-state, or other scenario classifications when useful;
* `constraints` — relevant business, technical, security, performance, compatibility, data, or operational constraints;
* `failure_model` — expected failures, partial failures, timeout/retry, duplicate/replay, dependency outage, concurrency, or other reliability assumptions when material;
* `quality_fit_criteria` — observable quality conditions and justified thresholds when supplied;
* `security_obligations` — supported authorization, information, purpose, delegation, organizational, or misuse constraints when supplied;
* `risk_notes` — evidenced risk areas, failure consequences, or verification priorities;
* `known_gaps` — unresolved or intentionally unspecified behavior that must not be silently converted into expected behavior;
* `assumptions` — material assumptions and confirmation state;
* `provenance` — enough source context to distinguish direct evidence, decisions, assumptions, and derived implications.

## Integrity

* This contract carries evidence; it does not replace the authoritative requirement, code, or project source.
* Requirements, decisions, assumptions, known gaps, and unresolved questions must remain distinguishable.
* Testing may consume only the relevant subset.
* Material conflicts with implementation or other project evidence must remain explicit.
* Missing expected behavior must not be invented merely to make a test executable or passing.
* Business examples remain business evidence; the Testing context may automate them but should not rewrite them into implementation-coupled behavior merely for convenience.
* The contract may support BDD or Specification by Example, but it does not require Gherkin or any particular automation framework.
* When a material ambiguity changes what a correct test should assert, request clarification or report the unresolved behavior.
* Testing remains usable when this handoff does not exist.

## Portability

The contract defines meaning rather than a required serialization format.
