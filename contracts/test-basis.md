# Test Basis Contract

This contract defines an optional, vendor-neutral input that requirements, specification, backlog, design, or implementation workflows may provide to testing workflows.

Testing remains independently usable when this contract is absent.

## Fields

A test basis may include:

* `subject` — feature, behavior, change, component, or work item under test.
* `source_refs` — requirement, specification, backlog, decision, defect, or code references.
* `intended_behavior` — supported behavior to verify.
* `acceptance_conditions` — observable conditions of satisfaction.
* `constraints` — relevant business, technical, security, performance, compatibility, or operational constraints.
* `risk_notes` — evidenced risk areas or failure consequences.
* `known_gaps` — unresolved or intentionally unspecified behavior.
* `assumptions` — material assumptions and their confirmation state.

## Consumption Rules

* Treat the test basis as evidence, not as permission to ignore current code or repository conventions.
* Preserve conflicts between the test basis and implementation evidence; surface them instead of silently choosing one.
* Do not invent missing acceptance behavior.
* When a material ambiguity changes what a correct test should assert, request clarification.
