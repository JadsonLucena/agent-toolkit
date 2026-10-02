# Work Item Contract

## Purpose

Define the neutral semantic handoff for a planning item derived from requirements, defects, risks, decisions, or other explicit work sources. This contract does not impose an issue tracker or delivery framework.

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
* Material semantic ambiguity must be returned to the requirements source rather than resolved by planning invention.

## Portability

The contract defines meaning, not serialization. Platform adapters may map it to issue fields, Markdown, YAML, JSON, or another representation without changing the semantics.
