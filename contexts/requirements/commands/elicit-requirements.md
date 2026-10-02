# Elicit Requirements

## Intent

Discover and structure stakeholder needs, outcomes, constraints, rules, evidence, and unresolved questions before formal specification.

## Invocation

This command is an engineering-intent entry point. It selects the Requirements Elicitor and elicitation workflow; it does not authorize specification, backlog decomposition, implementation, or repository mutation.

## Uses

* Agent: `contexts/requirements/agents/requirements-elicitor.md`
* Skill: `contexts/requirements/skills/elicitation/skill.md`
* Rule: `contexts/requirements/rules/requirements.md`
* Contract: `contracts/requirements.md`

## Inputs

* Available stakeholder or project context.
* Existing evidence and source material.
* The requested problem, initiative, or scope.

## Output

A requirements elicitation handoff conforming to the elicitation semantics in `contracts/requirements.md`.

## Boundary

If required evidence is materially ambiguous or insufficient, return the clarification need rather than inventing stakeholder intent.
