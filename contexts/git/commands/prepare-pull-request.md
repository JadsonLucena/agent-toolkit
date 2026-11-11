# Prepare Pull Request

## Intent

Inspect an implemented change and prepare a truthful, reviewable pull request title, description, scope assessment, verification summary, and readiness state.

## Invocation

Use when a branch or diff is intended for review and needs to be reconciled with its objective, repository conventions, PR template, tests/evidence, and reviewability constraints.

Invocation authorizes read-only repository inspection and non-destructive project verification when available, including discovery of effective hooks/CI, execution of missing authorized lint/tests and established coverage checks, and reconciliation of independent code-review evidence. It does not authorize remote PR creation or modification. Preparation may report missing evidence, but no remote PR may be created until all applicable pre-creation checks pass.

## Uses

* Agent: `contexts/git/agents/git-engineer.md`
* Skill: `contexts/git/skills/manage-pull-request/SKILL.md` in `prepare` mode
* Rule: `contexts/git/rules/pull-request.md`
* Rule: `contexts/git/rules/git.md`
* Rule: `contexts/git/rules/gitflow.md` when applicable
* Optional contract: `contracts/work-item.md`
* Optional contract: `contracts/test-basis.md`
* Optional review evidence contract: `contracts/review-evidence.md`
* Optional contract: `contracts/test-evidence.md`

## Inputs

* Current or explicitly identified head branch/diff.
* Intended base or repository workflow evidence from which it can be determined.
* Optional PR Boundary or prior PR plan.
* Optional requirement, rule, use case, scenario, work item, defect, or slice references.
* Optional independent code-review evidence and identity/coverage for the intended change.
* Optional completed test/verification evidence, effective hook and CI information, and corresponding code revision/scope.

## Output

A PR preparation result containing:

* readiness: `ready`, `draft`, or `blocked`;
* reconciled PR Boundary;
* scope drift, accidental-change, complexity, and decomposition findings;
* the applicable repository PR template source, or explicit fallback decision;
* proposed PR title;
* complete PR description based on the final diff;
* observed independent Code Review status/coverage/identity and applicable tests/lint evidence;
* effective hooks/CI evidence, required checks discovered, and explicitly executed missing checks;
* observed tests/checks and their results;
* unexecuted, failed, or blocked verification;
* material impacts, risks, dependencies, and remaining work.

## Boundary

This command does not authorize modifying production/test code, staging, committing, pushing, rewriting history, creating/updating a remote PR, assigning reviewers, applying labels, enabling auto-merge, merging, closing, deleting branches, releasing, or deploying.

A preparation finding may recommend implementation or decomposition changes, but the command must not perform them without separate authorization.

Do not claim that a task, Product Slice, story, deployment, or release is complete merely because the PR is prepared or ready for review.
