# Requirements Contract

## Purpose

Define the neutral semantic handoff across requirements elicitation and definition and for downstream planning, design, implementation, review, or testing. This is a schema contract, not a workflow, rule, skill, command, or agent.

## Context Semantics

A requirements handoff should make the surrounding change or initiative context reconstructable when known:

* `context_id` — stable identity for the initiative, change context, or requirements scope;
* `sources` — source references and concise provenance;
* `decisions` — explicit stakeholder or developer decisions that govern the specification;
* `assumptions` — material assumptions, including whether they are confirmed or unresolved;
* `open_questions` — unresolved questions whose answers may change semantics or scope;
* `conflicts` — unresolved contradictions between sources, requirements, rules, or decisions;
* `status` — semantic state such as `sufficient`, `needs-revision`, `needs-clarification`, or `blocked`;
* `readiness_for` — optional downstream target for which the status was evaluated, such as backlog planning or design.

Do not encode the downstream target into `status`, and do not use numeric confidence scores as a substitute for evidence.

## Tailoring Semantics

When rigor materially affects the workflow, the handoff may include:

* `rigor` — `lightweight`, `standard`, or `high-assurance`;
* `rigor_rationale` — concise evidence explaining why that level is appropriate;
* `applicable_concerns` — knowledge areas judged relevant for the current context;
* `not_applicable_concerns` — concerns explicitly assessed as not applicable, with rationale when useful;
* `governance` — relevant approval, rule-authority, validation, change-management, or traceability expectations.

Missing documentation is not a valid reason by itself to mark a concern not applicable.

## Strategic and Elicitation Evidence

An elicitation handoff may include, when material and known:

* `need` — problem, opportunity, obligation, or undesirable condition;
* `business_goals` — desired outcomes linked to the need;
* `success_metrics` — outcome/value evidence, distinguished from fit criteria, acceptance criteria, and test assertions;
* `current_state` and `future_state`;
* `change_gaps` — differences between current and future state that justify investigation or change;
* `work_scope` — the broader work to understand or change;
* `product_boundary` — the part, if any, assigned to software/product;
* `stakeholders` and affected actors;
* `business_events` and expected business responses when useful for completeness;
* `candidate_solutions` or learning options when solution uncertainty is material;
* `domain_terms`, facts, and business rules;
* functional needs and quality expectations;
* transition needs for migration, rollout, compatibility, cutover, training, or decommissioning;
* constraints and externally imposed obligations;
* dependencies and risks;
* assumptions, options, conflicts, open questions, and decisions;
* provenance for every material statement.

Elicitation evidence remains distinct from approved specification. Candidate requirements, assumptions, options, and interpretations must not be promoted to accepted requirements merely because they appear in the handoff.

## Requirement Specification Semantics

A requirement specification must make the following available when material and known:

* scope, objective, parent need, goal, source, and rationale;
* stable requirement identifiers within the specification scope;
* requirement statements;
* acceptance criteria, fit criteria, examples, or other verification evidence as appropriate;
* business rules and invariants;
* functional, quality, security, interface, data, operational, and transition constraints when relevant;
* actors, triggers, preconditions, states, transitions, outcomes, guarantees, alternatives, exceptions, or failure behavior when they materially improve understanding;
* data semantics such as ownership, temporal meaning, integrity, lifecycle, lineage, or consumer guarantees when relevant;
* quality context, metric/observable property, justified thresholds, failure assumptions, and trade-offs when relevant;
* security actors, information, operations, purposes, delegations, obligations, and misuse concerns when relevant;
* dependencies and conflicts;
* explicit assumptions, unknowns, and options;
* unresolved questions and blocked decisions;
* traceability relationships.

## Rule Governance

For material business rules, the handoff may preserve:

* stable rule identity and statement;
* source and rationale;
* owner or business authority;
* effective or expiration conditions;
* exceptions;
* dependencies and conflicts;
* enforcement locations when useful for impact analysis.

## Integrity

* Unknown information remains unknown; absence must not be converted into fabricated values.
* Derived information must be distinguishable from directly stated source evidence.
* Newer evidence supersedes older evidence only when that relationship is explicit and provenance is retained.
* Downstream consumers may select a relevant subset but must preserve requirement identity and semantics.
* A material semantic change creates a requirements concern and must not be hidden as a downstream transformation.
* When requirement semantics change, consumers should be able to identify downstream artifacts that require re-evaluation.
* A proposed technical solution does not become a requirement unless evidence supports it as intent, constraint, or decision.
* The contract defines knowledge; it does not require every field or artifact for every context.

## Portability

The contract defines meaning, not serialization. A platform adapter may represent it in another format as long as these semantics are preserved.
