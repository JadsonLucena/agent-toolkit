# Implement Slice

## Intent

Implement one bounded, coherent, verifiable software change under the accepted specification and authorized Change Boundary.

## Invocation

Select the Implementation Engineer and implement-slice procedure. Authorizes in-scope production and related test edits and local checks; completed verified atomic intentions may be locally committed under the existing Git rules unless explicitly prohibited. No permission to publish or deploy is inferred.

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
* Explicit mutation exclusions, credentials/external-effect approvals and local-commit restrictions if any.

## Output

Implemented scope and file inventory, observed tests/checks and revision, coherent local commit references if permitted, unresolved questions, residual risks, and explicit implemented/blocked/incomplete status.

## Boundary

No silent requirement or scope change; no mutation of unrelated work, unapproved external effects, push, PR creation, merge, deployment or release. Missing material authority or mandatory evidence blocks the affected slice.
