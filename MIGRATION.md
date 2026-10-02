# Migration

## Structural Change

The repository moved from artifact-type-first top-level folders to context-first ownership:

* `rules/git*.md`, `rules/semantic-*.md`, and `agents/git-engineer.md` moved under `contexts/git/`.
* `rules/testing.md`, `skills/generate-tests/skill.md`, and `agents/test-engineer.md` moved under `contexts/testing/`.
* The new Requirements context owns requirements and backlog artifacts under `contexts/requirements/`.
* `contracts/` was added only for neutral cross-stage or cross-context handoff schemas.

## Moved Responsibility

* Detailed commit execution moved from `git-engineer.md` to `contexts/git/skills/commit-changes.md`.
* Semantic-version decision procedure moved to `contexts/git/skills/determine-semantic-version.md`.
* Branch/integration procedural orchestration moved to `contexts/git/skills/manage-branch-work.md`.
* `git-engineer.md` now owns specialist scope, evidence discipline, routing, and authorization boundaries.
* Testing gained optional consumption of `contracts/test-basis.md` without a dependency on Requirements agents or skills.

## Preserved Semantics

* Existing Git, Gitflow, Conventional Commit, Semantic Versioning, and testing rules were moved without intentionally weakening their safety or quality semantics.
* Testing remains independently invocable through an explicit generate-tests command.
* Git remains independently usable without Requirements.
* Existing ambiguity discipline is preserved: when evidence cannot establish material semantic intent, ask the developer rather than guess.

## Intentional Consolidation

* Backlog creation and refinement use one skill with explicit modes because both operate on the same decomposition and traceability semantics.
* Traceability rules are owned by the Requirements and Backlog rules rather than duplicated in a separate behavioral rule file.
* Cross-context data shapes are contracts, not generic shared rules.

## Intentional Deletions

The former top-level `rules/`, `skills/`, and `agents/` copies are removed after migration to avoid duplicate canonical sources. No vendor-specific adapter files are introduced.
