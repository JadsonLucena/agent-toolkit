# Resolve Conflicts

## Intent

Diagnose and, when separately authorized, resolve Git merge/rebase/cherry-pick interference with evidence-backed preservation of integrated behavior.

## Invocation

Default to read-only `diagnose` mode. `apply` mode requires explicit authorization for selected conflicted or directly affected files. Staging resolved files requires distinct permission. Non-destructive checks run only when allowed by repository/runtime policy. Diagnosing or applying never authorizes continuing an active Git operation.

## Uses

* Agent: `contexts/git/agents/git-engineer.md`
* Skill: `contexts/git/skills/resolve-merge-conflicts/SKILL.md`
* Rule: `contexts/git/rules/git.md`
* Rule: `contexts/git/rules/gitflow.md` when applicable
* Optional contract: `contracts/requirements.md`
* Optional contract: `contracts/test-basis.md`
* Optional contract: `contracts/test-evidence.md`

## Inputs

* Current integration operation or specified comparison refs and repository state.
* Optional selected paths, Change Boundary, requirement/decision references, and test evidence.
* Requested `diagnose` or `apply` scope; explicit independent approval for staging or operation continuation if wanted.

## Output

Three-way provenance and intent analysis; interaction and invariant risks; semantic resolution decision or `decision-needed`; applied path inventory if authorized; verification results tied to exact snapshot; remaining permissions, limitations and next steps.

## Boundary

Read-only by default. Do not edit or stage without explicit scoped permission. Never infer authority from the labels `ours` or `theirs`. This command does not authorize starting/continuing integration, committing, pushing, merging PRs, rewriting shared history, deleting refs, releasing or deploying. Escalate material uncertainty rather than guessing.

