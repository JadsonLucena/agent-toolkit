# Requirements Rules

## Core Principles

* Requirements must express stakeholder or system needs as verifiable constraints on observable behavior, outcomes, qualities, interfaces, data, or operating conditions.
* Preserve the distinction between source evidence, derived requirement, assumption, decision, and unresolved question.
* Derive requirements only from supported evidence and explicit context. Do not invent stakeholder intent to make a specification appear complete.
* Preserve traceability from each material requirement to its supporting source or rationale and through later derived artifacts when identifiers are available.
* Use terminology consistently with the domain and source material. Define ambiguous or overloaded terms when their meaning affects behavior.
* Keep requirements solution-neutral unless a technology, architecture, interface, standard, or implementation constraint is itself part of the supported requirement.

## Evidence and Provenance

* Record the origin of material requirements, constraints, business rules, and decisions when that origin is known.
* Distinguish directly stated needs from analyst-derived implications.
* Treat existing software behavior, documentation, tickets, policies, regulations, contracts, interviews, and developer context as evidence with potentially different authority; do not silently resolve conflicts between them.
* Surface conflicting evidence and identify what must be clarified or decided.
* Never present an unsupported inference as a stakeholder-approved requirement.

## Ambiguity and Assumptions

* State material assumptions explicitly.
* Continue with an explicit assumption only when uncertainty is low impact and does not materially alter semantic intent, scope, acceptance criteria, behavior, compatibility, security, or the resulting operation.
* Ask for clarification when ambiguity can materially change the requirement or a downstream decision.
* Stop only the affected decision when missing information is blocking; preserve work that remains valid independently.
* Keep unresolved questions visible until they are answered, intentionally deferred, or declared out of scope.

## Requirement Quality

A requirement should be, to the degree appropriate for its scope:

* necessary and supported by evidence;
* clear and unambiguous;
* singular enough to reason about and trace;
* feasible within known constraints, or explicitly marked when feasibility is unverified;
* verifiable through observable evidence;
* consistent with other accepted requirements and business rules;
* sufficiently complete for the decision or downstream artifact that consumes it;
* traceable to its source, rationale, parent need, or governing constraint.

Do not create false precision. Unknown values, thresholds, priorities, dates, actors, or policies must remain explicit unknowns when evidence does not establish them.

## Requirement Semantics

* Distinguish stakeholder goals and needs from formal requirements.
* Distinguish functional behavior from quality attributes, business rules, external constraints, interface constraints, data constraints, and operational constraints when the distinction materially improves understanding or verification.
* Capture relevant preconditions, triggers, states, transitions, outcomes, failure behavior, invariants, and boundaries when they are part of the required behavior.
* Capture non-functional requirements as measurable or otherwise verifiable qualities whenever practical; avoid vague adjectives without an observable criterion.
* Treat business rules as domain constraints that may govern multiple requirements or backlog items; do not duplicate them inconsistently.
* Record dependencies and conflicts when one requirement relies on, constrains, excludes, or supersedes another.

## Acceptance and Verification

* Acceptance criteria must describe observable evidence that can distinguish acceptable from unacceptable behavior.
* Acceptance criteria refine verification of a requirement; they must not silently introduce unrelated stakeholder intent.
* Do not prescribe a test level, framework, or implementation technique unless that is itself required.
* A requirement may be valid before executable tests exist, but it must be possible to explain how its satisfaction could be evaluated.

## Traceability

* Preserve identity across transformations from source need to requirement, acceptance evidence, backlog item, implementation reference, and test evidence when those artifacts exist.
* Traceability identifiers must be stable within their scope and must not be fabricated from external systems.
* Downstream artifacts may summarize a requirement but must not silently change its semantics.
* When a downstream artifact exposes a material ambiguity or contradiction, return the issue to the requirement source rather than resolving it by invention.

## Quality Guardrails

* Do not treat a backlog item, implementation detail, commit message, or test as the authoritative source of stakeholder intent when a requirement source exists.
* Do not mark a requirement complete merely because a template is filled.
* Do not hide uncertainty behind generic wording such as "as appropriate", "user friendly", "fast", or "secure" when the missing criterion is material.
* Do not combine independent obligations into one requirement when doing so harms verification, traceability, or change control.
* Do not split a coherent requirement solely to satisfy an arbitrary format.
* Do not impose Scrum, a specific ticketing system, a specific requirements notation, or a vendor-specific schema.
