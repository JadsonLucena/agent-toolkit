# Requirements Workflow Contract

This contract defines the neutral handoff shape between requirements elicitation, specification, validation, and backlog planning. It is a data contract, not a rule set or workflow.

## General Envelope

Every handoff should carry:

* `context_id` — stable identifier for the requirement context or initiative.
* `sources` — source identifiers and concise provenance.
* `decisions` — explicit stakeholder or developer decisions relevant to the handoff.
* `assumptions` — material assumptions, each marked as confirmed or unconfirmed.
* `open_questions` — unresolved questions whose answers may change semantics or scope.
* `conflicts` — unresolved contradictions between sources, requirements, or decisions.
* `status` — semantic readiness such as `draft`, `needs-clarification`, `ready-for-specification`, `ready-for-backlog`, or `blocked`.

Do not use numeric confidence scores as a substitute for evidence.

## Elicitation Handoff

The elicitation handoff may include:

* problem or opportunity statement;
* desired outcomes and success evidence;
* stakeholders and actors;
* scope boundaries;
* candidate requirements;
* business rules;
* functional needs;
* non-functional or quality needs;
* constraints;
* dependencies;
* risks;
* glossary or domain language;
* provenance for every material statement.

Candidate requirements do not become approved requirements merely by appearing in this handoff.

## Specification Record

A specified requirement should contain, when applicable:

* `requirement_id`;
* title or short label;
* normative statement;
* type or category when useful;
* rationale;
* source references;
* acceptance conditions;
* dependencies and relationships;
* constraints;
* priority only when evidenced;
* status;
* unresolved questions;
* material assumptions.

A requirement may remain `needs-clarification`; the contract does not require invented values to make every field complete.

## Backlog Record

A backlog item should contain, when applicable:

* `work_item_id`;
* tracker-native kind or level;
* title;
* intended outcome;
* requirement references;
* relevant acceptance-condition references or item-specific acceptance conditions;
* dependencies;
* priority or ordering only when evidenced;
* status/readiness;
* unresolved questions.

## Traceability

Traceability should support:

`source → requirement → backlog item → implementation/verification evidence`

Not every environment stores every link in one system. Preserve stable identifiers and enough references to reconstruct the chain without depending on a specific vendor.
