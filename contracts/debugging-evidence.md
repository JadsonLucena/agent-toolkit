# Debugging Evidence Contract

## Purpose

Portable, vendor-neutral handoff of a bounded technical causal investigation. This contract conveys evidence and uncertainty, not a mandatory report file, automatic gate, remediation approval or Review verdict.

## Identity and Evidence

Record proportionately, when material:

* `investigation_id`: locally stable investigation identity when traceability is necessary; never invent external tracker IDs.
* `subject`: reported and/or inspected symptom, actual behavior, authoritative or disputed expectation source, and impact provenance.
* `source_identity`: repository/commit SHA or workspace fingerprint, relevant runtime/version/configuration, environment and time window; identify missing, uninspected and excluded sources.
* `reproduction`: `reproduced`, `intermittent`, `not-reproduced`, `not-attempted` or `unavailable`, with observed attempts, inputs and conditions. Lack of reproduction is not disproof.
* `observations`: concrete code paths, bounded logs/traces, versions, comparisons and actually executed checks, referenced with provenance and outcome. Do not include private logs when a redacted reference suffices.
* `hypotheses`: mechanism, disconfirming prediction, supporting and contradictory evidence, confounders and `supported`, `refuted` or `unresolved` disposition.
* `experiments`: distinguish executed checks and results from proposed/not-run checks; record safety/authorization and actual scope.
* `causal_assessment`: defect/mechanism, triggers, contributing conditions, causal chain and limits. Correlation alone is not proof.
* `diagnosis_status`: `confirmed`, `probable`, `inconclusive` or `blocked`. Confirmed applies only to the evidenced causal scope; blocked specifies missing authority/evidence. Status is not severity or a Review PASS/FAIL.
* `confidence`: optional `high`, `medium` or `low` support strength, distinct from risk, likelihood and impact.
* `next_owner` and `recommended_next_action`: separate diagnosis from authorized work. Implementation owns correction, Requirements owns semantics, Design owns architecture, Testing owns test work, Review owns independent verdict, Delivery/operations owns incident mitigation.
* `open_questions`, `missing_evidence`, `limitations` and stable references to requirements/scenarios/tests/review findings where available.

## Consumption and Freshness

Consumers recheck material source and runtime identity before reuse, preserve counterevidence, and distinguish proposed work from executed outcomes. Debugging evidence can support a Review finding only after the Review owner independently verifies its relevance to the frozen target; Review retains its sole verdict in `contracts/review-evidence.md`. No diagnosis authorizes mutations or changes accepted semantics. Lightweight inline findings are valid; persistent artifacts are optional.
