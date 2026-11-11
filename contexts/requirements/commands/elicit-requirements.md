# Elicit Requirements

## Intent

Discover and structure the knowledge needed to understand a change, with requirements rigor proportional to risk and uncertainty, before formal specification.

## Invocation

This command is an engineering-intent entry point. It selects the Requirements Elicitor and elicitation workflow; it does not authorize specification, backlog decomposition, implementation, or repository mutation.

## Uses

* Rule: `contexts/requirements/rules/tailoring.md`

* Agent: `contexts/requirements/agents/requirements-elicitor.md`
* Skill: `contexts/requirements/skills/elicitation/SKILL.md`
* Rule: `contexts/requirements/rules/requirements.md`
* Contract: `contracts/requirements.md`

## Inputs

* Available stakeholder or project context.
* Existing evidence and source material.
* The requested problem, initiative, or scope.
* Existing Change Boundary or scope decisions when present.
* Applicable local requirements template/schema/notation when known.
* Optional known risk, compliance, security, migration, or assurance constraints.

## Output

A requirements elicitation handoff conforming to `contracts/requirements.md`, including the Change Boundary, material scope discoveries, intended next-decision knowledge batch, lifecycle claim, and local representation convention when applicable.

## Boundary

If required evidence is materially ambiguous or insufficient, return the clarification need rather than inventing stakeholder intent.
