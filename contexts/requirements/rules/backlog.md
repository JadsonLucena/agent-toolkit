# Backlog Rules

## Core Principles

* A backlog is a delivery decomposition of supported requirements and decisions, not a substitute for requirements discovery or specification.
* Preserve requirement semantics while decomposing work.
* Every backlog item that implements or verifies a requirement must trace to the relevant requirement or specification identifier when one exists.
* Do not create scope merely to make the backlog appear complete.
* If decomposition exposes a material requirement ambiguity, return it for clarification or specification rather than resolving it by invention.
* Keep backlog structure compatible with the project's established hierarchy and tracker conventions.

## Work Item Quality

A backlog item should:

* represent one coherent delivery outcome or enabling unit;
* state the intended outcome rather than only an implementation activity when outcome language is possible;
* carry the acceptance conditions needed to determine completion;
* identify relevant dependencies and ordering constraints supported by evidence;
* be small enough for planning and ownership without fragmenting one inseparable behavior into artificial tasks;
* preserve traceability to source requirements and relevant decisions.

## Hierarchy and Decomposition

* Use the repository or organization hierarchy when one exists.
* Do not assume a universal epic, feature, story, task hierarchy.
* Create parent items only when they provide useful grouping, scope, or outcome context.
* Split items by independently valuable behavior, risk, dependency, or verification boundary rather than by file or technical layer alone.
* Technical tasks may exist when they represent necessary enabling work, but they must trace to the outcome, constraint, risk, or requirement that justifies them.

## Acceptance and Readiness

* Reuse requirement acceptance conditions when they already express the item boundary.
* Add item-specific acceptance conditions only when decomposition requires narrower observable completion criteria.
* Do not mark an item ready when a material unresolved question can change its semantics, scope, dependencies, or acceptance.
* Missing implementation detail is not automatically a blocker if the item remains semantically clear and design can legitimately decide it later.

## Priority and Ordering

* Preserve stakeholder or product priority when provided.
* Do not infer business priority from implementation convenience, file order, or model preference.
* Distinguish priority from dependency order.
* If sequencing is technically required, record the dependency even when business priority is unknown.

## Traceability

* Maintain forward links from requirements to backlog items and backward links from backlog items to requirements when the storage system supports them.
* Avoid orphan backlog items with no evidenced purpose.
* Avoid accepted requirements with no planned realization unless explicitly deferred, rejected, external, or otherwise accounted for.
* When requirements change, identify impacted backlog items before treating the backlog as current.

## Quality Guardrails

* Do not silently rewrite requirements while generating backlog items.
* Do not add speculative features, edge cases, metrics, or constraints as committed scope.
* Do not manufacture estimates, priorities, owners, dates, or release assignments without supported input.
* Do not claim backlog completeness while material requirements or traceability gaps remain unresolved.
