# Git Rules

## Core Principles

* Preserve repository integrity, traceability, and recoverability.
* Inspect repository state before performing operations that modify the working tree, index, history, branches, tags, worktrees, or remotes.
* Follow the repository's established branch, merge, rebase, review, signing, and release conventions.
* Prefer explicit, reversible operations over destructive or ambiguous ones.
* Distinguish local state from remote state; never assume remote-tracking references are current without refreshing them when freshness matters.
* Do not infer semantic intent from repository state alone when multiple plausible interpretations remain.

## Repository State

* Before mutating repository state, inspect the current branch, working tree, staged changes, upstream configuration, active Git operation, relevant worktrees, and relevant remote references.
* Do not mix unrelated working-tree or staged changes into the current Git operation.
* Preserve uncommitted work before switching branches, rebasing, resetting, or performing another operation that may affect it.
* Do not discard local changes unless the intent is explicit and the affected state is understood.

## Branch Freshness and Synchronization

* Before starting branch-based work that depends on remote state, fetch the configured upstream remote or remotes and refresh the relevant remote-tracking references.
* If required remote state cannot be fetched, report branch freshness as unverified and do not claim that the branch is current.
* Determine the correct synchronization base and integration target from the branch's role and lifecycle as defined by the repository's workflow; do not assume one base applies to every branch type.
* Immediately before a merge or other integration operation, fetch remote state again and verify that the intended source and target have not changed unexpectedly.
* Refreshing a target branch does not itself require merging or rebasing that target into the source branch; follow the repository's integration policy.
* Treat `origin`, `main`, and `develop` as conventional names only; use the repository's configured remote, production branch, integration branch, and upstream relationships.
* Prefer `fetch` before choosing an integration operation; do not assume an implicit `pull` strategy when merge or rebase policy is unknown.

## Worktrees and Parallel Work

* Use worktrees when independent tasks need concurrent access to different branches or revisions without repeatedly switching branches, stashing changes, or disturbing the main working tree.
* Prefer a dedicated worktree and branch for each parallel task or agent that may modify files, run stateful commands, or create commits.
* Do not allow multiple agents or tasks to modify the same worktree concurrently.
* Keep writable worktrees on distinct branches; do not bypass Git safeguards to check out the same branch in multiple worktrees.
* Before creating a worktree, refresh the relevant remote state and select its base with the same care required for any branch-based work.
* Treat each worktree as working-tree isolation, not repository isolation: refs, objects, and repository-level configuration may still be shared across worktrees.
* Coordinate concurrent operations that mutate shared repository state, such as branch deletion, tag creation, history rewriting, or other ref updates.
* Use a detached worktree for temporary experiments, inspection, or validation when the work does not require a persistent branch.
* Prefer a normal branch switch when only one task is active and parallel isolation provides no meaningful benefit.
* Avoid worktree-based parallelization when tasks are tightly coupled, modify substantially overlapping code, or depend on serialized changes from one another.
* Remove linked worktrees when their task is complete and preserve any required changes before removal.
* Use `git worktree prune` only to clean stale administrative metadata for worktrees that no longer exist.
* Exercise additional caution in repositories using submodules because multiple-worktree support for submodules is incomplete.

## Repository Composition

* Distinguish intra-repository isolation from inter-repository composition: a worktree shares one repository; a fork or submodule relates two repositories.
* Do not create a fork or add a submodule unless the intended relationship to the other repository is explicit.
* Do not clone another repository into a subdirectory of this working tree as a substitute for a composition relationship.
* If the relationship cannot be determined with sufficient confidence, ask the developer rather than choosing a composition mechanism.

### Prefer a Submodule When

* This repository must consume another repository at a pinned commit while keeping histories, remotes, and release cycles separate.
* Updating the consumed repository must be a deliberate commit in this repository, not an implicit fetch of latest history.
* Do not use a submodule to contribute to or diverge from a repository you do not control.
* Do not use a submodule as a substitute for a package-manager dependency, a one-off snapshot, or a branch in the same repository.

### Prefer a Fork When

* The intent is to contribute to or diverge from a repository you do not control, while remaining able to fetch upstream and publish an independent history.
* Treat a fork as a separate repository with its own remotes, protections, and publication state; do not treat it as a branch of the original repository.
* Do not create a fork merely to consume another repository as a pinned dependency.

### Other Composition Mechanisms

* Prefer a package manager when the other project is consumed as a versioned artifact rather than as a Git repository.
* Prefer a vendor copy when a snapshot must live in this tree without a live Git link.
* Prefer subtree only when repository policy already imports foreign history into this tree; do not introduce subtree as a substitute for a fork or submodule without explicit intent.
* Do not replace an existing composition mechanism with another merely to complete the task.

## History Classification

* Treat local or unpublished history as commits and references that have not been made available for collaborators, automation, or consumers to depend upon.
* Treat published or shared history as commits or references that have been pushed or otherwise made available for others to depend upon.
* Local unpublished history may be rewritten when doing so is safe and does not discard required work.
* Treat published or shared history as immutable by default.
* When publication status is uncertain, assume the history may be shared until repository evidence shows otherwise.

## History Safety

* Do not rebase, amend, reset, or otherwise rewrite commits that others may already depend on without explicit intent, sufficient context, and coordination.
* Prefer `revert` for undoing published changes because it preserves history.
* Use `reset` only when its effect on the index, working tree, and reachable commits is understood.
* Use `cherry-pick` only when intentionally copying specific commits across histories; do not use it as a substitute for correcting an unclear branch strategy.
* Use squash only when it improves history without hiding meaningful independent changes required for review, traceability, or rollback.
* Use `reflog` to investigate and recover previous local reference states before assuming local commits are lost.
* Treat reflog as local recovery evidence, not as a remote backup or guarantee that deleted remote history can be recovered.

## Merge and Rebase

* Follow the repository's established integration strategy; do not impose merge, rebase, squash, or fast-forward policies universally.
* Choose between merge and rebase based on history ownership, publication state, branch lifecycle, and whether branch topology carries useful information.

### Prefer Rebase When

* The commits are local or otherwise unpublished and rewriting them cannot disrupt collaborators, automation, or consumers.
* A topic or feature branch needs to be replayed onto its current base before integration and the repository prefers a linear history.
* Cleaning, reordering, combining, or otherwise preparing your own unpublished commits improves the history before publication.
* The integration policy expects the topic branch to apply cleanly on the target and then be integrated by fast-forward.
* Do not rebase merely because another branch has advanced; first determine whether the current branch lifecycle should actually incorporate that branch.

### Prefer Merge When

* The commits are already published or shared and rewriting them could invalidate references or disrupt collaborators.
* Preserving the actual branch topology, integration boundary, or parallel development history is valuable.
* Integrating long-lived or lifecycle-significant branches such as release or hotfix lines where the merge relationship itself provides useful history.
* The repository intentionally records integration events with merge commits.
* Rewriting the source history would provide little benefit relative to the coordination or conflict-resolution cost.

### Fast-Forward Policy

* When the target is an ancestor of the source, a fast-forward can integrate the change without creating a merge commit.
* Prefer fast-forward when a linear history is desired and no explicit integration event needs to be recorded.
* Use a merge commit, including `--no-ff` when repository policy requires it, when preserving the branch integration event is meaningful.
* Use `--ff-only` when the operation must fail rather than silently create a merge commit after unexpected divergence.

### Safety and Verification

* Never rebase shared or published history by default; rewrite it only when explicitly authorized and coordinated.
* A rebase creates new commits by replaying changes onto another base; verify the rewritten history before publication.
* A merge preserves both lines of ancestry and may create a merge commit when histories have diverged.
* Do not use squash as a synonym for rebase or merge: squashing collapses changes and may intentionally discard intermediate commit topology.
* Never resolve conflicts by blindly accepting one side; preserve the intended behavior represented by both relevant histories.
* Review the resulting diff and history after merge, rebase, squash, or conflict resolution before continuing.
* Rerun relevant tests and quality gates after reconciliation, integration, conflict resolution, or history rewriting when the resulting changes can affect behavior.

## Remote Operations

* Verify the destination remote, ref, upstream relationship, and intended update before pushing.
* Do not use an unconditional force push to rewrite shared or published history.
* Rewrite a published remote ref only when the rewrite is explicitly authorized, repository policy permits it, and the expected remote state has been established.
* Before an authorized force update, refresh or otherwise inspect the remote ref and determine the exact remote state that the update is allowed to replace.
* Prefer an explicit lease such as `--force-with-lease=<ref>:<expected>` when the expected remote object can be established.
* If the expected remote state cannot be established with sufficient confidence, stop instead of forcing the update.
* Treat plain `--force-with-lease` as weaker than an explicit expected-value lease because its safety depends on remote-tracking state.
* Never replace a rejected guarded force update with unconditional `--force` merely to complete the push.
* Do not delete remote branches or tags without confirming the intended target and that deletion is authorized.
* Do not claim a push succeeded until the relevant remote state provides evidence of publication.

## Tags and Release Integrity

* Treat published release tags as immutable references to released history.
* A release tag must point to the exact commit intended for that release.
* Follow repository conventions for tag naming, including any prefix applied to the version identifier.
* Prefer annotated tags for releases when the repository has no conflicting convention.
* Reserve lightweight tags primarily for private, temporary, or non-release labels unless project convention explicitly uses them differently.
* When release authenticity is required, create a signed release tag and verify its signature before publication.
* Treat commit signing and tag signing as distinct authenticity mechanisms and follow repository policy for each.
* If required signing material or verification infrastructure is unavailable, report the blocker; do not silently disable the signing requirement.
* Do not move, replace, or reuse a published release tag for different content.
* If released content must change, publish it as a new release under a new tag rather than mutating the previous release tag.
* Before creating or publishing a release tag, verify the version, target commit, tag name, relevant metadata, and whether the tag already exists locally or remotely.
* Do not claim a release exists merely because a local tag exists; distinguish tagged, pushed, published, deployed, and released states.
* When a release operation must update multiple remote refs together and the remote supports atomic pushes, consider an atomic push when repository policy benefits from all-or-nothing publication.

## Conflict and Failure Handling

* Surface merge conflicts, divergent history, rejected pushes, missing upstreams, unavailable remotes, and ambiguous repository state instead of hiding or bypassing them.
* Diagnose repository state before retrying a failed Git operation.
* Abort or stop an in-progress merge, rebase, or cherry-pick when continuing would require guessing at intended history or behavior.
* Do not bypass hooks, branch protections, required checks, signing requirements, or review policies merely to complete an operation.

## Quality Guardrails

* Every history-changing operation must have a clear intent and understood effect.
* Keep Git operations scoped to the authorized change; do not include unrelated cleanup or repository restructuring.
* Verify the resulting working tree, staged state, branch, history, tag, worktree, and remote state relevant to the operation before declaring success.
* Do not infer that a branch is current, a push succeeded, a merge completed, a worktree is safe to remove, or a tag was published without evidence from the corresponding Git state.
* Prefer recoverable failure over destructive success.
