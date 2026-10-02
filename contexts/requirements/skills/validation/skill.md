# Requirements Validation

## Purpose

Use as an independent quality gate for requirement definitions before downstream planning or implementation.

## Uses

* Rule: `contexts/requirements/rules/requirements.md`
* Contract: `contracts/requirement-specification.md`

## Workflow

1. Identify the specification scope, intended downstream use, sources, and unresolved questions.
2. Check each material requirement for evidence, clarity, consistency, verifiability, traceability, and sufficient completeness.
3. Check acceptance criteria for observable evidence and semantic alignment with their source requirement.
4. Check business rules, constraints, assumptions, dependencies, states, invariants, and non-functional requirements for contradictions or unsupported precision.
5. Distinguish specification defects from unresolved stakeholder intent.
6. Classify the result as:
   * `sufficient` — no material issue blocks the intended downstream use;
   * `needs-revision` — the specification can be corrected from existing evidence;
   * `needs-clarification` — stakeholder or developer input is required;
   * `blocked` — required evidence is unavailable.
7. Report findings with traceable references to the affected requirement or source. Do not rewrite stakeholder intent merely to make validation pass.

## Output

Produce a concise validation report with status, material findings, affected identifiers, unresolved questions, and the evidence required to resolve them.
