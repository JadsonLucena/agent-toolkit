# Specify Requirements

## Intent

Convert supported elicitation evidence into precise, traceable, verifiable requirements at the rigor justified by the context.

## Invocation

This command selects the Requirements Specifier and definition workflow. It does not authorize backlog decomposition, design, implementation, or unrelated downstream mutations.

## Uses

* Rule: `contexts/requirements/rules/tailoring.md`

* Agent: `contexts/requirements/agents/requirements-specifier.md`
* Skill: `contexts/requirements/skills/definition/skill.md`
* Rule: `contexts/requirements/rules/requirements.md`
* Contract: `contracts/requirements.md`

## Inputs

* Elicitation handoff or equivalent authoritative source material.
* Existing requirement identifiers, Change Boundary/scope decisions, decisions, assumptions, constraints, and local representation convention when present.

## Output

Requirement definitions conforming to `contracts/requirements.md`, including Change Boundary reconciliation when applicable, acceptance evidence, traceability, assumptions, conflicts, unresolved questions, and an explicit requirements-specified lifecycle claim.

## Boundary

If material requirement semantics or scope cannot be established from evidence, return the clarification/scope-decision need rather than inventing values, thresholds, actors, behavior, or boundary changes.
