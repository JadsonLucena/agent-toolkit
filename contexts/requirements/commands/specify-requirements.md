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
* Existing requirement identifiers, decisions, assumptions, and constraints when present.

## Output

Requirement definitions conforming to `contracts/requirements.md`, including acceptance evidence, traceability, assumptions, conflicts, and unresolved questions.

## Boundary

If material requirement semantics cannot be established from evidence, return the clarification need rather than inventing values, thresholds, actors, or behavior.
