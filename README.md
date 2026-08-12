# Agent Toolkit

A vendor-neutral toolkit for organizing **AI rules, skills, and specialized agents** for software engineering workflows.

The project provides a reusable foundation for coordinating AI agents by responsibility, knowledge domain, reasoning needs, and shared context—without coupling the source definitions to a specific IDE, provider, or model.

## Purpose

The toolkit is built around four principles:

1. **Specialized agents** for distinct software engineering responsibilities.
2. **Reusable skills** that encapsulate knowledge and procedures shared across agents.
3. **Task-aware model selection** so each activity can use an appropriate AI model and reasoning effort.
4. **Context management** to reduce duplication, preserve relevant knowledge, and coordinate multiple agents efficiently.

## Architecture

```text
agent-toolkit/
├── rules/
├── skills/
├── agents/
└── README.md
```

### Rules

Rules define persistent principles, constraints, quality standards, and expected behavior.

They answer:

> **What standards must be respected?**

Examples:

```text
rules/
├── testing.md
├── architecture.md
├── security.md
└── clean-code.md
```

Rules should remain concise, reusable, and independent of specific workflows or tools.

### Skills

Skills encapsulate reusable knowledge and procedures for accomplishing a specific type of task.

They answer:

> **How should this task be performed?**

Examples:

```text
skills/
├── generate-tests/
├── design-api/
├── threat-modeling/
├── performance-analysis/
└── code-review/
```

Multiple agents may reuse the same skill whenever it is relevant to their responsibility.

### Agents

Agents represent specialized engineering roles and orchestrate the rules and skills required to accomplish their goals.

They answer:

> **Who should perform this task, and which capabilities should be applied?**

Examples:

```text
agents/
├── planner.md
├── software-architect.md
├── software-engineer.md
├── test-engineer.md
├── security-engineer.md
└── code-reviewer.md
```

Each agent should have a clear scope and use only the rules and skills relevant to its specialty.

## Agent Specialization

Prefer specialized agents over a single general-purpose agent.

A software engineering workflow may involve agents responsible for:

- **Plan** — requirements, decomposition, risks, dependencies, and execution strategy.
- **Develop** — architecture, design, patterns, quality, security, performance, and implementation.
- **Test** — test strategy, automated testing, edge cases, failure behavior, and quality validation.
- **Review** — correctness, code quality, architecture, security, technical debt, performance, and maintainability.

Agents may collaborate, but responsibilities should remain explicit to avoid duplicated work and conflicting decisions.

## Model Selection

The toolkit does not require a specific AI provider or model.

The execution environment should select an appropriate model and reasoning effort according to the task.

For example:

```text
Planning             → strong reasoning and decomposition
Architecture         → high reasoning
Implementation       → strong coding capability
Testing              → high reasoning and adversarial analysis
Security             → high reasoning and specialized analysis
Code Review          → high reasoning and broad context
Simple transformations → lightweight model when sufficient
```

Model configuration belongs to the execution environment or platform adapter, while agents describe the capability they require.

This keeps the toolkit portable across different AI providers and future model generations.

## Context Management

Efficient context management is a core concern when multiple agents collaborate.

The toolkit should favor:

### Conversation Compaction

Periodically summarize or compact long-running conversations while preserving:

- decisions;
- constraints;
- assumptions;
- unresolved issues;
- relevant implementation context.

Historical detail that no longer affects the task should not consume active context unnecessarily.

### Shared Context

Agents working on the same task should share the relevant project and decision context instead of rebuilding it independently.

Shared context may include:

- requirements;
- architectural decisions;
- domain constraints;
- implementation decisions;
- discovered risks;
- test strategy;
- review findings.

Each agent should consume only the subset relevant to its responsibility.

### Context Caching

Stable or repeatedly used information should be cached when the execution platform supports it.

Examples include:

- project conventions;
- architecture documentation;
- rules;
- commonly used skills;
- dependency information;
- domain terminology.

Caching should reduce repeated context processing without allowing stale information to override newer project state.

## Execution Model

A typical workflow may look like:

```text
Request
   │
   ▼
Planner
   │
   ├── requirements
   ├── risks
   └── execution plan
   │
   ▼
Developer / Architect
   │
   ├── architecture rules
   ├── design skills
   ├── security skills
   └── implementation
   │
   ▼
Test Engineer
   │
   ├── testing rules
   └── testing skills
   │
   ▼
Reviewer
   │
   ├── correctness
   ├── quality
   ├── security
   ├── technical debt
   ├── performance
   └── maintainability
```

Relevant context and decisions should flow between agents without forcing every agent to inherit the complete conversation history.

## Design Principles

- **Vendor neutral** — source definitions must not depend on a specific IDE, AI provider, or model.
- **Single responsibility** — rules, skills, and agents must have clearly separated concerns.
- **Composable** — agents combine only the rules and skills they need.
- **Reusable** — knowledge should be defined once and shared across agents.
- **Context aware** — preserve relevant context while minimizing unnecessary tokens.
- **Task oriented** — use specialized agents and appropriate models according to the work being performed.
- **Quality driven** — optimize for correctness, security, maintainability, performance, and meaningful engineering outcomes.

## Portability

Canonical definitions are written in neutral Markdown.

Platform-specific formats should be treated as adapters rather than sources of truth.

```text
rules / skills / agents
         │
         ▼
   Canonical Markdown
         │
   ┌─────┼─────────┐
   ▼     ▼         ▼
 Cursor  Copilot  Claude
   ▼     ▼         ▼
 Other AI platforms
```

This allows the toolkit to evolve independently from any individual AI ecosystem.

## Goal

The goal is not to create a collection of prompts.

It is to build a **composable software engineering system for AI agents**, where responsibilities, knowledge, reasoning, and context are intentionally structured to produce consistent and high-quality engineering outcomes.