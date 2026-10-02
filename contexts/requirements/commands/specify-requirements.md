# Specify Requirements

## Intent

Convert evidenced requirements material into precise, traceable, verifiable specification records.

## Invocation

This command is an engineering-intent entry point. It selects the responsible specialist and workflow; it does not duplicate their procedure.

## Uses

* Agent: `contexts/requirements/agents/requirements-specifier.md`
* Skill: `contexts/requirements/skills/specify-requirements.md`

## Inputs

* Elicitation handoff or equivalent authoritative source material.
* Existing requirement identifiers and decisions when present.

## Output

Specified requirement records conforming to `contracts/requirements-workflow.md`.

## Boundary

If required evidence is materially ambiguous or insufficient, return the clarification need rather than inventing intent.
