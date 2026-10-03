# Migration

## Structural Change

The repository moved from artifact-type-first top-level folders to context-first ownership:

* Git rules and the Git Engineer moved under `contexts/git/`.
* Testing rules, skills, and the Test Engineer moved under `contexts/testing/`.
* Requirements engineering and backlog planning are owned by `contexts/requirements/`.
* `contracts/` contains neutral semantic handoffs and is not a fifth canonical artifact type.

## Moved Responsibility

* Detailed atomic commit execution moved from `git-engineer.md` to `contexts/git/skills/create-semantic-commits/skill.md`.
* Semantic-version decision procedure lives in `contexts/git/skills/determine-semantic-version/skill.md`.
* Branch, synchronization, integration, and worktree procedure lives in `contexts/git/skills/manage-branch-work/skill.md`.
* `git-engineer.md` owns Git specialization, evidence discipline, routing, authorization boundaries, and handoffs.
* Testing consumes `contracts/test-basis.md` only as optional evidence and remains independent from Requirements agents and skills.

## Naming Migration

The following names were made more explicit so commands express engineering intent and backlog artifacts own a narrower concern:

* `contexts/requirements/rules/planning.md` → `contexts/requirements/rules/backlog.md`
* `contexts/requirements/skills/planning/skill.md` → `contexts/requirements/skills/backlog-planning/skill.md`
* `contexts/requirements/commands/elicit.md` → `elicit-requirements.md`
* `contexts/requirements/commands/specify.md` → `specify-requirements.md`
* `contexts/requirements/commands/audit.md` → `validate-requirements.md`
* `contexts/requirements/commands/items.md` → `build-backlog.md`
* `contexts/requirements/commands/refinement.md` → `refine-backlog.md`
* `contexts/testing/commands/test.md` → `generate-tests.md`
* `contracts/testing.md` → `contracts/test-basis.md`

## Preserved Semantics

* Existing Git, Gitflow, semantic-commit, semantic-version, and testing rules remain authoritative.
* Requirements remains usable without a repository.
* Testing remains usable without Requirements artifacts.
* Git remains usable without Requirements or Testing.
* Cross-context evidence may support decisions but does not silently become authoritative intent.
* Material semantic ambiguity must be surfaced rather than guessed.

## Intentional Consolidation

* Backlog creation and refinement use one backlog-planning skill with explicit `build` and `refine` modes.
* Requirement and work-item semantics remain separate contracts.
* Elicitation and specification use the same Requirements contract to preserve semantic continuity without introducing a workflow-specific mega-contract.
* Cross-context data shapes remain contracts rather than generic shared rules.

## Methodology Hardening

The context-first migration was also hardened against later requirements-review findings:

* `requirements/rules/tailoring.md` makes rigor proportional to risk and uncertainty instead of document count.
* Elicitation now separates Need, Business Goal, success evidence, Current/Future State, Work Scope, Product Boundary, and candidate solutions when those concerns are material.
* Requirements semantics now cover conditional data, quality, security, transition, scenario, rationale, and rule-governance concerns without making every concern mandatory.
* `example-discovery/skill.md` owns stable behavioral Scenario Sets plus domain examples, counterexamples, boundaries, and questions before test automation.
* `contracts/test-basis.md` preserves portable scenario identity into Testing, while `contracts/test-evidence.md` records scenario-to-test coverage and verification without mutating upstream semantics.
* Backlog planning now supports coherent vertical/use-case/journey slicing, explicit learning work, trim-the-tail candidates, and critical guarantees.
* Validation is read-only and evaluates missing knowledge, cross-artifact consistency, severity, and risk-proportional readiness.
* Test generation may diagnose production defects but may not modify production artifacts without separate authorization.
* Commit verification may diagnose failures but may not edit the authorized implementation merely to make a commit pass.

## Intentional Deletions

Former top-level `rules/`, `skills/`, and `agents/` copies were removed after migration to avoid duplicate canonical sources.

Detailed procedures removed from agents are not semantic losses when their durable constraints remain in rules or their reusable workflow moved into a skill.

No vendor-specific adapter files are introduced by this migration.
