# Requirements Rules

## Core Principles

* Treat requirements as evidence-backed statements of stakeholder need, system obligation, constraint, or quality expectation.
* Preserve the distinction between source evidence, interpretation, assumption, decision, and derived requirement.
* Do not invent stakeholder intent to complete a workflow.
* State material assumptions explicitly.
* If ambiguity or missing evidence can materially change scope, behavior, acceptance, priority, or downstream work, obtain stakeholder or developer clarification rather than guessing.
* Prefer problem and outcome language during elicitation; do not turn a proposed solution into a requirement unless the solution itself is an explicit constraint or decision.
* Keep requirements traceable from their source through specification, backlog decomposition, implementation, and verification when those artifacts exist.
* Use stable identifiers once requirements enter specification or downstream traceability.

## Evidence and Provenance

* Record the source of each material requirement, constraint, decision, or assumption.
* Distinguish direct evidence from derived conclusions.
* When sources conflict, preserve the conflict until an authorized stakeholder resolves it; do not silently choose one source.
* Do not present inferred priorities, business rules, personas, constraints, or acceptance conditions as stakeholder-approved facts.
* New clarification supersedes older evidence only when the relationship is explicit; retain enough provenance to explain the change.

## Requirement Quality

A specified requirement should be:

* necessary for an evidenced goal, constraint, or decision;
* clear enough to admit one materially relevant interpretation;
* atomic enough to reason about, trace, change, and verify without hiding unrelated obligations;
* consistent with other accepted requirements or explicitly marked as conflicting;
* feasible to assess with the available technical and organizational context, without inventing feasibility evidence;
* verifiable through observable acceptance conditions, inspection, analysis, demonstration, or test;
* implementation-neutral unless a technology, interface, architecture, or solution choice is itself required;
* traceable to its source and downstream artifacts.

## Requirement Types

Use the project's established taxonomy when one exists. Otherwise distinguish only when useful:

* business or outcome requirements;
* stakeholder or user requirements;
* functional requirements;
* non-functional or quality requirements;
* constraints and externally imposed obligations;
* transition or operational requirements.

Do not force every statement into a taxonomy when classification adds no engineering value.

## Acceptance Conditions

* Acceptance conditions must describe observable evidence of satisfaction.
* Do not encode unstated implementation choices into acceptance conditions.
* Include relevant alternate, failure, boundary, permission, data, and quality conditions when they materially affect acceptance.
* If a quantitative threshold is required but no supported value exists, record the threshold as unresolved and request clarification rather than inventing a number.

## Scope and Change

* Record material in-scope and out-of-scope boundaries when known.
* Treat a material change in stakeholder need, constraint, or acceptance as a requirement change, not a silent edit.
* Re-evaluate affected specifications, backlog items, tests, and traceability after a material requirement change.
* Do not preserve an obsolete interpretation merely because downstream artifacts already depend on it.

## Quality Guardrails

* Do not equate elicited notes with validated requirements.
* Do not equate a user story with the complete requirement set when additional rules, constraints, quality attributes, or acceptance conditions exist.
* Do not use priority as a substitute for clarity.
* Do not claim stakeholder approval, feasibility, completeness, or validation without evidence.
* Do not let formatting completeness hide unresolved semantic ambiguity.
