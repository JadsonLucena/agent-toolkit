# Requirements Contract

## Purpose

Define the neutral semantic handoff produced by requirements definition and consumed by planning, design, implementation, review, or testing contexts. This is a schema contract, not a workflow, rule, skill, command, or agent.

## Context Semantics

A requirement specification should make the surrounding change or initiative context reconstructable when known:

* `context_id` — stable identity for the initiative, change context, or requirements scope;
* `sources` — source references and concise provenance;
* `decisions` — explicit stakeholder or developer decisions that govern the specification;
* `assumptions` — material assumptions, including whether they are confirmed or unresolved;
* `open_questions` — unresolved questions whose answers may change semantics or scope;
* `conflicts` — unresolved contradictions between sources, requirements, rules, or decisions;
* `status` — semantic state such as `sufficient`, `needs-revision`, `needs-clarification`, or `blocked`;
* `readiness_for` — optional downstream target for which the status was evaluated, such as backlog planning or design.

Do not encode the downstream target into `status`, and do not use numeric confidence scores as a substitute for evidence.

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
* Newer evidence supersedes older evidence only when that relationship is explicit and provenance is retained.
* Downstream consumers may select a relevant subset but must preserve requirement identity and semantics.
* A material semantic change creates a requirements concern and must not be hidden as a downstream transformation.
* When requirement semantics change, consumers should be able to identify downstream artifacts that require re-evaluation.

## Portability

The contract defines meaning, not serialization. A platform adapter may represent it in another format as long as these semantics are preserved.
