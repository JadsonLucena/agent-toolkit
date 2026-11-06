# Verify Review Findings

## Purpose

Independently investigate candidate code-review findings and produce traceable, evidence-backed classifications without discarding genuine defects or converting speculation into blockers.

## Uses

* Rule: `contexts/review/rules/code-review.md`
* Output contract: `contracts/review-evidence.md`

## Working State

Preserve each raw candidate's identity and source; inspected file and code location; alleged trigger and consequence; confirming and contradicting evidence; verification status; severity; confidence; deduplication mapping; and remediation disposition.

## Workflow

1. **Normalize without loss.** Assign each raw finding an identifier and preserve its originating reviewer, location, allegation, and relevant evidence. Do not merge similar comments before investigating the specific root cause.
2. **Attempt falsification.** Read beyond the changed hunk, follow relevant caller/callee or guards, and identify the concrete runtime/input/state condition required for the alleged behavior. Check whether the source file and location contain the claimed code and whether nearby or cross-file checks contradict the claim. Treat an author's PR description as an assertion to verify, not proof.
3. **Check test implications.** For a claimed verification gap, inspect the actual assertions and test execution path. Name a realistic regression that could escape. Test file existence or coverage percentage is not proof of test adequacy.
4. **Classify truth separately from impact.** Mark each candidate `confirmed` when supported by directly checked evidence, `supported` when plausible and grounded but not conclusively demonstrated, `unverified` when decisive evidence is unavailable, or `refuted` when contradictory evidence disproves the claim. Preserve refuted claims with reasons.
5. **Assess consequences.** Classify `critical`, `high`, `medium`, or `low` based on realistic impact, then assign qualitative confidence (`high`, `medium`, `low`). Priority may also consider exposure and urgency, without changing severity. A high-impact uncertain claim remains open for investigation.
6. **Deduplicate by cause.** After verification, group findings only when they share a demonstrated cause. Preserve raw IDs and originating reviewers; separate independent defects even if found at the same line.
7. **Decide disposition.** Select `fix` for an actionable defect, `investigate` when evidence is missing, `decision-needed` when a material design/business choice is ambiguous, or `defer` for explicitly identified pre-existing debt consistent with local policy. Never silently defer a defect introduced by the reviewed change.
8. **Return evidence.** For each surviving issue report file/line or scoped location, triggering condition, code/test evidence, consequence, practical remediation, verification state, severity, confidence, and open questions. Report reasons for all discarded/refuted findings.

## Output

A normalized, traceable finding set under `contracts/review-evidence.md`, including raw-finding mappings, rejected reasons, unresolved concerns, and whether further verification is required.

## Boundaries

* Independent, read-only analysis; do not change code or tests, accept risk for a stakeholder, publish PR comments, or determine Git readiness.
* A reviewer cannot prove a claim false merely because the relevant code was not inspected. If evidence is insufficient, use `unverified`.
* An external filter or second LLM is optional; the native reviewer must perform the same verification when helpers are absent.

