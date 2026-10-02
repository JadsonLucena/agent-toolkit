# Commit

## Intent

Create one or more atomic semantic commits from an explicitly authorized set of repository changes.

## Orchestration

1. Delegate Git specialization and repository-state reasoning to `contexts/git/agents/git-engineer.md`.
2. Apply `contexts/git/skills/create-semantic-commits/skill.md`.
3. Enforce `contexts/git/rules/git.md` and `contexts/git/rules/semantic-commit.md`.
4. Treat work-item, requirement, or backlog context as optional supporting evidence only. The staged diff and verified repository state remain authoritative for what is committed.

## Inputs

* Authorized change scope.
* Repository state and conventions.
* Optional developer intent or work-item references.
* Optional verification constraints.

## Output

The created atomic commits, verification evidence, remaining repository state, and any blocker or unresolved semantic ambiguity.

## Authorization

Invoking this command authorizes commit creation for the defined change scope. It does not authorize pushing, merging, tagging, releasing, rewriting published history, or other remote-state mutation.
