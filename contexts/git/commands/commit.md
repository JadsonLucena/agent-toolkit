# Commit

## Intent

Create one or more safe, atomic semantic commits from an explicitly authorized set of repository changes.

## Invocation

This command authorizes commit creation only for the defined change scope. It does not authorize push, merge, tag, release, remote-ref mutation, or rewriting published history.

## Uses

* Agent: `contexts/git/agents/git-engineer.md`
* Skill: `contexts/git/skills/create-semantic-commits/skill.md`
* Rule: `contexts/git/rules/git.md`
* Rule: `contexts/git/rules/semantic-commit.md`

## Inputs

* Authorized change scope.
* Repository state and conventions.
* Optional developer intent, requirement, issue, or work-item references.
* Optional verification constraints.

## Output

Verified atomic commits, commit identifiers, verification evidence, remaining repository state, and any blocker or unresolved semantic ambiguity.

## Boundary

The staged diff and verified repository state remain authoritative for what is committed. If semantic intent or change partitioning is materially ambiguous, ask before committing. Authorization does not silently expand to adjacent Git mutations.
