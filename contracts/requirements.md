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
* `readiness_for` — optional downstream target for which the status was evaluated, such as backlog planning or design;
* `stage_claims` — optional explicit lifecycle claims such as elicitation sufficient, requirements specified, requirements validated, or planning ready, each with its evidence/target when material.

Do not encode the downstream target into `status`, and do not use numeric confidence scores as a substitute for evidence. A stage claim must not imply a later stage such as implementation, acceptance, deployment, release, or outcome achievement.

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
* `change_boundary` — the current change's objective, included scope, excluded scope, explicitly deferred scope, affected semantics, critical guarantees, dependencies, unresolved scope decisions, and expected state after the bounded change when useful;
* `scope_changes` — material discoveries that clarify, expand, narrow, or sit outside the current Change Boundary, together with the decision/evidence that governs their disposition when known;
* `stakeholders` and affected actors;
* `business_events` and expected business responses when useful for completeness;
* `candidate_solutions` or learning options when solution uncertainty is material;
* `domain_terms`, facts, and business rules;
* functional needs and quality expectations;
* transition needs for migration, rollout, compatibility, cutover, training, or decommissioning;
* constraints and externally imposed obligations;
* dependencies and risks;
* assumptions, options, conflicts, open questions, and decisions;
* provenance for every material statement;
* `representation_convention` — applicable project/organization template, schema, notation, or document convention when one governs the handoff, including unresolved template-selection ambiguity when material.

Elicitation evidence remains distinct from approved specification. Candidate requirements, assumptions, options, and interpretations must not be promoted to accepted requirements merely because they appear in the handoff.

## Change Boundary Semantics

When a Change Boundary is represented, preserve enough information to distinguish:

* primary objective and expected observable change;
* included semantics;
* excluded semantics;
* explicitly deferred semantics and supporting authority/decision when material;
* affected requirement/rule/use-case/scenario references when available;
* critical guarantees that must not be lost by decomposition;
* material dependencies and unresolved scope decisions;
* expected state after the bounded change;
* material boundary revisions and their provenance.

The Change Boundary must remain distinct from Work Scope and Product Boundary. Discovery does not automatically authorize boundary expansion.

## Requirement Specification Semantics

A requirement specification must make the following available when material and known:

* scope, objective, parent need, goal, source, and rationale;
* stable requirement identifiers within the specification scope;
* requirement statements;
* acceptance criteria, fit criteria, examples, or other verification evidence as appropriate;
* business rules and invariants;
* functional, quality, security, interface, data, operational, and transition constraints when relevant;
* actors, triggers, preconditions, states, transitions, outcomes, guarantees, alternatives, exceptions, or failure behavior when they materially improve understanding;
* stable scenario identities and scenario-to-requirement/rule/use-case relationships when scenarios are treated as first-class behavioral knowledge;
* data semantics such as ownership, temporal meaning, integrity, lifecycle, lineage, or consumer guarantees when relevant;
* quality context, metric/observable property, justified thresholds, failure assumptions, and trade-offs when relevant;
* quality verification approach, necessary evaluation conditions and measurement boundaries, and expected evidence for acceptance when material and known; unresolved verification knowledge must remain explicit;
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
* Stable scenario identifiers must survive downstream transformations when supplied; adapters and Testing must not replace semantic scenario identity with framework-specific test names.
* Local templates or schemas may shape representation but must not replace or silently alter these semantics.
* Template completion must not be interpreted as requirements completion.
* A lifecycle stage such as requirements validated or planning ready must not be used as evidence that implementation, acceptance, release, deployment, or business outcome has occurred.
* The contract defines knowledge; it does not require every field or artifact for every context.

## Portability

The contract defines meaning, not serialization. A platform adapter may represent it in another format as long as these semantics are preserved.
