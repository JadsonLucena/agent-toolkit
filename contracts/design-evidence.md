# Design Evidence Contract

## Purpose

Carry technical design decisions across the Requirements-to-Implementation boundary without turning Design into a new requirements authority or imposing a template, format, or tool.

## Context Semantics

When material, preserve:

* `context_id` — shared change identity when supplied;
* `change_boundary_ref` — the governing Change Boundary when one exists;
* `source_baseline_ref` — accepted requirement or design baseline used, never invented;
* `slice_ref` — the intended bounded implementation outcome;
* `source_refs` — requirements, constraints, scenarios, existing code, ADRs and decisions that justify the design;
* `decision_refs` — stable technical decisions and their owners/authorization when known;
* `design_status` — `sufficient`, `needs-revision`, `needs-clarification`, or `blocked`, scoped to `readiness_for`.

## Technical Decision Semantics

For each material decision, preserve the concern, supported choice, rationale and relevant alternatives/trade-offs; affected responsibilities, interfaces, data contracts or states; assumptions and unresolved authority; and impact on compatibility, deployment, security, recovery and verification where relevant.

A proposed technical decision must remain distinguishable from an approved one when authority is material. The receiving Implementation capability may not assume an unapproved product or contract decision is binding.

## Integrity and Handoff

* Preserve source identities and upstream semantics. A design alternative is not a business requirement.
* Do not infer acceptance, implementation, passing tests, independent review, rollout or business outcomes from design readiness.
* When a source baseline changes, re-evaluate affected decisions and consumers instead of silently reusing stale design evidence.
* Material contradictions in business rules, scope or acceptance return to the Requirements owner.
* An absent design document is not proof that a change cannot proceed: the need for formal design evidence is risk- and decision-proportionate.

## Portability

These are neutral semantics, not a mandatory YAML/JSON/Markdown representation, ADR format, architecture notation, tool, or runtime dependency.
