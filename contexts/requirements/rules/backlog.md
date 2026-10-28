# Backlog Rules

Apply `contexts/requirements/rules/tailoring.md` when deciding how much decomposition, traceability, slicing, and planning detail are necessary.

## Core Principles

* A backlog is a planning view of work derived from supported needs, requirements, defects, risks, decisions, learning needs, or other explicit work sources.
* Backlog decomposition must preserve source intent. Do not introduce new requirements merely to make an item appear implementation-ready.
* Keep backlog structure process-neutral unless the project explicitly adopts a specific delivery framework.
* When a target planning system has an established hierarchy, item taxonomy, or required metadata, preserve those conventions unless they conflict with semantic integrity.
* Every material work item should have a coherent purpose and enough context for its intended planning horizon.
* Keep the goal whole; slice delivery rather than inventing artificial mini-goals or technical stories.

## Source Integrity and Traceability

* Trace work items to the requirements, needs, goals, defects, risks, decisions, learning objectives, or other evidence that justify them.
* Preserve requirement identifiers, business rules, critical guarantees, and acceptance semantics when they exist.
* Treat requirement and work-item identities as different: one requirement may map to multiple work items, and one coherent work item may satisfy multiple related requirements.
* When a work item reveals unsupported behavior or materially changes source intent, return the issue for requirements clarification rather than silently expanding scope.
* A task, test, architecture change, or implementation step with no evidenced parent outcome is a traceability finding.

## Decomposition and Vertical Slicing

* Decompose by coherent deliverable intent, observable behavior, learning, risk, dependency, or independently valuable outcome rather than by arbitrary file, layer, component, or organizational boundary.
* Prefer end-to-end slices that are observable, verifiable, coherent, informative, and expandable when the product/domain permits it.
* Keep coupled work together when separation would create an invalid, misleading, unverifiable, or operationally unsafe intermediate state.
* Split work when independent intents, acceptance conditions, risks, dependencies, learning objectives, or delivery paths can be reasoned about separately.
* Avoid premature decomposition beyond the level needed for the current planning horizon.
* Technical or enabling tasks may exist when they represent necessary work, but they should remain subordinate to the coherent outcome, slice, requirement, constraint, dependency, risk, or learning objective that justifies them.
* Do not manufacture implementation tasks when the solution has not been selected and the task would encode an unsupported design decision.

## Use-Case and Journey Slicing

When use cases, journeys, or story maps exist:

* preserve the actor/user goal and narrative context;
* identify the meaningful use-case story, flow, or scenario covered by a slice;
* keep the known behavioral space distinct from the behavior committed to the current release and from behavior already implemented;
* prefer the simplest useful story that can traverse the goal coherently, then add enough stories to make the release sufficient before pursuing the remaining tail;
* do not require all known use-case stories to be fulfilled before a release can be useful;
* avoid splitting a user goal into artificial CRUD or technical-layer stories merely to fit an iteration;
* keep relevant business rules, quality/security constraints, acceptance evidence, and expected tests traceable to the slice.

When Story Mapping is useful:

* preserve the journey or narrative flow horizontally;
* use a backbone to retain the larger activity/task context;
* place details, alternatives, and smaller user tasks beneath the relevant backbone activity;
* distinguish a **User Task** in the story map from an **Engineering Task** used to implement a slice;
* shape release slices as coherent traversals of the experience rather than arbitrary collections of individually high-priority items.

Story Mapping is an optional context-preserving technique, not a mandatory backlog format.

## User Stories

When User Stories are useful, treat them as lightweight units for conversation and planning rather than as complete requirement containers.

Preserve the intent behind **Card, Conversation, Confirmation**:

* the card or item is a reminder of the need;
* conversation establishes shared understanding;
* confirmation identifies observable evidence of satisfaction.

Use INVEST only as a diagnostic heuristic: Independent enough, Negotiable, Valuable, Estimatable, Small, and Testable. Do not assign an INVEST score or turn it into a universal Definition of Ready.

Do not force bugs, spikes, migrations, technical enablers, compliance work, operational work, or Use-Case Slices into a User Story template.

## Learning and Uncertainty

* When uncertainty is the dominant risk, prefer explicit learning work such as an experiment, prototype, probe, spike, or thin real slice over building large speculative scope.
* A learning item must state the uncertainty it reduces and the decision it is intended to inform.
* Do not treat "we do not know yet" as justification for silently selecting an implementation.

## Critical Guarantees During Slicing

Do not remove or defer guarantees that are required for a slice to be valid or safe, including when applicable:

* financial integrity;
* security and privacy;
* compliance;
* fundamental domain invariants;
* no-duplicate or consistency guarantees;
* minimum observability and operability.

A smaller slice is not acceptable if it violates a guarantee that must hold from its first use.

## Acceptance and Readiness

* Preserve relevant acceptance criteria, examples, fit criteria, and critical guarantees from source requirements.
* Add planning-specific completion conditions only when they do not alter stakeholder intent.
* Keep material unknowns, assumptions, dependencies, risks, and blockers visible.
* Do not label an item ready when a material ambiguity prevents reliable implementation or verification.
* Missing implementation detail is not automatically a blocker when source semantics are clear and design or implementation can legitimately decide the detail later.
* Readiness is contextual; do not impose a universal Definition of Ready.

## Dependencies and Ordering

* Represent dependencies when one item requires another artifact, decision, capability, migration, interface, learning result, or state before it can be completed safely.
* Distinguish hard dependencies from preferred sequencing.
* Do not invent priority from item order alone.
* Preserve explicit stakeholder or project priority when provided; otherwise report priority as unspecified.
* Surface dependency cycles and conflicting ordering constraints instead of silently choosing an order.

## Scope Trimming and Disposition

* Identify speculative flexibility, rare variants, unused configurability, or low-value tail work that may be a candidate for deferment or removal.
* Distinguish candidates for now/later/maybe/never when that classification is supported by an authorized product or stakeholder decision.
* Do not discard a requirement or scenario merely because it is rare; preserve mandatory financial, security, privacy, compliance, or invariant-related behavior.
* The planner may recommend trimming or deferral but must not invent the business decision.

## Refinement

* Refinement may improve clarity, decomposition, traceability, dependencies, risks, learning intent, examples, and acceptance evidence without changing underlying requirement semantics.
* A semantic scope change requires requirements evidence or an explicit decision; it is not merely backlog refinement.
* Preserve history or rationale for material planning changes when the surrounding system supports it.

## Planning Closure

* Account for every material source requirement, defect, risk, decision, learning obligation, or other source that entered the planning scope.
* Identify source items with no planned realization and classify them explicitly when they are deferred, rejected, external, out of scope, or otherwise intentionally unplanned.
* Identify work items with no evidenced source or purpose; do not retain orphan work merely because it already exists.
* Check for duplicated scope, hidden scope expansion, inconsistent acceptance semantics, lost critical guarantees, and unresolved dependency cycles before treating the backlog as current.
* A closed traceability loop does not require every source to become a work item, but every material omission must be explainable.

## Quality Guardrails

* Do not use estimates, priorities, owners, iteration assignments, or deadlines unless requested, supported by project policy, or supplied as evidence.
* Do not force every item into a user-story template.
* Do not equate small size with readiness, verticality, or value.
* Do not duplicate the same obligation across multiple items without an explicit coordination reason.
* Do not hide unresolved requirement questions inside implementation notes.
* Do not impose a specific issue tracker, agile framework, story-map notation, or vendor schema.
