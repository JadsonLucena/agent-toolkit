# Behavior-Preserving Refactoring — Conditional Guide

Load only for material structural work, preparatory changes, or legacy code with weak regression evidence. The owning `implement-slice` Skill controls edits, scope, verification and Git handoffs.

## Identify intent before editing

- **TDD REFACTOR:** a bounded post-GREEN improvement within the currently authorized intention. No improvement is a valid outcome.
- **Structural-only:** behavior remains unchanged; establish a passing baseline, not a manufactured RED.
- **Preparatory:** a minimal structural prerequisite to an authorized behavior change. Apply Git's independent reversible-intention test before the first edit.
- **Behavior change or defect fix:** not refactoring. Return unsupported acceptance semantics to Requirements and material design changes to Design.

For each candidate record the observed cost (for example change amplification, coupling, opaque dependency, cognitive load or repeated test setup), change boundary, intended improvement, and expected verification. A smell, rule count, or pattern preference is a prompt for investigation, not an automatic mandate. Do not refactor unrelated code to chase cleanliness.

## Preservation boundary

Determine actual callers and affected consumers, current accepted requirements and characterization targets. Preserve where applicable:

- preconditions, postconditions, invariants and substitution guarantees;
- return values, exceptions, data writes, event/API/schema contracts, ordering and timing guarantees;
- transactional integrity, concurrent behavior, retry/idempotency rules and recovery;
- external effects, including duplicate payment, message or notification prevention.

Current behavior may include defects. Capture it as observed without silently declaring it correct business policy; separate an explicitly authorized fix from structural work.

## Small-step procedure

1. Identify the smallest material structural problem and expected benefit. If the problem is a substantial architectural decision, return to Design for alternatives.
2. Select representative existing tests or create authorized characterization/contract tests. Record what the baseline actually covers and does **not** cover.
3. Make one reversible, behavior-preserving transformation (for example Extract Function, Move Function, Encapsulate Variable). Follow existing repository patterns unless a supported decision justifies otherwise.
4. Run focused and affected regressions after each material step, then required integrated checks. Stop and diagnose differences instead of changing tests to conceal them.
5. Evaluate the result against the initial problem. Remove an abstraction that adds indirection without hiding meaningful complexity; an explicit no-op is preferable to speculative design.
6. Handoff the current verified intention and its real checks to Git; never bundle newly discovered separate intentions, claim independent Code Review, or publish without authority.

## Legacy and migration choices

Use Feathers-style seams and characterization when coupling prevents controlled testing. For larger replacements, select strategy with Design: Branch by Abstraction for internal implementation substitution, Parallel Change for API/schema compatibility, Strangler Fig for incremental capability displacement. Differential/shadow comparison must suppress irreversible external effects; routing rollback alone does not reverse durable data.

## Stop and handoff

Stop for missing critical contracts or baselines, failing required checks, changes to accepted behavior, material new dependencies, out-of-scope cleanup, or unverifiable external effects. Report what was verified and what remains unknown, preserving the narrowest safe intermediate state.

Foundations: Fowler (*Refactoring*, 2018), Feathers (*Working Effectively with Legacy Code*, 2004), Meyer (Design by Contract), Ousterhout (*A Philosophy of Software Design*, 2021), Kerievsky (*Refactoring to Patterns*, 2004).