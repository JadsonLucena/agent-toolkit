# Agent Toolkit

A vendor-neutral toolkit of **rules, skills, commands, and specialized agents** for the software development pipeline, organized by engineering context.

Canonical definitions stay independent of any IDE, provider, model, issue tracker, or agent runtime. Platform-specific formats are adapters, not sources of truth.

## Architecture

```text
agent-toolkit/
├── contexts/
│   ├── requirements/
│   │   ├── rules/
│   │   ├── skills/
│   │   ├── commands/
│   │   └── agents/
│   ├── testing/
│   │   ├── rules/
│   │   ├── skills/
│   │   ├── commands/
│   │   └── agents/
│   └── git/
│       ├── rules/
│       ├── skills/
│       ├── commands/
│       └── agents/
├── contracts/
├── ARCHITECTURE.md
├── MIGRATION.md
└── README.md
```

Contexts organize the four canonical artifact types by engineering responsibility. Cross-context collaboration uses explicit semantic evidence and contracts rather than accidental dependencies on another context's internal skills or agents.

`contracts/` contains neutral handoff schemas. Contracts are not a fifth artifact type and contain no workflow logic.

## Artifact Responsibilities

1. **Rules** — durable principles, constraints, invariants, and quality standards.
2. **Skills** — reusable operational procedures and task state models.
3. **Commands** — thin engineering-intent and authorization entry points that select a workflow without granting unrelated mutations.
4. **Agents** — specialist scope, evidence discipline, orchestration, boundaries, and handoffs.

See `ARCHITECTURE.md` for the responsibility matrix, dependency rules, command shape, and naming rules. See `MIGRATION.md` for structural renames and moved responsibilities.

## Current Contexts

### Requirements

```text
contexts/requirements/
├── rules/
│   ├── requirements.md
│   └── backlog.md
├── skills/
│   ├── elicitation/skill.md
│   ├── definition/skill.md
│   ├── validation/skill.md
│   └── backlog-planning/skill.md
├── commands/
│   ├── elicit-requirements.md
│   ├── specify-requirements.md
│   ├── validate-requirements.md
│   ├── build-backlog.md
│   └── refine-backlog.md
└── agents/
    ├── requirements-elicitor.md
    ├── requirements-specifier.md
    └── backlog-planner.md
```

Requirements can operate from conversations, documents, interviews, tickets, existing-system evidence, policies, and other supported sources. A repository is not required.

Elicitation and specification share `contracts/requirements.md` so source evidence, decisions, assumptions, conflicts, and traceability survive the transformation without coupling their workflows.

### Testing

```text
contexts/testing/
├── rules/testing.md
├── skills/generate-tests/skill.md
├── commands/generate-tests.md
└── agents/test-engineer.md
```

Testing remains autonomous. Requirements evidence may improve test design through the optional `contracts/test-basis.md`, but Testing does not invoke Requirements skills or agents merely to obtain that evidence.

### Git

```text
contexts/git/
├── rules/
│   ├── git.md
│   ├── gitflow.md
│   ├── semantic-commit.md
│   └── semantic-version.md
├── skills/
│   ├── create-semantic-commits/skill.md
│   ├── determine-semantic-version/skill.md
│   └── manage-branch-work/skill.md
├── commands/
│   ├── commit.md
│   └── determine-semantic-version.md
└── agents/git-engineer.md
```

Git is cross-cutting but is not automatically invoked by other contexts. Planning metadata may provide supporting intent, while repository evidence remains authoritative for repository operations.

## Contracts

* `contracts/requirements.md` — elicitation and requirement-definition semantics.
* `contracts/work-item.md` — planning-item semantics.
* `contracts/test-basis.md` — optional behavioral evidence for Testing.

## Commands

Commands express engineering intent rather than low-level tool aliases:

```text
/requirements/elicit-requirements
/requirements/specify-requirements
/requirements/validate-requirements
/requirements/build-backlog
/requirements/refine-backlog

/testing/generate-tests

/git/commit
/git/determine-semantic-version
```

A command's invocation defines its authorization boundary. For example, determining a semantic version does not authorize version-file mutation, tagging, publishing, or release.

## Development Pipeline

```text
Elicitation ↔ Specification ↔ Backlog / Plan → Design → Implement → Test → Review

Cross-cutting: Git, security, conventions, …
```

The first three stages are iterative. A backlog ambiguity may return to specification, and missing stakeholder intent may return to elicitation.

## Cross-Context Composition

The default integration model is loose coupling by semantic contracts.

A context must not invoke another context's internal agent or skill merely to obtain data. Explicit multi-context workflows may orchestrate multiple specialists when the workflow itself intentionally spans those responsibilities.

Testing and Git remain independently usable when Requirements artifacts are absent.

## Ambiguity Policy

* **Low-impact uncertainty** — state an explicit assumption and continue.
* **Material ambiguity** — ask rather than guess.
* **Blocking missing information** — stop only the affected decision.

Avoid numeric confidence scores that imply unsupported precision.

## Traceability

Preserve identity across transformations when the corresponding artifacts exist:

```text
Stakeholder Need
      │
      ▼
Requirement
      ├────────────► Acceptance Criterion
      ├────────────► Business Rule
      ▼
Work Item
      ▼
Implementation
      ▼
Test Evidence
```

Downstream artifacts may summarize upstream semantics but must not silently change them.

## Model Selection

The toolkit does not require a specific AI provider or model.

The execution environment should select an appropriate model and reasoning effort according to the task. Agents describe the capability they need; model configuration belongs to the platform adapter.

```text
Elicitation / planning → strong reasoning and decomposition
Architecture           → high reasoning
Implementation         → strong coding capability
Testing                → high reasoning and adversarial analysis
Git and release        → high reasoning over repository evidence
Security               → high reasoning and specialized analysis
Code review            → high reasoning and broad context
Simple transformations → lightweight model when sufficient
```

## Context Management

Long-running collaboration should preserve decisions, constraints, assumptions, unresolved issues, and relevant implementation context without forcing every agent to inherit the complete conversation history.

Stable or repeatedly used project information may be cached when the execution platform supports it, but stale cached context must not override newer project state.

## Design Principles

* **Vendor neutral** — canonical definitions do not depend on a specific AI ecosystem.
* **Context first** — artifacts are grouped by engineering responsibility.
* **Single responsibility** — each concept has one authoritative owner.
* **Composable** — explicit workflows may coordinate multiple contexts without merging their responsibilities.
* **Loosely coupled** — cross-context evidence does not create unnecessary workflow dependencies.
* **Traceable** — material semantics preserve provenance across transformations.
* **Evidence driven** — supported evidence precedes inference.
* **Context aware** — preserve relevant context while minimizing unnecessary context.
* **Task oriented** — commands express clear engineering intent.
* **Quality driven** — verification distinguishes evidence from assumptions and unverified conclusions.

## Roadmap

Next contexts should cover architecture and design, implementation, code review, and security without collapsing specialties.

Additional Git commands should be introduced only when a reusable procedure also has a clear user-facing invocation intent and authorization boundary.

## Portability

Canonical definitions are neutral Markdown. Adapters may transform them into provider-specific formats while preserving canonical semantics.

## Goal

The goal is not a collection of prompts. It is a **composable software engineering system for AI agents** where responsibility, evidence, workflow, boundaries, and context are structured to produce consistent engineering outcomes.
