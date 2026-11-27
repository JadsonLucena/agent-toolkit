# Agent Toolkit

**Engineering discipline for AI-assisted software development.**

AI coding agents can generate code, but reviewable software changes also require coherent requirements, explicit design decisions, meaningful verification, and controlled delivery. Agent Toolkit brings established software engineering practices to AI-assisted work, helping developers and teams move from change requests to reviewable increments.

It provides vendor-neutral, reusable guidance spanning requirements, design, implementation, testing, review, delivery preparation, and Git. Its Rules, Skills, Commands, specialist Agents, and shared Contracts clarify responsibilities, preserve decisions and evidence across handoffs, and support verification proportionate to risk.

**The goal is not simply to generate more code, but to make AI-assisted engineering more disciplined, transparent, and reviewable.**

The toolkit is a collection of portable, version-controlled Markdown artifacts, **not a standalone executable agent or an automatically installed CLI**. Agent runtimes can discover or integrate the relevant artifacts; optional adapters support specific environments. Guidance alone does not prove agent behavior or enforce permissions; execution and safeguards depend on the host runtime.

## What it covers

| Context | Purpose |
| --- | --- |
| [Requirements](contexts/requirements/) | Discover needs, specify and validate requirements, and plan a backlog. |
| [Design](contexts/design/) | Define technical decisions for a bounded implementation slice. |
| [Debugging](contexts/debugging/) | Investigate observed technical defects without applying changes; provide reusable causal evidence. |
| [Implementation](contexts/implementation/) | Implement and verify an authorized increment. |
| [Delivery](contexts/delivery/) | Coordinate authorized changes from Requirements through reviewable PRs. |
| [Testing](contexts/testing/) | Design, generate, and verify automated tests with traceable evidence. |
| [Review](contexts/review/) | Assess code changes and risks, verify findings, and distinguish advisory review from independently attested gates. |
| [Git](contexts/git/) | Manage repository changes, semantic commits, branches, and pull requests. |

Within each context, **Rules** define durable constraints; **Skills** describe reusable procedures; **Commands** provide explicit invocation entry points; and **Agents** describe specialist roles. Shared [Contracts](contracts/) carry evidence between contexts without forcing them to depend on each other's internal workflows.

## Getting started

1. Explore the [contexts](contexts/) and select the engineering responsibility you need.
2. Use [deliver change](contexts/delivery/commands/deliver-change.md) to coordinate Requirements through PR creation, or select a focused command such as [elicit requirements](contexts/requirements/commands/elicit-requirements.md) or [review code](contexts/review/commands/review-code.md).
3. Make those artifacts available to your agent host using its supported instruction or skill mechanism. Command names such as `/review/review-code` are **logical toolkit entry points**, not universally pre-registered slash commands.
4. Supply the task, relevant sources, and the authorization required by that command. The selected agent or runtime must execute and verify the work; Markdown instructions alone do not enforce permissions.

Canonical Skills follow the [Agent Skills specification](https://agentskills.io/specification). Hosts can load the relevant `SKILL.md` as needed instead of loading the entire toolkit into every session.

## Optional integrations

The [Cursor Plugin](.cursor-plugin/README.md) optionally exposes canonical Skills, Commands, Agents and Rules without duplicating sources; contextual Rule activation must be verified in Cursor.

The [adapters](adapters/) directory contains optional runtime integrations, including [portable Review execution](adapters/review/README.md), [OCR-assisted discovery](adapters/ocr/README.md), [team orchestration](adapters/teams/README.md), [GitHub PR safeguards](adapters/github/README.md), and [context retrieval](adapters/context/README.md). Canonical workflows remain usable without any particular adapter.

## Documentation

- [Architecture](ARCHITECTURE.md) — canonical structure, ownership matrix, dependency rules, and architectural invariants.
- [Agent contributor instructions](AGENTS.md) — how coding agents should navigate, change, and verify this repository.
- [Review runtime guide](adapters/review/README.md) — review integration and execution options.
- [Evaluation principles and catalogs](evals/README.md) — evidence-based assessment methodology, behavioral scenarios, and their limitations.
- [Capability routing evaluations](evals/routing/README.md) — discovery, activation, and negative-selection test protocol with host-observed evidence.

Agent Toolkit favors **composition without duplicating authority**: one owner for each rule, procedure, invocation boundary, or evidence contract.
