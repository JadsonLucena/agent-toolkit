# Design Solution

## Intent

Design the next bounded implementation slice from supported requirements, decisions, constraints, and repository evidence.

## Invocation

Select the Design Engineer and design-solution procedure. Authorizes technical analysis and a proposed design, not approval of business requirements or mutation of production/test code or Git state.

## Uses

* Agent: `contexts/design/agents/design-engineer.md`
* Skill: `contexts/design/skills/design-solution/SKILL.md`
* Rule: `contexts/design/rules/design.md`
* Output contract: `contracts/design-evidence.md`
* Optional input contract: `contracts/requirements.md`
* Optional input contract: `contracts/work-item.md`

## Inputs

* Authorized change objective and intended implementation slice.
* Applicable accepted requirements, scenarios and Change Boundary when present.
* Existing architecture, interface, project conventions and risk evidence.
* Decisions, unknowns, compatibility and operational constraints when known.

## Output

An evidence-backed design for the next slice, including affected boundaries and interface decisions, trade-offs as justified, recovery considerations, risks, traceable decisions, unresolved authority and explicit readiness.

## Boundary

No requirement semantic changes or silent approvals. No source/test code mutation, Git operations, deployments or invented acceptance results. Escalate material source ambiguity to Requirements and implementation work to a separately authorized capability.
