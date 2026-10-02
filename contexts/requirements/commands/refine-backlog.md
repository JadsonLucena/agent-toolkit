# Refine Backlog

## Intent

Refine an existing backlog while preserving requirement semantics and traceability.

## Invocation

This command is an engineering-intent entry point. It selects the responsible specialist and workflow; it does not duplicate their procedure.

## Uses

* Agent: `contexts/requirements/agents/backlog-planner.md`
* Skill: `contexts/requirements/skills/build-backlog.md`
* Mode: `refine`

## Inputs

* Existing backlog.
* Current specified requirements and decisions.
* Tracker conventions when available.

## Output

A refined backlog plus surfaced traceability, ambiguity, and readiness findings.

## Boundary

If required evidence is materially ambiguous or insufficient, return the clarification need rather than inventing intent.
