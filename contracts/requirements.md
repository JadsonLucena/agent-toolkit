# Requirements Contract

## Purpose

Define the neutral semantic handoff produced by requirements definition and consumed by planning, design, implementation, review, or testing contexts. This is a schema contract, not a workflow, rule, skill, command, or agent.

## Required Semantics

A requirement specification must make the following available when material and known:

* scope and objective;
* source evidence and provenance;
* stable requirement identifiers within the specification scope;
* requirement statements;
* acceptance criteria or other verification evidence;
* business rules and invariants;
* functional and non-functional constraints;
* interfaces, data constraints, states, or transitions when relevant;
* dependencies and conflicts;
* explicit assumptions;
* unresolved questions and blocked decisions;
* traceability relationships.

## Integrity

* Unknown information remains unknown; absence must not be converted into fabricated values.
* Derived information must be distinguishable from directly stated source evidence.
* Downstream consumers may select a relevant subset but must preserve requirement identity and semantics.
* A material semantic change creates a requirements concern and must not be hidden as a downstream transformation.

## Portability

The contract defines meaning, not serialization. A platform adapter may represent it in another format as long as these semantics are preserved.
