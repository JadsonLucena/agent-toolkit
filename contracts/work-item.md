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
* readiness state for the intended planning horizon;
* parent goal, use-case, journey, requirement, scenario, or other semantic context when one exists;
* `scenario_refs` when the work item realizes or changes explicitly modeled behavioral scenarios;
* slice intent and observable outcome when the item represents an incremental slice;
* learning objective when the item intentionally exists to reduce uncertainty;
* critical guarantees or invariants that the slice must preserve.

Optional project-specific fields may include priority, estimate, owner, iteration, deadline, labels, or implementation notes only when supported by the surrounding process.

## Integrity

* Work-item semantics must not silently expand or reinterpret source requirements.
* Missing priority, estimate, owner, or schedule information remains unspecified.
* One requirement may map to multiple items and one item may trace to multiple related requirements.
* Technical or enabling work must retain an evidenced outcome, requirement, constraint, dependency, risk, or learning objective that justifies it.
* A technical task should normally remain subordinate to a coherent slice or work item when it is only one implementation step of that outcome.
* Incremental slicing must not remove critical financial, security, privacy, compliance, integrity, deduplication, or minimum-observability guarantees that are required from the first usable increment.
* A use-case or actor goal should remain semantically whole even when delivery is split across slices.
* Stable scenario identifiers referenced by planning items must be preserved rather than replaced with tracker-specific item identifiers.
* Material semantic ambiguity must be returned to the requirements source rather than resolved by planning invention.
* Source obligations with no work item must remain explicitly accounted for when they are deferred, rejected, external, out of scope, or intentionally unplanned.
* Work items with no evidenced source or purpose are traceability findings, not automatically valid scope.
* Candidates for deferment, trimming, experimentation, or removal must remain recommendations unless an authorized decision establishes their disposition.

## Portability

The contract defines meaning, not serialization. Platform adapters may map it to issue fields, Markdown, YAML, JSON, or another representation without changing the semantics.
