# Build Backlog

## Intent

Create a structured, traceable delivery backlog from sufficiently specified requirements.

## Invocation

This command is an engineering-intent entry point. It selects the responsible specialist and workflow; it does not duplicate their procedure.

## Uses

* Agent: `contexts/requirements/agents/backlog-planner.md`
* Skill: `contexts/requirements/skills/build-backlog.md`
* Mode: `build`

## Inputs

* Specified requirements.
* Existing tracker hierarchy or backlog conventions when available.

## Output

Structured backlog records conforming to `contracts/requirements-workflow.md`.

## Boundary

If required evidence is materially ambiguous or insufficient, return the clarification need rather than inventing intent.
