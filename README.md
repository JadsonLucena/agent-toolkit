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
│   ├── tailoring.md
│   ├── requirements.md
│   └── backlog.md
├── skills/
│   ├── elicitation/skill.md
│   ├── definition/skill.md
│   ├── example-discovery/skill.md
│   ├── validation/skill.md
│   └── backlog-planning/skill.md
├── commands/
│   ├── shape-change.md
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

Requirements can operate from conversations, documents, interviews, tickets, existing-system evidence, policies, data, and other supported sources. A repository is not required.

Requirements work is tailored to risk and uncertainty using the principle **just enough requirements, with sufficient rigor for the risk**. The toolkit may use `lightweight`, `standard`, or `high-assurance` rigor when the distinction is useful; it does not require every known artifact or technique for every change.

When scope control is material, Requirements distinguishes **Work Scope**, **Product Boundary**, and a specific **Change Boundary**. The Change Boundary records what the current change intends to alter, preserve, exclude, or defer and is reconciled as new evidence appears. Discovery does not automatically authorize scope expansion.

Requirements also favors the smallest coherent **knowledge batch** that safely supports the next material decision. Existing project templates/schemas are preserved as representation conventions when applicable, but template completeness is not requirements completeness. Lifecycle states such as elicitation sufficient, requirements specified, requirements validated, planning ready, implementation, acceptance, and demonstrated outcome remain distinct.

Elicitation and specification share `contracts/requirements.md` so Need/Goal context, source evidence, decisions, assumptions, conflicts, applicable concerns, and traceability survive the transformation without coupling their workflows. Example Discovery can define stable Scenario Sets, refine rules/examples/boundaries before automation, and hand optional evidence to Testing through `contracts/test-basis.md`.

`/requirements/shape-change` is an optional composite entry point that routes the existing elicitation, definition, read-only validation, and backlog-planning capabilities according to the evidence already available. It works toward the next material decision using the smallest coherent knowledge batch, preserves/reconciles the Change Boundary when present, and remains neutral to feature, defect, migration, regulatory, and other change types. It does not authorize design, implementation, testing, or Git mutation.

### Testing

```text
contexts/testing/
├── rules/testing.md
├── skills/generate-tests/skill.md
├── commands/generate-tests.md
└── agents/test-engineer.md
```

Testing remains autonomous. Requirements evidence may improve test design through the optional `contracts/test-basis.md`, but Testing does not invoke Requirements skills or agents merely to obtain that evidence. When stable scenarios are supplied, Testing preserves their identities and reports coverage/verification separately through `contracts/test-evidence.md`.

### Git

```text
contexts/git/
├── rules/
│   ├── git.md
│   ├── gitflow.md
│   ├── semantic-commit.md
│   ├── semantic-version.md
│   └── pull-request.md
├── skills/
│   ├── create-semantic-commits/skill.md
│   ├── determine-semantic-version/skill.md
│   ├── manage-branch-work/skill.md
│   └── manage-pull-request/skill.md
├── commands/
│   ├── commit.md
│   ├── determine-semantic-version.md
│   ├── plan-pull-requests.md
│   ├── prepare-pull-request.md
│   └── create-pull-request.md
└── agents/git-engineer.md
```

Git is cross-cutting but is not automatically invoked by other contexts. Planning metadata may provide supporting intent, while repository evidence remains authoritative for repository operations.

Pull-request workflows preserve three distinct intents: planning review boundaries, preparing a truthful PR from the final diff, and explicitly creating the remote review request. PRs are bounded by coherent/verifiable integration units rather than line count alone; repository PR templates take precedence over the generic fallback; and PR creation never implies push, merge, auto-merge, release, or deployment authorization.

## Contracts

* `contracts/requirements.md` — elicitation and requirement-definition semantics, including optional Change Boundary, scope-change, lifecycle, and representation-convention context.
* `contracts/work-item.md` — planning-item semantics.
* `contracts/test-basis.md` — optional portable Scenario Set and behavioral evidence for Testing.
* `contracts/test-evidence.md` — scenario-to-automation coverage and verification evidence.

## Commands

Commands express engineering intent rather than low-level tool aliases:

```text
/requirements/shape-change
/requirements/elicit-requirements
/requirements/specify-requirements
/requirements/validate-requirements
/requirements/build-backlog
/requirements/refine-backlog

/testing/generate-tests

/git/commit
/git/determine-semantic-version
/git/plan-pull-requests
/git/prepare-pull-request
/git/create-pull-request
```

A command's invocation defines its authorization boundary. For example, determining a semantic version does not authorize version-file mutation, tagging, publishing, or release.

## Development Pipeline

The intended delivery flow is **test-first**: supported behavior is specified before implementation, and executable tests can guide implementation incrementally when a TDD workflow is selected.

```text
Elicitation ↔ Specification ↔ Validation ↔ Backlog / Plan
                 │                           │
                 ▼                           ▼
        Scenario Set / Test Basis     Initial Design
                 └──────────┬────────────────┘
                            ▼
                       Test Design
                            ▼
                   RED → GREEN → REFACTOR
                    ▲                   │
                    └───────────────────┘
                            │
                            ▼
                     Verification → Review

Cross-cutting: Git, security, conventions, …
```

Requirements stages are iterative. Validation is a separate, read-only requirement-quality gate: its findings return to the appropriate elicitation or specification owner before a planning-readiness claim. Backlog ambiguity can also return to earlier stages. A Scenario Set and the portable `contracts/test-basis.md` can originate during specification, **before** backlog planning or detailed technical design, and evolve through approved clarification. The diagram shows the principal handoff, not a mandatory one-way order between all activities.

**Test Basis is not an executable test suite.** Test Design selects and prioritizes behavior, risk, test levels, and test cases from supported evidence. With TDD, choose the next small behavior, write and execute a test that fails for the **expected reason** (RED), implement just enough production code to pass (GREEN), and refactor while keeping tests green (REFACTOR). Repeat per behavior; do not turn the entire test list into speculative executable tests before the first implementation feedback. Initial design provides only the interface/architecture decisions needed to begin and may evolve during TDD.

Verification remains distinct from the TDD inner loop: it checks the integrated result against applicable acceptance criteria, scenario coverage, contracts, functional and non-functional requirements, and project quality gates. TDD does not replace integration, security, resilience, performance, or acceptance verification. A material discrepancy discovered in test design or execution must be returned to the appropriate requirement owner, not silently change expected behavior.

The current `/testing/generate-tests` command authorizes **test-artifact changes only**; it does not authorize production implementation. A future TDD capability should be owned by the Implementation context and invoked with explicit scope for both test and production-code changes, reusing Testing's standards and portable test evidence without changing their canonical ownership. The diagram expresses the target workflow; it does not claim that a TDD skill or Implementation agent already exists. Projects not using TDD may use another authorized, risk-appropriate delivery workflow while preserving test traceability and verification.

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
Source / Rationale
      ↓
Need → Business Goal
      ↓
Change Boundary
      ↓
Requirement / Rule / Constraint / Use Case
      │
      ▼
Scenario Set
      ├────────────► Example / Counterexample / Boundary
      │
      ▼
Slice / Work Item
      ▼
Test Basis
      ▼
Automated Tests
      ▼
Test Evidence
      ▼
Outcome Evidence
```

Downstream artifacts may summarize upstream semantics but must not silently change them.

## BDD Portability

The canonical model does not equate BDD with Gherkin.

`contracts/test-basis.md` can carry stable scenarios, rules, examples, counterexamples, boundaries, assumptions, and expected outcomes independently from any automation syntax. Adapters may render that same Scenario Set as Gherkin/Cucumber, framework-native tests, test-case-management records, Markdown, JSON/YAML, or other representations.

`contracts/test-evidence.md` keeps execution evidence separate from the business specification so a test framework can change without changing scenario identity.

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
* **Risk proportionate** — requirements rigor and representation scale with consequence, uncertainty, and the next decision rather than template completeness.
* **Context aware** — preserve relevant context while minimizing unnecessary context.
* **Task oriented** — commands express clear engineering intent.
* **Quality driven** — verification distinguishes evidence from assumptions and unverified conclusions.

## Roadmap

Next contexts should cover Product Discovery, architecture and design, implementation, code review, security engineering, release evidence, solution/outcome evaluation, and Lean/delivery-flow concerns without collapsing specialties. Requirements may carry Needs, Goals, constraints, candidate solutions, uncertainty, quality/security drivers, and other semantic evidence, but it does not own those disciplines' internal procedures.

Product Discovery should later own opportunity/user discovery, Impact Mapping, solution hypotheses, Valuable/Usable/Feasible evaluation, prototypes/experiments, and validated learning. Lean/delivery flow should later own explicit WIP, queue, batch-size, handoff, feedback-delay, flow-efficiency, built-in-integrity, and whole-system concerns when needed.

Additional Git commands should be introduced only when a reusable procedure also has a clear user-facing invocation intent and authorization boundary.

## Portability

Canonical definitions are neutral Markdown. Adapters may transform them into provider-specific formats while preserving canonical semantics.

Canonical Skills use lowercase `skill.md` without requiring Agent Skills frontmatter. They are **not directly Agent Skills-compatible**. An adapter may export compliant `SKILL.md` files with `name`/`description` metadata, reference rewriting, and format validation. The canonical source remains authoritative; see `ARCHITECTURE.md` for the compatibility contract.

## Goal

The goal is not a collection of prompts. It is a **composable software engineering system for AI agents** where responsibility, evidence, workflow, boundaries, and context are structured to produce consistent engineering outcomes.
