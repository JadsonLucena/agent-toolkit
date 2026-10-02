# Validate Requirements

## Intent

Evaluate requirement quality and readiness for the requested downstream use.

## Invocation

This command selects the Requirements Specifier and validation workflow. It authorizes evidence-backed validation and correction of specification defects that do not require inventing stakeholder intent.

## Uses

* Agent: `contexts/requirements/agents/requirements-specifier.md`
* Skill: `contexts/requirements/skills/validation/skill.md`
* Rule: `contexts/requirements/rules/requirements.md`
* Contract: `contracts/requirements.md`

## Inputs

* Requirement specification.
* Supporting evidence and decisions.
* Intended readiness target.

## Output

Validation findings, affected identifiers, evidence, unresolved questions, and an evidence-backed readiness state.

## Boundary

Material ambiguity, gaps, or conflicts requiring stakeholder or developer authority must be surfaced rather than silently resolved.
