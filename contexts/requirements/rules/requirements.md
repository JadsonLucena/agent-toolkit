# Requirements Rules

Apply `contexts/requirements/rules/tailoring.md` when deciding how much rigor and representation are necessary.

## Core Principles

* Requirements must express stakeholder or system needs as verifiable constraints on observable behavior, outcomes, qualities, interfaces, data, or operating conditions.
* Preserve the distinction between source evidence, derived requirement, assumption, option, decision, and unresolved question.
* Derive requirements only from supported evidence and explicit context. Do not invent stakeholder intent to make a specification appear complete.
* Preserve traceability from each material requirement to its supporting source or rationale and through later derived artifacts when identifiers are available.
* Use terminology consistently with the domain and source material. Define ambiguous or overloaded terms when their meaning affects behavior.
* Keep requirements solution-neutral unless a technology, architecture, interface, standard, or implementation constraint is itself part of the supported requirement.
* Judge sufficiency by the next decision and selected rigor, not by whether a template is fully populated.

## Strategic Framing

When material to the change, keep these concepts distinct:

* **Need** — the problem, opportunity, obligation, or undesirable condition that justifies change.
* **Business Goal** — the desired outcome that addresses the need.
* **Success Metric** — evidence that an outcome or value changed; do not confuse it with an output, fit criterion, acceptance criterion, or test assertion.
* **Current State** — relevant behavior, process, policy, data, system, constraints, and outcomes today.
* **Future State** — the desired future condition independent of unsupported implementation detail.
* **Change / Gap** — the material difference between current and future state. A gap is evidence for change, not automatically a requirement.

When current-state knowledge matters, distinguish genuine business rules from accidental or historical implementation limitations.

## Scope and Solution Boundary

* Distinguish **Work Scope** from **Product Boundary** when the broader change may include people, process, policy, purchased products, manual operations, or partial automation.
* Do not assume that every need should be solved by software.
* Treat a proposed API, dashboard, queue, framework, datastore, service, or other technical mechanism as a candidate solution unless supported as an explicit constraint or decision.
* When solution uncertainty is material, preserve candidate options and the evidence needed to compare them rather than collapsing prematurely to one design.
* A prototype, experiment, probe, or spike may be valid work when its purpose is to reduce a material uncertainty.

## Business Events and Business Response

When event completeness is useful:

* identify material external, temporal, human-initiated, and system-initiated business events;
* identify the required business response without assuming the entire response belongs to software;
* distinguish a business response from the product behavior that implements only part of it.

Do not require a formal Business Use Case when another representation captures the same knowledge adequately.

## Transition Requirements

When a change moves data, users, operations, or systems between states, identify temporary obligations separately from permanent solution requirements, including when relevant:

* migration, backfill, conversion, or reconciliation;
* temporary compatibility or dual operation;
* feature flags, rollout, rollback, or cutover;
* training or temporary permissions;
* decommissioning and data lifecycle consequences.

Do not hide transition work inside permanent product behavior.

## Business Knowledge and Rules

* Keep important domain terms explicit and consistent; distinguish domain language from technical implementation vocabulary.
* Capture material facts and relationships between domain concepts, including n-ary relationships when the domain requires them.
* Treat business rules as declarative business knowledge that may define concepts or structures, constrain behavior, establish eligibility or authorization, classify or derive information, define calculations, or govern decisions and actions across multiple requirements, scenarios, work items, or tests.
* Keep **Business Rule**, **Domain Invariant**, **Functional Requirement**, **Process**, and **Implementation** conceptually distinct. A business rule may lead to an invariant, requirement, decision, or enforcement mechanism, but is not automatically any one of them.
* Keep rule meaning separate from enforcement. The same rule may be enforced by domain logic, application policy, workflow, database constraints, external policy services, or another justified mechanism.
* Do not bury authoritative business rules only inside code, SQL, use-case steps, stories, or acceptance criteria.
* For critical rules, preserve governance information when known and useful: stable identity, statement, source, rationale, owner or authority, effective/expiration conditions, exceptions, dependencies, conflicts, and enforcement locations.
* A rule's absence of an owner or authority is a governance finding when changing that rule requires business authorization.

## Evidence and Provenance

* Record the origin of material requirements, constraints, business rules, and decisions when that origin is known.
* Distinguish directly stated needs from analyst-derived implications.
* Treat existing software behavior, documentation, tickets, policies, regulations, contracts, interviews, data, and developer context as evidence with potentially different authority; do not silently resolve conflicts between them.
* Surface conflicting evidence and identify what must be clarified or decided.
* Newer evidence supersedes older evidence only when the supersession relationship is explicit; preserve enough provenance to explain what changed and why.
* Never present an unsupported inference as a stakeholder-approved requirement.
* User proxies, historical software behavior, and existing documentation are evidence, not automatically authoritative stakeholder intent.

## Ambiguity, Assumptions, Unknowns, and Options

* State material assumptions explicitly.
* Continue with an explicit assumption only when uncertainty is low impact and does not materially alter semantic intent, scope, acceptance criteria, behavior, compatibility, security, or the resulting operation.
* Ask for clarification when ambiguity can materially change the requirement or a downstream decision.
* Stop only the affected decision when missing information is blocking; preserve work that remains valid independently.
* Keep unresolved questions visible until they are answered, intentionally deferred, or declared out of scope.
* For material unknowns, record when useful: the unknown statement, risk if unresolved, how it can be learned, and any decision deadline.
* For material options, record when useful: alternatives, evidence needed, option-expiration conditions, and the cost or consequence of committing now versus delaying.
* Treat uncertainty as knowledge to manage, not as a defect to hide.

## Requirement Quality

A requirement should be, to the degree appropriate for its scope and rigor:

* necessary and supported by evidence;
* clear and unambiguous;
* singular enough to reason about and trace;
* feasible within known constraints, or explicitly marked when feasibility is unverified;
* verifiable through observable evidence;
* consistent with other accepted requirements and business rules;
* sufficiently complete for the decision or downstream artifact that consumes it;
* traceable to its source, rationale, parent need, goal, or governing constraint;
* proportional in value and rigor to the cost and risk it introduces.

Do not create false precision. Unknown values, thresholds, priorities, dates, actors, metrics, or policies must remain explicit unknowns when evidence does not establish them.

## Functional Behavior, Use Cases, and Scenarios

* Distinguish stakeholder goals from technical steps and CRUD operations.
* When Use Cases are useful, preserve the actor goal and relevant scope, trigger, preconditions, guarantees, main behavior, and meaningful alternatives or exceptions.
* Keep the actor goal whole; incremental delivery may slice realization without inventing artificial mini use cases.
* Treat scenarios as first-class behavioral knowledge when they improve understanding. Useful dimensions may include current/desired state, positive/negative, misuse, instance/type, system-internal/interaction/context, main/alternative/exception, and exploratory/explanatory/descriptive.
* These scenario dimensions are not mutually exclusive.
* Distinguish an invalid business condition from a caller/callee contract violation when that distinction affects behavior or verification.

## Data Requirements

When data semantics are material, define enough of the following to avoid implementation-driven assumptions:

* meaning, source, ownership, type, precision, units, and nullability;
* temporal semantics, timezone, and historical behavior;
* integrity and consistency expectations;
* lifecycle, retention, archiving, and disposal;
* lineage, reporting, acquisition, and privacy classification.

For distributed or replicated data, consider when relevant:

* system of record and derived data;
* freshness and stale-read tolerance;
* duplicates, ordering, replay, and reprocessing;
* idempotency;
* event or schema versioning and compatibility;
* materialized views and lineage;
* consumer guarantees.

A storage type such as `datetime` or `decimal` is not a complete data requirement.

## Quality Requirements

* Capture quality concerns as contextualized goals rather than vague adjectives.
* Refine broad concerns when necessary to make trade-offs and verification meaningful.
* When objective acceptance is required, use fit criteria that state the relevant context, operation or stimulus, conditions/workload, expected response, metric or observable property, threshold when justified, and rationale.
* Do not invent arbitrary thresholds or percentiles merely to make a requirement measurable.
* Record relevant quality trade-offs and assumptions when one decision helps one goal while hurting another.
* For material reliability concerns, make the expected failure model explicit enough to reason about timeouts, retries, partial failure, duplicates, crashes, dependency outages, lag, and concurrent updates.

## Security Requirements

When security is material, reason beyond a generic "secure" requirement. Preserve relevant knowledge about:

* actors, responsibilities, dependencies, and delegations;
* information assets, ownership, representation, and flows;
* authorization: who may perform which operation on what information, for what purpose, and under which delegation constraints;
* organizational obligations such as separation or binding of duties, non-repudiation, need-to-know, least privilege, redundancy, non-delegation, or purpose limitation;
* misuse, malicious threats, accidental violations, and ordinary negative business scenarios as distinct concepts.

Check security requirements for conflicts with each other and with required business goals or operations.

## Requirement Patterns

Patterns may be used as reusable requirements knowledge to improve elicitation, specification, and validation. They are investigation and specification guides, not pre-written requirements.

When a pattern is applicable, preserve only the guidance that is useful to the current context, which may include:

* the recurring problem or intent the pattern addresses;
* applicability and non-applicability signals;
* questions and knowledge that should be obtained;
* expected requirement content or semantic dimensions;
* templates or examples used only as guidance;
* related or extra requirement concerns that are often worth checking;
* development considerations that may affect feasibility or downstream design;
* testing considerations that may affect verification.

Check applicability before expanding related concerns. A pattern may point to other patterns without making those concerns mandatory. For example, an inter-system interface may lead to authentication, authorization, availability, response-time, throughput, compatibility, logging, upgrade, documentation, error-handling, or data-longevity questions only when the context supports them.

Treat pattern relationships as a graph of candidate questions and concerns rather than a checklist. Do not create requirements solely because a pattern contains them.

When the same requirements problem recurs across initiatives, it may become a candidate organizational pattern after review. Reuse should capture learned questions and omissions without duplicating live business rules or turning a domain-specific specification into a generic pattern prematurely.

## Rationale, Acceptance, and Validation

* Significant requirements should have a discoverable rationale when the reason is not obvious from their source.
* A missing or weak rationale may indicate gold plating, an obsolete requirement, or an unsupported assumption and should be surfaced.
* Acceptance criteria must describe observable evidence that can distinguish acceptable from unacceptable behavior.
* Acceptance criteria refine verification of a requirement; they must not silently introduce unrelated stakeholder intent.
* Do not prescribe a test level, framework, or implementation technique unless that is itself required.
* A requirement may be valid before executable tests exist, but it must be possible to explain how its satisfaction could be evaluated.
* Requirements validation asks whether the specified thing is the right thing for the supported need; do not equate requirements validation with software testing.
* Validation evidence may come from stakeholder review, walkthrough, examples, prototypes, model review, inspection, checklists, or other supported evidence.

## Requirement Change and Impact

* Treat a material change in stakeholder need, goal, constraint, business rule, acceptance semantics, or governing evidence as a requirement change rather than a silent edit.
* Preserve the superseded interpretation or enough history to explain the change when the surrounding system supports it.
* Re-evaluate affected acceptance criteria, dependent requirements, planning items, design decisions, implementation references, examples, and test evidence after a material requirement change.
* Do not preserve an obsolete interpretation merely because downstream artifacts already depend on it.
* Impact analysis should identify what remains valid independently and what requires revision, clarification, re-planning, re-design, or re-verification.

## Requirements Architecture and Traceability

Preserve useful relationships when the corresponding knowledge exists, for example:

```text
Source / Rationale
        ↓
Need → Goal
        ↓
Policy / Rule / Constraint
        ↓
Requirement
        ↓
Use Case / Scenario / Slice
        ↓
Example / Acceptance Evidence
        ↓
Design / Implementation / Test
        ↓
Outcome Evidence
```

* Preserve identity across transformations without requiring a matrix when hyperlinks, graph relationships, or another representation already solve the problem.
* Traceability identifiers must be stable within their scope and must not be fabricated from external systems.
* Detect material orphan relationships, such as a requirement with no supported need/rationale, a work item with no source, a test with no behavior, or a design decision with no evidenced driver.
* Downstream artifacts may summarize a requirement but must not silently change its semantics.
* When a downstream artifact exposes a material ambiguity or contradiction, return the issue to the requirement source rather than resolving it by invention.

## Quality Guardrails

* Do not treat a backlog item, implementation detail, commit message, or test as the authoritative source of stakeholder intent when a requirement source exists.
* Do not mark a requirement complete merely because a template is filled.
* Do not equate elicitation notes with validated requirements.
* Do not equate a user story with the complete requirement set when additional rules, constraints, quality attributes, states, or acceptance conditions exist.
* Do not use priority as a substitute for semantic clarity.
* Do not let formatting or template completeness hide unresolved semantic ambiguity.
* Do not hide uncertainty behind generic wording such as "as appropriate", "user friendly", "fast", or "secure" when the missing criterion is material.
* Do not combine independent obligations into one requirement when doing so harms verification, traceability, or change control.
* Do not split a coherent requirement solely to satisfy an arbitrary format.
* Do not impose Scrum, a specific ticketing system, a specific requirements notation, or a vendor-specific schema.
* Do not require every artifact or technique in this rule for every change; apply only the knowledge concerns justified by `tailoring.md`.
