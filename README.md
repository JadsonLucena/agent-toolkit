# Agent Toolkit

A vendor-neutral toolkit of **rules, skills, commands, and specialized agents** for the software development pipeline—from elicitation through code review—including cross-cutting concerns such as version control.

Canonical definitions stay independent of any IDE, provider, or model. Platform-specific formats are adapters, not sources of truth.

## Purpose

Cover the full development cycle with composable artifacts:

1. **Rules** — persistent standards that must be respected.
2. **Skills** — reusable procedures for a specific kind of task.
3. **Commands** — explicit entry points that start a workflow.
4. **Agents** — specialized roles that apply the relevant rules, skills, and commands.

Agents stay specialized. Cross-cutting concerns (for example Git, security, or conventions) are first-class, not hidden inside a general-purpose prompt.

## Current inventory

What this repository already defines:

```text
rules/
├── testing.md
├── git.md
├── gitflow.md
├── semantic-commit.md
└── semantic-version.md

skills/
└── generate-tests/

agents/
├── test-engineer.md
└── git-engineer.md
```

| Area | Status | Artifacts |
|---|---|---|
| Automated testing | Available | `rules/testing.md`, `skills/generate-tests/`, `agents/test-engineer.md` |
| Git, history, and release semantics | Available | `rules/git.md`, `rules/gitflow.md`, `rules/semantic-commit.md`, `rules/semantic-version.md`, `agents/git-engineer.md` |
| Commands | Not started | no `commands/` definitions yet |
| Elicitation through implementation | Roadmap | no planner, architect, or implementation agent yet |
| Code review | Roadmap | no reviewer agent or review skill yet |

`gitflow.md` applies only when the repository uses Gitflow or the task explicitly requires it.

## Architecture

```text
agent-toolkit/
├── rules/
├── skills/
├── commands/    # planned
├── agents/
└── README.md
```

### Rules

Persistent principles, constraints, quality standards, and expected behavior.

> **What standards must be respected?**

Rules stay concise, reusable, and independent of a specific workflow or tool.

### Skills

Reusable knowledge and procedures for one type of task.

> **How should this task be performed?**

Multiple agents may reuse the same skill when it matches their responsibility.

### Commands

Named entry points that start a pipeline stage or a cross-cutting workflow.

> **When should this workflow be invoked, and with what goal?**

Commands compose agents, rules, and skills. They do not replace them. None are defined yet.

### Agents

Specialized engineering roles that orchestrate the rules, skills, and commands needed for a goal.

> **Who should perform this task, and which capabilities should be applied?**

Each agent has a clear scope and uses only the artifacts relevant to its specialty.

## Development pipeline

Prefer specialized agents over a single general-purpose agent.

```text
Elicitation → Plan → Design → Implement → Test → Review
                      │
                      └── Cross-cutting: Git, security, conventions, …
```

| Stage | Responsibility | Status |
|---|---|---|
| Elicitation | Problem, stakeholders, constraints, and desired outcomes | Roadmap |
| Plan | Requirements, decomposition, risks, dependencies, and execution strategy | Roadmap |
| Design | Architecture, boundaries, contracts, and trade-offs | Roadmap |
| Implement | Application code within the agreed design and quality rules | Roadmap |
| Test | Test strategy, automated tests, edge cases, and verification | Available |
| Review | Correctness, quality, architecture, security, debt, and maintainability | Roadmap |

| Cross-cutting | Responsibility | Status |
|---|---|---|
| Git and release | Safe history, commits, branches, composition, versions, and publication | Available |
| Security | Threats, authorization, secrets, and sensitive data | Roadmap |
| Conventions | Shared coding, architecture, and documentation standards | Roadmap |

Agents may collaborate. Responsibilities stay explicit so work is not duplicated and decisions do not conflict.

A typical collaboration still flows left to right through the pipeline. Git is not a late stage: it applies whenever repository state, history, or release intent changes.

```text
Request
   │
   ▼
Elicitation / Planner          (roadmap)
   │
   ▼
Designer / Implementer         (roadmap)
   │
   ├── Test Engineer           (available)
   └── Git Engineer            (available, cross-cutting)
   │
   ▼
Reviewer                       (roadmap)
```

Relevant context and decisions should flow between agents without forcing every agent to inherit the complete conversation history.

## Roadmap

The next definitions should fill the pipeline and the missing artifact type, without collapsing specialties into one agent.

**Commands**

- Entry points for elicitation, planning, implementation, testing, review, and Git operations.

**Pipeline agents and supporting artifacts**

- Elicitation and planning (requirements, decomposition, risks).
- Architecture and design (including API and system-design skills).
- Implementation (software engineer, plus quality rules such as architecture and clean code).
- Code review (reviewer agent and review skill).

**Additional cross-cutting concerns**

- Security (rule, threat-modeling skill, security engineer).
- Shared conventions that remain independent of a single pipeline stage.

New artifacts should follow the same vendor-neutral Markdown shape as the existing testing and Git definitions.

## Model selection

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

## Context management

Efficient context management matters when multiple agents collaborate.

### Conversation compaction

Periodically summarize or compact long-running conversations while preserving decisions, constraints, assumptions, unresolved issues, and relevant implementation context.

### Shared context

Agents on the same task should share project and decision context instead of rebuilding it independently. Each agent consumes only the subset relevant to its responsibility.

### Context caching

Stable or repeatedly used information—conventions, architecture docs, rules, common skills, domain terms—should be cached when the platform supports it, without letting stale cache override newer project state.

## Design principles

- **Vendor neutral** — source definitions must not depend on a specific IDE, AI provider, or model.
- **Full pipeline** — artifacts should cover elicitation through review, plus cross-cutting concerns.
- **Single responsibility** — rules, skills, commands, and agents must have clearly separated concerns.
- **Composable** — agents combine only the artifacts they need.
- **Reusable** — knowledge is defined once and shared.
- **Context aware** — preserve relevant context while minimizing unnecessary tokens.
- **Task oriented** — use specialized agents and appropriate models for the work.
- **Quality driven** — optimize for correctness, security, maintainability, performance, and meaningful engineering outcomes.

## Portability

Canonical definitions are written in neutral Markdown.

```text
rules / skills / commands / agents
              │
              ▼
      Canonical Markdown
              │
      ┌───────┼─────────┐
      ▼       ▼         ▼
   Cursor  Copilot   Claude
      ▼       ▼         ▼
      Other AI platforms
```

This allows the toolkit to evolve independently from any individual AI ecosystem.

## Goal

The goal is not a collection of prompts.

It is a **composable software engineering system for AI agents**, covering the development pipeline and its cross-cutting concerns, where responsibilities, knowledge, reasoning, and context are structured to produce consistent engineering outcomes.
