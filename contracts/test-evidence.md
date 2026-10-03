# Test Evidence Contract

## Purpose

Define vendor-neutral evidence that relates behavioral scenarios to automated tests and verification results without making the test implementation the authoritative source of business semantics.

This contract complements `contracts/test-basis.md`. The test basis describes what behavior should be verified; test evidence records how that behavior is covered and what verification actually occurred.

## Context Semantics

Test evidence should preserve, when known:

* `context_id` — the initiative or change context shared with upstream artifacts;
* `subject` — the behavior, change, component, defect, slice, or work item being verified;
* `test_basis_ref` — reference to the test basis or equivalent behavioral evidence used;
* `source_refs` — relevant requirement, rule, use-case, scenario, work-item, implementation, or decision references;
* `verification_commands` — commands or procedures actually executed;
* `verification_environment` — material environment or configuration facts when they affect the result;
* `provenance` — enough evidence to distinguish executed verification from assumptions or unverified claims.

## Scenario Coverage

When a Scenario Set exists, record coverage by preserving its stable scenario identity.

Each scenario coverage entry may include:

* `scenario_id` — the exact stable identifier from the Scenario Set;
* `automation_refs` — references to one or more automated test cases, test symbols, files, suites, or platform test identifiers;
* `automation_status` — `automated`, `partially-automated`, `not-automated`, or `blocked`;
* `verification_status` — `passed`, `failed`, `not-run`, or `blocked`;
* `verification_refs` — result, log, build, report, or execution references when available;
* `notes` — concise explanation for partial coverage, deliberate non-automation, or blockers.

One scenario may map to multiple tests, and one test may provide evidence for multiple related scenarios when the relationship is explicit.

## Coverage Findings

When traceability is material, identify:

* scenarios with no automation evidence;
* scenarios with only partial automation;
* automated tests whose intended behavior has no scenario or other supported source reference;
* stale automation references;
* conflicts between expected behavior and observed implementation/test behavior;
* verification that was skipped, blocked, or not executed.

An automated test without a Scenario Set reference is not automatically invalid. It may trace directly to another supported behavior source when no Scenario Set exists.

## Integrity

* Preserve scenario identifiers exactly; Testing must not silently replace upstream scenario identity with framework-specific names.
* Do not mark a scenario covered merely because a test file exists.
* Do not mark verification as passed unless relevant checks were actually executed successfully.
* Keep `automation_status` separate from `verification_status`: a scenario can be automated but not yet run, or automated with failing verification.
* Do not infer business correctness from code coverage percentage.
* Do not convert a test implementation detail into new business semantics.
* When a test exposes an ambiguity or contradiction in the Scenario Set, surface the conflict rather than rewriting the scenario to match the implementation.
* Missing automation may be acceptable when automation is not justified by risk or cost, but the disposition should remain explicit when traceability is required.

## Portability

The contract defines semantic relationships rather than a required test framework, file layout, tag format, report format, or serialization.

Adapters may map `scenario_id` and `automation_refs` to Cucumber tags, test annotations, test-case-management identifiers, code symbols, CI reports, or other platform-specific mechanisms while preserving the canonical identity and relationships.
