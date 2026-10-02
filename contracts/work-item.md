# Work Item Contract

## Purpose

Define the neutral semantic handoff for a planning item derived from requirements, defects, risks, decisions, or other explicit work sources. This contract does not impose an issue tracker or delivery framework.

## Context Semantics

Planning handoffs should preserve the surrounding change context when known:

* `context_id` — stable identity for the initiative, change context, or planning scope;
* `sources` — requirements, defects, risks, decisions, or other evidence that justify the work;
* `decisions` — explicit decisions that constrain decomposition or sequencing;
* `assumptions` — material assumptions and confirmation state;
* `open_questions` — unresolved questions that may change item semantics or readiness;
* `conflicts` — unresolved contradictions relevant to the work;
* `status` — semantic state such as `sufficient`, `needs-revision`, `needs-clarification`, or `blocked`;
* `readiness_for` — optional planning horizon or downstream target against which readiness was assessed.

## Required Semantics

A work item should make the following available when material and known:

* stable item identity within its planning scope;
* coherent work intent;
* source references and requirement traceability;
* relevant acceptance evidence;
* dependencies and sequencing constraints;
* risks and blockers;
* explicit assumptions and unresolved questions;
* readiness state for the intended planning horizon.

Optional project-specific fields may include priority, estimate, owner, iteration, deadline, labels, or implementation notes only when supported by the surrounding process.

## Integrity

* Work-item semantics must not silently expand or reinterpret source requirements.
* Missing priority, estimate, owner, or schedule information remains unspecified.
* One requirement may map to multiple items and one item may trace to multiple related requirements.
* Technical or enabling work must retain an evidenced outcome, requirement, constraint, dependency, or risk that justifies it.
* Material semantic ambiguity must be returned to the requirements source rather than resolved by planning invention.
* Source obligations with no work item must remain explicitly accounted for when they are deferred, rejected, external, out of scope, or intentionally unplanned.
* Work items with no evidenced source or purpose are traceability findings, not automatically valid scope.

## Portability

The contract defines meaning, not serialization. Platform adapters may map it to issue fields, Markdown, YAML, JSON, or another representation without changing the semantics.
