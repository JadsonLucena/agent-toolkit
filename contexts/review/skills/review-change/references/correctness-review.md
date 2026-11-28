# Behavioral Correctness — Conditional Investigation Reference

This is a **read-only falsification aid** for changes with meaningful functional
behavior or regression risk. It does not impose formal verification, a new gate,
a universal checklist, or any additional authority over Requirements. In a
native-solo review, the Lead applies the same relevant probes; with a team, the
Correctness Reviewer owns this investigation lens.

## Investigate the Behavior, Not a Pattern Name

For each *material, reachable* behavioral change:

1. **Establish the obligation.** Identify accepted requirements, business rules,
   interface contracts, documented invariants or project conventions with their
   source and revision. Inspect prior behavior to detect regressions, but do not
   silently elevate a previous implementation, PR claim, test expectation or
   preference into approved business policy. Where intent is material and
   unresolved, report source ambiguity through existing review dispositions.
2. **Trace an actual path.** Start at a changed entry point, then inspect its
   inputs, relevant guards, control/data flow, state mutations, output/error
   semantics, side effects and affected callers or consumers. Keep the examined
   base/head or workspace snapshot fixed.
3. **Try to falsify the guarantee.** Construct a minimal input, branch
   combination, transition sequence or execution ordering that might produce
   a prohibited outcome. Favor the relevant probes below, not all probes.
4. **Seek disconfirmation.** Inspect called code, constraints and tests that
   might prevent the alleged outcome. A hypothetical path is not reachable merely
   because one line appears dangerous. Record unknown dependencies explicitly.
5. **Explain expected versus actual.** State the governing obligation, concrete
   trigger, source-grounded expected result, observed or statically derived
   result, impact, contrary evidence and verification limits. Reuse the existing
   specialist handoff fields and finding statuses; never certify passing checks
   that were not actually executed.

## Risk-Selected Functional Probes

| Mechanism | Falsification question | Useful witness |
| --- | --- | --- |
| Boolean decisions and guards | Does precedence, short-circuiting, negation or a combined condition admit a forbidden branch? | Decision table with discriminating true/false combinations; MC/DC only when justified |
| Boundary and cardinality | Do inclusive/exclusive comparisons satisfy the stated interval, limit or count? | Just below / exactly at / just above each contractual boundary |
| Null, absent and empty values | Are missing, null, zero, false and empty values distinguishable where the contract requires it? | Paired inputs that differ only in presence or emptiness |
| Data flow and transformation | Is the value consumed the intended value after mapping, conversion, aliasing or overwrite? | Input-to-output trace through changed producer and consumer |
| Numeric correctness | Can rounding order, precision, integer division, overflow or units change a required result? | A value at the smallest observable numerical difference |
| Loops and progress | Can a changed condition skip, duplicate or never process an item under valid inputs? | Empty, singleton and final iteration; termination/progress argument when material |
| State and sequence | Can a transition bypass an essential guard or violate an invariant across multiple calls? | Starting state, event sequence, final state and invariant |
| Time and intervals | Does a window change its inclusive endpoints, timezone assumptions or event ordering? | Exact boundary timestamp or out-of-order event, with explicit time basis |
| Error and side effects | Does a negative path now return success, corrupt state or leak an unintended effect? | Reachable failure and resulting observable state |
| Behavioral preservation | Does a purported refactor change output, errors, side effects or state for a supported input? | Paired base/head behavior for the same input |

### Examples and controls

- **Defect, if the accepted limit is two previous refunds:** a guard
  `refund_count <= 2` allows one more refund when the count is exactly two;
  show the reachable request path and expected rejection.
- **Not a defect if the accepted maximum is inclusive:** `amount <= 100`
  correctly accepts 100. A generic preference for `<` is not evidence.
- **Unresolved, not confirmed:** if the contractual meaning of an empty
  display name is unknown, a change from `is None` to a truthiness check may
  be a regression worth investigation, but not an invented business rule.
- **Not proof:** a green test that copies the implementation's expectation,
  line coverage, or a model's agreement alone does not establish correctness.

## Lens Boundaries and Handoff

- Ask **Specification** to establish disputed requirement authority or
  compatibility obligations; do not redefine the accepted contract.
- Ask **Reliability** to probe concurrent interleavings, transaction isolation,
  retries, deduplication and crash/recovery windows. Correctness may supply the
  violating state or outcome without duplicating the failure-mechanism audit.
- Ask **Testing** whether real assertions, test oracles and fresh check evidence
  can detect the specific counterexample; do not create/modify tests in Review.
- For material refactors, reuse `references/refactoring-review.md`; for
  external effects and state risks, reuse
  `contexts/review/rules/high-risk-patterns.md`. Neither is a second gate.
- Preserve one source-backed candidate per demonstrated defect mechanism;
  deduplicate shared causes through the existing verifier and Lead. Return
  source scope, contrary evidence and material uncertainties even without a
  finding. The Code Review Lead alone issues PASS/FAIL/INCOMPLETE.

Foundations: Hoare (pre/postconditions), Meyer (contracts and invariants),
Myers (boundary/negative testing), Dijkstra (limits of test evidence), and
Feathers (behavioral characterization). These motivate investigation, not
mandatory formal proofs or universal technique requirements.
