# Agent Toolkit

A vendor-neutral toolkit of canonical Markdown artifacts for AI-assisted software engineering.

The toolkit is organized by engineering context. Each context owns four distinct artifact types:

1. **Rules** — durable principles, constraints, invariants, and quality/safety semantics.
2. **Skills** — reusable operational workflows and stateful procedures.
3. **Commands** — explicit engineering-intent entry points and authorization boundaries.
4. **Agents** — specialized roles that apply rules, route work to skills, and manage handoffs.

Neutral **contracts** define data shapes between workflow stages or contexts without becoming a shared behavior layer.

## Current Structure

```text
agent-toolkit/
├── contexts/
│   ├── requirements/
│   │   ├── rules/
│   │   │   ├── requirements.md
│   │   │   └── backlog.md
│   │   ├── skills/
│   │   │   ├── elicit-requirements.md
│   │   │   ├── specify-requirements.md
│   │   │   ├── validate-requirements.md
│   │   │   └── build-backlog.md
│   │   ├── commands/
│   │   │   ├── elicit-requirements.md
│   │   │   ├── specify-requirements.md
│   │   │   ├── validate-requirements.md
│   │   │   ├── build-backlog.md
│   │   │   └── refine-backlog.md
│   │   └── agents/
│   │       ├── requirements-analyst.md
│   │       ├── requirements-specifier.md
│   │       └── backlog-planner.md
│   ├── testing/
│   │   ├── rules/testing.md
│   │   ├── skills/generate-tests.md
│   │   ├── commands/generate-tests.md
│   │   └── agents/test-engineer.md
│   └── git/
│       ├── rules/
│       │   ├── git.md
│       │   ├── gitflow.md
│       │   ├── semantic-commit.md
│       │   └── semantic-version.md
│       ├── skills/
│       │   ├── commit-changes.md
│       │   ├── determine-semantic-version.md
│       │   └── manage-branch-work.md
│       ├── commands/
│       │   ├── commit-changes.md
│       │   └── determine-semantic-version.md
│       └── agents/git-engineer.md
├── contracts/
│   ├── requirements-workflow.md
│   └── test-basis.md
├── ARCHITECTURE.md
├── MIGRATION.md
├── LICENSE
└── README.md
```

## End-to-End Requirements Flow

```text
Evidence / stakeholder context
        │
        ▼
Elicit requirements
        │
        ▼
Requirements handoff
        │
        ▼
Specify requirements
        │
        ▼
Validate requirements
        │
        ├── material ambiguity ──► stakeholder/developer clarification
        │
        ▼
Build / refine backlog
        │
        ▼
Traceable delivery work
        │
        ├── optional test basis ──► Testing
        └── optional intent evidence ──► Git
```

Requirements does not become a mandatory dependency for Testing or Git. Both contexts can operate from repository evidence and explicit developer intent when requirements artifacts are absent.

## Core Design Principles

* **Evidence before inference** — never invent material semantic intent to keep a workflow moving.
* **Single responsibility** — each concept has one authoritative owner.
* **No procedural duplication** — reusable workflows belong in skills; agents orchestrate them.
* **Explicit entry points** — commands express engineering intent and authorization, not low-level CLI aliases.
* **Independent contexts** — cross-context evidence is optional unless an explicit composed workflow says otherwise.
* **Traceable handoffs** — stable identifiers and provenance connect requirements, backlog, tests, and implementation evidence.
* **Vendor neutral** — canonical artifacts do not depend on a specific IDE, model, provider, tracker, or hosting platform.
* **Semantic uncertainty is not failure** — clarification is a first-class workflow state; technical inability is a blocker.

See `ARCHITECTURE.md` for the responsibility matrix and dependency rules and `MIGRATION.md` for the structural changes from the previous layout.
