# Plan Pull Requests

## Intent

Plan one or more coherent pull-request boundaries for a larger change before implementation or review.

## Invocation

Use when a feature, defect, migration, refactor, use-case slice, Product Slice, work item, or other change may require more than one review unit.

Invocation authorizes read-only analysis and PR-boundary planning. It does not authorize implementation or repository mutation.

## Uses

* Agent: `contexts/git/agents/git-engineer.md`
* Skill: `contexts/git/skills/manage-pull-request/SKILL.md` in `plan` mode
* Rule: `contexts/git/rules/pull-request.md`
* Rule: `contexts/git/rules/git.md`
* Optional contract: `contracts/work-item.md`
* Optional contract: `contracts/test-basis.md`

## Inputs

* The change to plan: requirement, rule, use case, scenario set, Product Slice, work item, defect, migration, refactor, or explicit developer intent.
* Repository context when available.
* Intended integration target or branch lifecycle when known.
* Existing implementation/dependency constraints when material.
* Existing PRs or planned PRs when the change is already partially decomposed.

## Output

An ordered PR plan containing, for each proposed PR:

* one primary objective;
* included and excluded scope;
* traceability to supplied source artifacts;
* intended base/dependency relationships;
* required scenarios, acceptance criteria, invariants, or guarantees;
* expected verification evidence;
* integration-safety considerations;
* size/complexity signals and decomposition rationale;
* the expected larger-scope state after merge.

## Boundary

This command is read-only.

It does not authorize code or test changes, branch creation, commits, pushes, PR creation/update, merge/rebase, reviewer assignment, labeling, release, deployment, or other repository/remote mutation.

Do not split a coherent change merely to satisfy a line-count heuristic, and do not invent missing product or implementation intent to complete the plan.
