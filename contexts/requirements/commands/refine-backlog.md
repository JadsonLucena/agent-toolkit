# Refine Backlog

## Intent

Refine an existing backlog while preserving requirement semantics and traceability.

## Invocation

This command selects the Backlog Planner and the `refine` mode of the backlog-planning skill. It authorizes planning refinement, not silent requirement change or unsupported scope expansion.

## Uses

* Rule: `contexts/requirements/rules/tailoring.md`

* Agent: `contexts/requirements/agents/backlog-planner.md`
* Skill: `contexts/requirements/skills/backlog-planning/skill.md`
* Mode: `refine`
* Rule: `contexts/requirements/rules/backlog.md`
* Contract: `contracts/work-item.md`

## Inputs

* Existing backlog.
* Current requirements, decisions, and source evidence.
* Existing tracker hierarchy, item taxonomy, or backlog conventions when available.
* Intended planning horizon.
* Optional use-case/journey context, examples, learning objectives, and critical guarantees when available.

## Output

Refined work items plus surfaced traceability, dependency, ambiguity, closure, and readiness findings.

## Boundary

A material semantic scope change is a requirements concern and must not be hidden as backlog refinement.
