# Architecture

This document defines the canonical structure and responsibility boundaries of Agent Toolkit.

## Canonical Structure

```text
contexts/
├── requirements/
│   ├── rules/
│   │   ├── requirements.md
│   │   └── planning.md
│   ├── skills/
│   │   ├── elicitation/skill.md
│   │   ├── definition/skill.md
│   │   ├── validation/skill.md
│   │   └── planning/skill.md
│   ├── commands/
│   │   ├── elicit.md
│   │   ├── specify.md
│   │   ├── audit.md
│   │   ├── items.md
│   │   └── refinement.md
│   └── agents/
│       ├── requirements-elicitor.md
│       ├── requirements-specifier.md
│       └── backlog-planner.md
├── testing/
│   ├── rules/testing.md
│   ├── skills/generate-tests/skill.md
│   ├── commands/test.md
│   └── agents/test-engineer.md
└── git/
    ├── rules/
    │   ├── git.md
    │   ├── gitflow.md
    │   ├── semantic-commit.md
    │   └── semantic-version.md
    ├── skills/
    │   ├── create-semantic-commits/skill.md
    │   ├── determine-semantic-version/skill.md
    │   └── manage-branch-work/skill.md
    ├── commands/commit.md
    └── agents/git-engineer.md

contracts/
├── requirements.md
├── work-item.md
└── testing.md
```

## Responsibility Model

| Type | Owns | Must not own |
|---|---|---|
| Rule | Durable principles, constraints, invariants, safety and quality standards | Step-by-step workflow, invocation routing, specialist persona |
| Skill | Reusable procedure, operational state, verification loop, task output | Global policy, user entry-point semantics, specialist identity |
| Command | Explicit engineering intent, input selection, authorization boundary, workflow entry point, expected result | Detailed policy or duplicated procedure |
| Agent | Specialist scope, evidence discipline, orchestration, boundaries, handoffs | Detailed reusable task procedure |
| Contract | Neutral handoff semantics and schema meaning | Policy, workflow, orchestration, specialist behavior |

Contracts are supporting schemas, not a fifth canonical artifact type.

## Artifact Matrix

| Context | Artifact | Type | Authoritative responsibility |
|---|---|---|---|
| Requirements | `rules/requirements.md` | Rule | Requirement evidence, ambiguity, quality, acceptance, and traceability invariants |
| Requirements | `rules/planning.md` | Rule | Planning integrity, decomposition, readiness, dependency, and refinement invariants |
| Requirements | `skills/elicitation/skill.md` | Skill | Discover and consolidate supported stakeholder needs and unknowns |
| Requirements | `skills/definition/skill.md` | Skill | Transform supported needs into verifiable requirement definitions |
| Requirements | `skills/validation/skill.md` | Skill | Independently evaluate requirement-definition quality |
| Requirements | `skills/planning/skill.md` | Skill | Transform supported work sources into traceable planning items |
| Requirements | `commands/elicit.md` | Command | Start requirements discovery |
| Requirements | `commands/specify.md` | Command | Start formal requirement definition |
| Requirements | `commands/audit.md` | Command | Start the independent requirement-quality gate |
| Requirements | `commands/items.md` | Command | Produce a structured backlog from supported sources |
| Requirements | `commands/refinement.md` | Command | Refine existing planning items without changing source semantics |
| Requirements | `agents/requirements-elicitor.md` | Agent | Own discovery scope, provenance, clarification, and elicitation handoff |
| Requirements | `agents/requirements-specifier.md` | Agent | Own formal requirement semantics, evidence discipline, and validation routing |
| Requirements | `agents/backlog-planner.md` | Agent | Own planning decomposition, traceability, dependencies, and readiness boundaries |
| Testing | `rules/testing.md` | Rule | Automated-testing standards and quality invariants |
| Testing | `skills/generate-tests/skill.md` | Skill | Test-design, generation, verification, and diagnosis workflow |
| Testing | `commands/test.md` | Command | Start automated-test creation or modification |
| Testing | `agents/test-engineer.md` | Agent | Own testing specialization, evidence discipline, and scope boundaries |
| Git | `rules/git.md` | Rule | Repository-state, history, synchronization, worktree, composition, and remote safety |
| Git | `rules/gitflow.md` | Rule | Gitflow applicability and branch-lifecycle invariants |
| Git | `rules/semantic-commit.md` | Rule | Commit semantics, message structure, and atomicity invariants |
| Git | `rules/semantic-version.md` | Rule | Semantic-version compatibility and increment invariants |
| Git | `skills/create-semantic-commits/skill.md` | Skill | Atomic staging, verification, message derivation, commit creation, and post-check workflow |
| Git | `skills/determine-semantic-version/skill.md` | Skill | Compatibility analysis, version-policy evaluation, and evidence-backed semantic-version recommendation |
| Git | `skills/manage-branch-work/skill.md` | Skill | Branch, synchronization, integration, and worktree decision and verification workflow |
| Git | `commands/commit.md` | Command | Start explicitly requested semantic commit creation |
| Git | `agents/git-engineer.md` | Agent | Own Git specialization, evidence discipline, operation routing, and boundaries |
| Cross-context | `contracts/requirements.md` | Contract | Neutral requirement-definition handoff semantics |
| Cross-context | `contracts/work-item.md` | Contract | Neutral planning-item handoff semantics |
| Cross-context | `contracts/testing.md` | Contract | Optional behavioral evidence handoff for Testing |

## Dependency Direction

Within a context, use this direction:

```text
Command ──► Agent ──► Skill ──► Rule
   │          │          │
   └──────────┴──────────┴──► Contract
```

Additional rules:

* Rules may reference other rules in the same context when one rule set refines another.
* Skills may depend on rules and contracts, but not on commands.
* Agents may depend on rules, skills, and contracts, but not on commands.
* Commands may select agents and skills and reference rules or contracts, but remain thin.
* Commands define the authorization granted by invocation; authorization does not silently expand to adjacent mutations or downstream operations.
* Contracts must not depend on a context implementation.
* A context must not invoke another context's internal agent or skill merely to obtain data.
* Cross-context integration should pass semantic evidence through contracts or explicit inputs.
* Git and Testing must remain independently usable when Requirements artifacts are absent.
* Requirements must remain independently usable when no repository exists.

## State Models

Operational state machines belong in skills when they describe how a reusable task progresses.

Agents may contain a routing state model when it represents specialist-level orchestration rather than a reusable task procedure.

Rules remain authoritative for constraints even when a state graph exists.

Iterative or mutating skills should state explicit stop conditions when continued execution could otherwise require guessing, unsafe mutation, out-of-scope work, or unproductive retries.

## Ambiguity

Use semantic states rather than numeric confidence:

* `sufficient`
* `needs-revision`
* `needs-clarification`
* `blocked`

Ask only when ambiguity can materially change semantics, scope, acceptance, behavior, compatibility, security, or the resulting operation.

## Naming

* Context names are stable engineering nouns: `requirements`, `testing`, `git`.
* Rule filenames name the governed concern.
* Skill directories name the reusable capability.
* Command filenames are concise within their context; the context supplies the namespace.
* Agent filenames name the specialist role.
* Contract filenames name the semantic handoff, not a workflow.

## Accepted Decisions

1. Physical organization is context-first; conceptual ownership remains Rule × Skill × Command × Agent.
2. Requirements is split into Elicitor, Specifier, and Backlog Planner because discovery, formal semantics, and work decomposition have different evidence and failure modes.
3. Testing consumes requirements-derived evidence optionally and never requires Requirements workflows.
4. Git consumes planning intent only as optional evidence and never treats it as stronger than repository state.
5. Detailed atomic commit execution lives in a dedicated skill.
6. Reusable branch/integration/worktree and semantic-version decision procedures live in dedicated skills; they do not require first-class commands until a clear user-facing invocation intent exists.
7. Contracts exist now because Requirements already hands semantics to Planning and Testing. They remain neutral schemas rather than a new artifact category.
8. A generic `shared/` directory is intentionally avoided.

## Deferred Candidates

The following are intentionally not first-class commands yet:

* semantic-version analysis;
* parallel worktree preparation;
* merge/rebase orchestration;
* repository-composition selection.

Promote one to a command only when there is a clear user-facing invocation intent. Reusable internal procedures may remain skills without public command entry points.
