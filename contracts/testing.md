# Testing Contract

## Purpose

Define optional behavioral evidence shared with the Testing context without requiring a dependency on Requirements workflows.

## Semantics

The handoff may include source requirement identifiers, observable outcomes, acceptance criteria, business rules, invariants, states, boundaries, failure conditions, relevant quality requirements, risks, assumptions, unresolved questions, and provenance.

## Integrity

* This contract carries evidence; it does not replace the authoritative requirement source.
* Requirements, assumptions, and unresolved questions must remain distinguishable.
* Testing may consume only the relevant subset.
* Material conflicts with implementation or other project evidence must remain explicit.
* Testing remains usable when this handoff does not exist.

## Portability

The contract defines meaning rather than a required serialization format.
