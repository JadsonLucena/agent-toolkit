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
└── README.md
```

Contexts organize the four canonical artifact types by engineering responsibility. Cross-context collaboration uses explicit semantic evidence and contracts rather than dependencies on another context's internal skills or agents.

`contracts/` contains neutral handoff schemas. Contracts are not a fifth artifact type and contain no workflow logic.

## Artifact Responsibilities

1. **Rules** — durable principles, constraints, invariants, and quality standards.
2. **Skills** — reusable operational procedures and task state models.
3. **Commands** — thin engineering-intent entry points that select a workflow.
4. **Agents** — specialist scope, evidence discipline, orchestration, boundaries, and handoffs.

See `ARCHITECTURE.md` for the responsibility matrix and dependency rules.

## Current Contexts

### Requirements

```text
contexts/requirements/
├── rules/
│   ├── requirements.md
│   └── planning.md
├── skills/
│   ├── elicitation/skill.md
│   ├── definition/skill.md
│   ├── validation/skill.md
│   └── planning/skill.md
├── commands/
│   ├── elicit.md
│   ├── specify.md
│   ├── audit.md
│   ├── items.md
│   └── refinement.md
└── agents/
    ├── requirements-elicitor.md
    ├── requirements-specifier.md
    └── backlog-planner.md
```

Requirements can operate from conversations, documents, interviews, tickets, existing-system evidence, policies, and other supported sources. A repository is not required.

### Testing

```text
contexts/testing/
├── rules/testing.md
├── skills/generate-tests/skill.md
├── commands/test.md
└── agents/test-engineer.md
```

Testing remains autonomous. Requirements evidence may improve test design, but it is optional and Testing does not invoke Requirements skills or agents.

### Git

```text
contexts/git/
├── rules/
│   ├── git.md
│   ├── gitflow.md
│   ├── semantic-commit.md
│   └── semantic-version.md
├── skills/create-semantic-commits/skill.md
├── commands/commit.md
└── agents/git-engineer.md
```

Git is cross-cutting but is not automatically invoked by other contexts. Planning metadata may provide supporting intent, while repository evidence remains authoritative for repository operations.

## Contracts

* `contracts/requirements.md` — requirement-definition semantics.
* `contracts/work-item.md` — planning-item semantics.
* `contracts/testing.md` — optional behavioral evidence for Testing.

## Development Pipeline

```text
Elicitation ↔ Specification ↔ Backlog / Plan → Design → Implement → Test → Review

Cross-cutting: Git, security, conventions, …
```

The first three stages are iterative. A planning ambiguity may return to specification, and missing stakeholder intent may return to elicitation.

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

## Design Principles

* **Vendor neutral**
* **Context first**
* **Single responsibility**
* **Composable**
* **Loosely coupled**
* **Traceable**
* **Evidence driven**
* **Task oriented**
* **Quality driven**

## Roadmap

Next contexts should cover architecture and design, implementation, code review, and security without collapsing specialties. Additional Git entry points should be added only when they represent reusable engineering intent.

## Portability

Canonical definitions are neutral Markdown. Adapters may transform them into provider-specific formats while preserving canonical semantics.

## Goal

The goal is not a collection of prompts. It is a **composable software engineering system for AI agents** where responsibility, evidence, workflow, boundaries, and context are structured to produce consistent engineering outcomes.
