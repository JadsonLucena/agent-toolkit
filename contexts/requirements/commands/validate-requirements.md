# Validate Requirements

## Intent

Evaluate requirement quality and readiness for the requested downstream stage.

## Invocation

This command is an engineering-intent entry point. It selects the responsible specialist and workflow; it does not duplicate their procedure.

## Uses

* Agent: `contexts/requirements/agents/requirements-specifier.md`
* Skill: `contexts/requirements/skills/validate-requirements.md`

## Inputs

* Requirement set or specification.
* Intended readiness target.

## Output

Validation findings and an evidence-backed readiness state.

## Boundary

If required evidence is materially ambiguous or insufficient, return the clarification need rather than inventing intent.
