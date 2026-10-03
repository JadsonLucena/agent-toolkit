# Shape Change

## Intent

Shape a feature, defect, correction, migration, regulatory change, operational improvement, or other change through the minimum Requirements work needed to reach a validated planning handoff.

## Invocation

This is an optional composite Requirements entry point. It conditionally routes the existing elicitation, definition, read-only validation, and backlog-planning capabilities according to the evidence already available.

Invocation does not authorize architecture selection, implementation, automated-test generation, repository mutation, or Git operations.

## Uses

* Rule: `contexts/requirements/rules/tailoring.md`
* Rule: `contexts/requirements/rules/requirements.md`
* Rule: `contexts/requirements/rules/backlog.md`
* Agent: `contexts/requirements/agents/requirements-elicitor.md`
* Agent: `contexts/requirements/agents/requirements-specifier.md`
* Agent: `contexts/requirements/agents/backlog-planner.md`
* Skill: `contexts/requirements/skills/elicitation/skill.md`
* Skill: `contexts/requirements/skills/definition/skill.md`
* Skill: `contexts/requirements/skills/validation/skill.md`
* Skill: `contexts/requirements/skills/backlog-planning/skill.md`
* Contract: `contracts/requirements.md`
* Contract: `contracts/work-item.md`

## Inputs

* The requested change or problem context.
* Available stakeholder, product, domain, project, or existing-system evidence.
* Existing elicitation or requirement artifacts when present.
* Existing backlog when refinement rather than initial planning is intended.
* Intended planning horizon when known.
* Optional known security, privacy, compliance, migration, financial, or assurance constraints.

## Routing

1. Inspect supplied evidence and determine the earliest Requirements capability that is still necessary; do not repeat work merely because this command spans the full path.
2. If material stakeholder intent, Need/Goal context, scope, business knowledge, or uncertainty is not sufficiently understood, route through Requirements Elicitation.
3. When evidence is sufficient for formal semantics, route through Requirements Definition.
4. Run Requirements Validation as a separate read-only pass before claiming readiness for planning.
5. Route `needs-clarification` findings back to the capability that owns the missing stakeholder/domain knowledge and route evidence-backed `needs-revision` findings back to Requirements Definition; do not repair the specification silently under validation authority.
6. When requirements are sufficient for the intended planning horizon, route to Backlog Planning:
   * use `build` when no planning representation exists;
   * use `refine` when an existing backlog was supplied and only planning refinement is authorized.
7. Preserve identifiers, provenance, decisions, assumptions, unknowns, business rules, scenarios, critical guarantees, and unresolved issues across each handoff.
8. Stop only the affected path when material evidence or authority is missing. Preserve independently valid knowledge rather than restarting the entire workflow.

## Output

Return the smallest useful set of outputs actually produced by the routed capabilities, which may include:

* elicitation evidence conforming to `contracts/requirements.md`;
* requirement specification and read-only validation findings;
* readiness state for the intended planning horizon;
* `contracts/work-item.md`-compatible backlog items or refinements;
* unresolved questions, assumptions, options, conflicts, blockers, and recommended next evidence.

Do not manufacture empty intermediate artifacts merely to demonstrate that every stage was visited.

## Boundary

This command composes existing Requirements capabilities; it does not redefine their semantics.

It must not:

* invent stakeholder intent to keep the pipeline moving;
* bypass a material validation finding;
* silently change requirement semantics during planning;
* select architecture or implementation;
* generate or repair production code;
* create automated tests;
* mutate a repository or perform Git operations.

A downstream mutation requires its own explicit command or separate authorization.
