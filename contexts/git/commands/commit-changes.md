# Commit Changes

## Intent

Create safe, atomic commits for an explicitly authorized set of repository changes.

## Invocation

This command authorizes commit creation only for the defined change set. It does not authorize push, merge, tag, release, or remote-ref mutation.

## Uses

* Agent: `contexts/git/agents/git-engineer.md`
* Skill: `contexts/git/skills/commit-changes.md`

## Inputs

* Authorized change scope.
* Repository state and conventions.
* Optional requirement, backlog, issue, or work-item context as supporting intent evidence.

## Output

Verified commit(s), commit identifiers, remaining uncommitted state, verification results, and any blockers.

## Boundary

If commit semantics or change partitioning remain materially ambiguous, ask the developer before committing.
