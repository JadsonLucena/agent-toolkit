# Specification Conformance Investigation

Conditional, read-only investigation reference for the Code Review Lead and
`specification-reviewer`. Use only for obligations applicable to the frozen
change and affected consumers. The owning authority remains
`contexts/review/rules/code-review.md`; no new gate or requirements process.

## 1. Establish the accepted source baseline

* Start with the assigned Change Boundary and supplied requirements, decisions,
  scenarios, quality criteria, interface contracts and source references.
* Within the actual change boundary, discover **relevant** repository-owned,
  versioned requirements, business rules, ADRs, API/event contracts and
  operational guarantees when omitted from the assignment. Do not conduct a
  repository-wide requirements elicitation.
* Identify applicability, source location, revision, effective conditions,
  explicit supersession and unresolved source conflicts. Proposed behavior,
  PR descriptions, tests and implementation are evidence, not automatically
  accepted business authority.
* Preserve unknown authority rather than inferring approval or rejecting every
  change missing a formal Requirements artifact.

## 2. Derive material behavioral obligations

For each relevant authorized requirement or contract, derive only what its
source and necessary logical consequences support:

* trigger, actors, inputs, eligibility and preconditions;
* expected outputs, postconditions and error behavior;
* invariants, permitted/prohibited effects, and affected consumers;
* state transitions, sequencing, time boundaries and concurrency guarantees
  **when contractually relevant**;
* quality attributes with stated measurements, limits and test conditions.

Use stable IDs when supplied; otherwise cite real source locations. Separate
source-stated obligations from derived consequences and still-open decisions.
Do not turn a preferred retry strategy, persistence shape, API maturity level,
test framework or implementation pattern into a requirement.

## 3. Trace both directions

* **Requirement to implementation:** inspect the actual branches, calls,
  state changes and consumers that deliver each obligation; identify omissions.
* **Implementation to authority:** identify material new behavior, external
  effects or changed guarantees without an authorized source; distinguish
  benign unspecified behavior from demonstrably prohibited behavior.
* **Existing contracts:** consider observable compatibility with consumers and
  affected older behavior, without treating every legacy quirk as permanent
  contract. A schema-compatible change may still be semantically incompatible.
* Assess source-backed obligations as `satisfied`, `violated` or `unverified`.
  Passing test names, code coverage and the implementation's own assertions
  do not establish conformance independently.

## 4. Attempt concrete falsification

Select a small number of probes proportional to the obligation and risk:

* boundaries (before/at/after), absence, invalid or forbidden inputs;
* decision-table combinations, alternative use-case paths and exceptions;
* state transitions, interleaving, ordering, retries and duplicate effects
  when the specification depends on them;
* API/event meaning, default values, previously authorized consumers and
  observable side effects.

Try to construct a reachable counterexample with inputs or event sequence,
expected source-backed result, observed implementation path, contradictory
evidence and realistic consequence. Do not assert that a potential corner case
is a defect until a governing obligation and reachable deviation are shown.
Formal specifications and executable property checks are optional techniques,
not universal requirements; never claim an unexecuted check passed.

## 5. Report and collaborate

* Return source-backed candidate findings under the normal Review evidence
  taxonomy, preserving uncertainty and contradictory observations.
* When authoritative sources materially conflict, report `decision-needed`
  with both versions and divergent outcomes; do not choose authority by
  convenience. An inadequate or ambiguous specification is not proof of a
  violating implementation.
* When applicable, include bounded `assessed_obligations` in the portable
  specialist handoff, even without findings. Distinguish verified claims from
  unknown outcomes; the Lead reconciles them into existing
  `specification_conformance` evidence, not a second verdict.
* Request Correctness for implementation paths, Reliability for failure/time
  mechanisms, Security for authorization boundaries and Testing for oracle
  quality only when the concern genuinely requires that expertise.
* Keep the entire investigation read-only and aligned with the frozen target.
