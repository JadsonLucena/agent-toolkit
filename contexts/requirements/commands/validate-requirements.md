# Validate Requirements

## Intent

Evaluate requirement quality and readiness for the requested downstream use.

## Invocation

This command selects the Requirements Specifier and validation workflow. It authorizes analysis and evidence-backed revision recommendations only; it does not authorize modifying the specification.

## Uses

* Rule: `contexts/requirements/rules/tailoring.md`

* Agent: `contexts/requirements/agents/requirements-specifier.md`
* Skill: `contexts/requirements/skills/validation/SKILL.md`
* Rule: `contexts/requirements/rules/requirements.md`
* Contract: `contracts/requirements.md`

## Inputs

* Requirement specification.
* Supporting evidence and decisions.
* Intended readiness target.
* Change Boundary and supporting scope decisions when one governs the specification.

## Output

Rigor assessment when material, validation findings with type and severity, Change Boundary/scope-drift findings when applicable, cross-artifact consistency findings, missing knowledge, evidence-backed revision recommendations, unresolved questions, and a readiness state tied to an explicit downstream target.

## Boundary

Material ambiguity, gaps, or conflicts requiring stakeholder or developer authority must be surfaced rather than silently resolved. Applying a recommended revision requires separate explicit authorization.
