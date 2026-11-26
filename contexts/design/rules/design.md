---
description: "Apply when designing a bounded software change, evaluating architecture decisions and tradeoffs, or defining a technical solution from supported requirements."
alwaysApply: false
---

# Design Rules

## Core Principles

* Transform supported specification and constraints into technical decisions sufficient for the next bounded implementation slice; Design does not authorize changes to product requirements.
* Use the authoritative Requirements Change Boundary and the latest accepted baseline when available. A proposed requirement change is not an accepted design driver without a governing decision.
* Tailor rigor to consequence, uncertainty, reversibility, and the next decision. Do not require an ADR, diagram, technology choice, or design ceremony merely to complete a template.
* Preserve feasibility, traceability, compatibility, operability, security, and data integrity appropriate to the change. Existing repository architecture and project standards take precedence over generic preferences.
* Distinguish known facts, assumptions, alternative options, recommendations, decisions and unresolved authority. A recommendation is not an approval.

## Technical Decision Integrity

* Identify material architecture drivers, affected responsibilities and boundaries, interfaces, data ownership, state transitions and failure behavior before selecting a solution.
* Consider alternatives only where a meaningful choice exists; state their material trade-offs, evidence and rationale. Reuse a proven local pattern when the alternative analysis would add no value.
* Address authorization, idempotency, ordering, concurrency, error handling, latency, accessibility, observability, recovery, and security where they affect the slice. Do not invent technical guarantees absent from sources or applicable standards.
* Relate decisions to requirement, scenario, risk or existing constraint identifiers when present. Preserve authoritative versions and record decisions that still require approval.
* A design can guide Implementation only when the material decisions governing that slice are sufficiently stable. Unresolved issues that can change an API, data contract, safety guarantee or acceptance behavior block the affected handoff, not all unrelated work.

## HTTP API Contract Decisions

* When a slice creates or changes an HTTP API, identify the declared architectural style and applicable published protocol, local contract, and consumer constraints before selecting resource operations or conventions. An HTTP API, a Richardson level, and Fielding's REST constraints are different assessments.
* Preserve HTTP method semantics, authorization, state transitions, representation contracts, failure behavior, caching and conditional requests **where applicable**. Derive explicit choices from supported requirements and standards; do not impose hypermedia, versioned URIs, ETags, idempotent PATCH, or a particular API format universally.
* Capture compatibility and verification consequences of material API changes. Use the conditional guidance in `skills/design-solution/references/http-api-design.md`; Requirements owns unmet behavioral needs, while Design owns the proposed technical realization.

## Refactoring Strategy Selection

* For an evidence-backed structural change, distinguish the observed design problem from a preferred pattern. Assess change amplification, cognitive load, obscured dependencies, information leakage, affected consumers and the cost of verification; code smells or style preferences alone are not sufficient reasons to redesign.
* Choose strategy proportional to the boundary: local behavior-preserving transformation, internal substitution behind an abstraction, compatible API/schema evolution, or incremental displacement of a legacy capability. Consider meaningful alternatives when risk or coupling justifies them, without requiring a pattern catalogue for trivial work.
* Prefer abstractions that hide significant volatile knowledge behind stable interfaces; avoid needless pass-through layers, speculative generality and extra indirection merely to satisfy SOLID, GoF or Object Calisthenics.
* Specify the observable contracts and critical invariants that Implementation must preserve. For replacement or transition architectures, identify routing, coexistence, data ownership, compatibility windows, migration and safe failure/rollback paths. A traffic switch alone does not reverse durable effects.
* Structural improvement and an authorized behavior change remain distinct intentions, even when one prepares for the other; a Design recommendation does not confer mutation or requirements authority.

## Small, Reversible Design

* Prefer the smallest coherent design that can implement and verify the next slice without breaking existing guarantees.
* Preserve compatibility and safe intermediate states when changes span several commits or PRs. Distinguish Git revert from reversal of deployed or durable effects; provide rollback, compensation, reconciliation or forward-fix considerations for material irreversible effects.
* Do not split shared contracts across parallel work until dependencies and integration evidence are explicit. Parallel exploratory analysis may inform one reconciled decision; only authorized Implementation may modify code.
* Document integration, rollout, data migration and operational decisions when risk justifies them, without claiming deployment or measured outcomes.

## Completion and Handoff

* Output should be compatible with `contracts/design-evidence.md` when that semantic handoff is useful.
* Design readiness means material technical decisions for the intended slice are supported, traceable and compatible with applicable requirements. It does **not** imply implementation, successful tests, independent review, release or business outcome.
* Escalate contradictions or gaps in authoritative business semantics to Requirements; do not silently resolve them in Design. Changes to implementation or test artifacts require separately authorized commands.

## Foundational Guidance

Apply design reasoning proportionally, drawing where relevant on architecture decision records, design by contract, DDD boundaries, quality attributes, evolutionary architecture and risk-based decision making. These sources inform judgment; they do not become mandatory practices or override the project.
