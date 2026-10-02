# Build Backlog

## Intent

Create a structured, traceable backlog from sufficiently defined requirements and other explicit work sources.

## Invocation

This command selects the Backlog Planner and the `build` mode of the backlog-planning skill. It does not authorize requirement changes, architecture selection, implementation, or repository mutation.

## Uses

* Rule: `contexts/requirements/rules/tailoring.md`

* Agent: `contexts/requirements/agents/backlog-planner.md`
* Skill: `contexts/requirements/skills/backlog-planning/skill.md`
* Mode: `build`
* Rule: `contexts/requirements/rules/backlog.md`
* Contract: `contracts/work-item.md`

## Inputs

* Requirement specifications and other explicit work sources.
* Existing tracker hierarchy, item taxonomy, or backlog conventions when available.
* Intended planning horizon.
* Optional use-case/journey context, examples, learning objectives, and critical guarantees when available.

## Output

Traceable work items with coherent intent, acceptance evidence, dependencies, risks, assumptions, blockers, readiness, and closure findings.

## Boundary

If decomposition would require inventing or changing source semantics, return the issue to requirements clarification rather than creating speculative scope.
