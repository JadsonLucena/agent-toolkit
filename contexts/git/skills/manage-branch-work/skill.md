# Manage Branch Work

## Purpose

Use for authorized branch, synchronization, integration, or worktree operations when repository policy and verified branch intent determine the safe procedure.

## Uses

* Rule: `contexts/git/rules/git.md`
* Rule: `contexts/git/rules/gitflow.md` only when Gitflow applies.

## Working State

Maintain:

* current branch and verified branch role;
* upstream and relevant remote references;
* publication state and shared-history constraints;
* active merge, rebase, cherry-pick, bisect, or conflict state;
* applicable repository workflow and integration policy;
* worktree occupancy and parallel-work constraints;
* explicit authorization scope;
* verification evidence and unresolved ambiguity.

## Workflow

1. Inspect repository state, branch role, upstreams, worktrees, active Git operations, and relevant remote references.
2. Refresh remote state when freshness materially affects synchronization, integration, or publication decisions.
3. Determine the branch lifecycle and correct base or target from repository policy and explicit intent rather than branch-name assumptions.
4. If branch role, base, target, publication state, or intended integration semantics are materially ambiguous, ask the developer.
5. Choose merge, rebase, fast-forward, worktree preparation, or another repository-supported strategy according to publication state, topology, repository policy, and explicit authorization.
6. Protect unrelated work, shared history, occupied worktrees, and remote state outside the authorized scope.
7. Execute only the specifically authorized mutation.
8. Inspect resulting history, working-tree state, worktrees, upstream relationships, and required verification.
9. Report verified state without implying push, merge, publication, release, or cleanup that did not occur.

## Parallel Work

Use dedicated worktrees only when tasks are sufficiently independent. Serialize tightly coupled or substantially overlapping work. A worktree isolates a working tree and index, not repository-level refs, objects, or all shared operations.

## Stop Conditions

Stop and surface the issue when:

* branch role, integration target, or publication state remains materially ambiguous;
* the safe operation would require authorization for an additional mutation;
* a conflict or active Git operation cannot be resolved within the authorized scope;
* required remote freshness, repository policy, signing, or verification evidence is unavailable;
* the operation would rewrite shared history, discard unrelated work, or mutate an unapproved remote ref;
* repeated conflict-resolution or verification attempts are not making meaningful progress.

## Output

Report the operation performed, relevant before/after refs or branch state, verification evidence, remaining work, and any blocked or unresolved condition.

## Boundary

Branch-work authorization does not imply permission to push, delete remote refs, rewrite published history, tag, publish, deploy, or release unless separately authorized.
