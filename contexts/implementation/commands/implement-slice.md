---
name: implement-slice
description: "Implement authorized production changes, preferring test-first TDD when feasible, with caller opt-out, verified checks and safe Git handoffs. Not for test-only work."
---

# Implement Slice

## Intent

Implement one bounded, coherent, verifiable software change under the accepted specification and authorized Change Boundary.

## Invocation

Select the Implementation Engineer and implement-slice procedure. Apply the Implementation rule's preferred-TDD selection for testable behavior changes; absence of a TDD request is not a direct-implementation exception. An explicit caller TDD opt-out affects sequencing, not required testing. Authorizes in-scope production and related test edits and local checks; completed verified atomic intentions may be locally committed under the existing Git rules unless explicitly prohibited by the caller or repository. An authorized implementation plan need not repeat commit permission; preserve restrictions inherited from the invoking context. When necessary, a read-only Git PR-plan handoff precedes the first mutation; each authorized completed atomic intention is handed to Git for commit verification before further intentions. No permission to publish or deploy is inferred.

## Uses

* Agent: `contexts/implementation/agents/implementation-engineer.md`
* Skill: `contexts/implementation/skills/implement-slice/SKILL.md`
* Rule: `contexts/implementation/rules/implementation.md`
* Optional input contract: `contracts/design-evidence.md`
* Optional input contract: `contracts/test-basis.md`
* Optional output contract: `contracts/test-evidence.md`

## Inputs

* Authorized slice, Change Boundary and intended acceptance/verification criteria.
* Applicable specification, design and risk constraints when available.
* Repository state, existing work and project verification conventions.
* Existing PR strategy or PR Boundary (when applicable), or the evidence needed for a conditional read-only Git PR plan.
* Explicit TDD requirement or caller TDD opt-out, when supplied; otherwise prefer TDD for testable behavior.
* Explicit mutation exclusions, credentials/external-effect approvals and local-commit restrictions if any.

## Output

The result describes completed Implementation only; independent Review and PR preparation/publication are subsequent Integration-stage operations. Implemented scope and file inventory, observed tests/checks and revision, verified Git commit references and actual resulting state if permitted (otherwise explicit uncommitted status), relevant PR-plan status, unresolved questions, residual risks, and explicit implemented/blocked/incomplete status.

## Boundary

No silent requirement or scope change; no mutation of unrelated work, unapproved external effects, push, PR creation, merge, deployment or release. Missing material authority or mandatory evidence blocks the affected slice.
