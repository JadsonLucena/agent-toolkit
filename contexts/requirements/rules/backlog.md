# Backlog Rules

## Core Principles

* A backlog is a planning view of work derived from supported needs, requirements, defects, risks, decisions, or other explicit work sources.
* Backlog decomposition must preserve source intent. Do not introduce new requirements merely to make an item appear implementation-ready.
* Keep backlog structure process-neutral unless the project explicitly adopts a specific delivery framework.
* When a target planning system has an established hierarchy, item taxonomy, or required metadata, preserve those conventions unless they conflict with semantic integrity.
* Every material work item should have a coherent purpose and enough context for its intended planning horizon.

## Source Integrity and Traceability

* Trace work items to the requirements, needs, defects, risks, decisions, or other evidence that justify them.
* Preserve requirement identifiers and acceptance semantics when they exist.
* Treat requirement and work-item identities as different: one requirement may map to multiple work items, and one coherent work item may satisfy multiple related requirements.
* When a work item reveals unsupported behavior or materially changes source intent, return the issue for requirements clarification rather than silently expanding scope.

## Decomposition

* Decompose by coherent deliverable intent, behavior, risk, dependency, or independently valuable outcome rather than by arbitrary file, layer, or organizational boundary.
* Keep coupled work together when separation would create an invalid, misleading, unverifiable, or operationally unsafe intermediate state.
* Split work when independent intents, acceptance conditions, risks, dependencies, or delivery paths can be reasoned about separately.
* Avoid premature decomposition beyond the level needed for the current planning horizon.
* Technical or enabling tasks may exist when they represent necessary work, but they must trace to the outcome, requirement, constraint, dependency, or risk that justifies them.
* Do not manufacture implementation tasks when the solution has not been selected and the task would encode an unsupported design decision.

## Acceptance and Readiness

* Preserve relevant acceptance criteria from source requirements.
* Add planning-specific completion conditions only when they do not alter stakeholder intent.
* Keep material unknowns, assumptions, dependencies, risks, and blockers visible.
* Do not label an item ready when a material ambiguity prevents reliable implementation or verification.
* Missing implementation detail is not automatically a blocker when source semantics are clear and design or implementation can legitimately decide the detail later.
* Readiness is contextual; do not impose a universal Definition of Ready.

## Dependencies and Ordering

* Represent dependencies when one item requires another artifact, decision, capability, migration, interface, or state before it can be completed safely.
* Distinguish hard dependencies from preferred sequencing.
* Do not invent priority from item order alone.
* Preserve explicit stakeholder or project priority when provided; otherwise report priority as unspecified.
* Surface dependency cycles and conflicting ordering constraints instead of silently choosing an order.

## Refinement

* Refinement may improve clarity, decomposition, traceability, dependencies, risks, and acceptance evidence without changing underlying requirement semantics.
* A semantic scope change requires requirements evidence or an explicit decision; it is not merely backlog refinement.
* Preserve history or rationale for material planning changes when the surrounding system supports it.

## Planning Closure

* Account for every material source requirement, defect, risk, decision, or obligation that entered the planning scope.
* Identify source items with no planned realization and classify them explicitly when they are deferred, rejected, external, out of scope, or otherwise intentionally unplanned.
* Identify work items with no evidenced source or purpose; do not retain orphan work merely because it already exists.
* Check for duplicated scope, hidden scope expansion, inconsistent acceptance semantics, and unresolved dependency cycles before treating the backlog as current.
* A closed traceability loop does not require every source to become a work item, but every material omission must be explainable.

## Quality Guardrails

* Do not use estimates, priorities, owners, iteration assignments, or deadlines unless requested, supported by project policy, or supplied as evidence.
* Do not force every item into a user-story template.
* Do not equate small size with readiness or value.
* Do not duplicate the same obligation across multiple items without an explicit coordination reason.
* Do not hide unresolved requirement questions inside implementation notes.
* Do not impose a specific issue tracker, agile framework, or vendor schema.
