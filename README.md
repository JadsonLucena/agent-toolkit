# Agent Toolkit

**A vendor-neutral software engineering toolkit for AI coding agents.**

Agent Toolkit organizes reusable engineering guidance into Rules, Skills, Commands, and specialist Agents. It helps teams move from requirements to delivery with explicit responsibility boundaries, traceable evidence, and risk-appropriate verification—without tying the engineering model to one IDE, model, or provider.

The toolkit is a collection of portable, version-controlled Markdown artifacts, **not a standalone executable agent or an automatically installed CLI**. Agent runtimes can discover or integrate the relevant artifacts; optional adapters support specific environments.

## What it covers

| Context | Purpose |
| --- | --- |
| [Requirements](contexts/requirements/) | Discover needs, specify and validate requirements, and plan a backlog. |
| [Design](contexts/design/) | Define technical decisions for a bounded implementation slice. |
| [Implementation](contexts/implementation/) | Implement and verify an authorized increment. |
| [Delivery](contexts/delivery/) | Coordinate evidence-based handoffs across the lifecycle. |
| [Testing](contexts/testing/) | Design and generate automated tests with traceable evidence. |
| [Review](contexts/review/) | Independently assess changes, risks, and documentation consistency. |
| [Git](contexts/git/) | Manage repository changes, semantic commits, branches, and pull requests. |

Within each context, **Rules** define durable constraints; **Skills** describe reusable procedures; **Commands** provide explicit invocation entry points; and **Agents** describe specialist roles. Shared [Contracts](contracts/) carry evidence between contexts without forcing them to depend on each other's internal workflows.

## Getting started

1. Explore the [contexts](contexts/) and select the engineering responsibility you need.
2. Open the applicable command and skill; for example, [elicit requirements](contexts/requirements/commands/elicit-requirements.md) or [review code](contexts/review/commands/review-code.md).
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
- [Evaluation catalogs](evals/) — provider-neutral behavioral evaluation baselines and their limitations.

Agent Toolkit favors **composition without duplicating authority**: one owner for each rule, procedure, invocation boundary, or evidence contract.
