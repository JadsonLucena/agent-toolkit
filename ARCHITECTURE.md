# Architecture

This document defines the canonical structure and responsibility boundaries of Agent Toolkit.

## Canonical Structure

```text
contexts/
├── requirements/
│   ├── rules/
│   │   ├── tailoring.md
│   │   ├── requirements.md
│   │   └── backlog.md
│   ├── skills/
│   │   ├── elicitation/skill.md
│   │   ├── definition/skill.md
│   │   ├── example-discovery/skill.md
│   │   ├── validation/skill.md
│   │   └── backlog-planning/skill.md
│   ├── commands/
│   │   ├── shape-change.md
│   │   ├── elicit-requirements.md
│   │   ├── specify-requirements.md
│   │   ├── validate-requirements.md
│   │   ├── build-backlog.md
│   │   └── refine-backlog.md
│   └── agents/
│       ├── requirements-elicitor.md
│       ├── requirements-specifier.md
│       └── backlog-planner.md
├── testing/
│   ├── rules/testing.md
│   ├── skills/generate-tests/skill.md
│   ├── commands/generate-tests.md
│   └── agents/test-engineer.md
└── git/
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

contracts/
├── requirements.md
├── work-item.md
├── test-basis.md
└── test-evidence.md
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

Rules may include an optional `## Foundational Guidance` section when established standards, specifications, books, papers, or engineering practices materially shaped the rule. The section documents conceptual provenance and interpretation; it must not contain reusable procedure or silently override repository, organization, stakeholder, or domain-specific policy. Include only material references, and do not add the section merely for structural symmetry.

## Artifact Matrix

| Context | Artifact | Type | Authoritative responsibility |
|---|---|---|---|
| Requirements | `rules/tailoring.md` | Rule | Risk-proportional rigor, applicable-knowledge selection, governance, and anti-bureaucracy invariants |
| Requirements | `rules/requirements.md` | Rule | Strategic framing, requirement semantics, evidence, ambiguity, quality, acceptance, change impact, and traceability invariants |
| Requirements | `rules/backlog.md` | Rule | Backlog integrity, decomposition, readiness, dependency, tracker compatibility, refinement, and closure invariants |
| Requirements | `skills/elicitation/skill.md` | Skill | Discover and consolidate supported stakeholder needs and unknowns |
| Requirements | `skills/definition/skill.md` | Skill | Transform supported needs into verifiable requirement definitions at the required rigor |
| Requirements | `skills/example-discovery/skill.md` | Skill | Discover domain examples, counterexamples, boundaries, and questions before test automation |
| Requirements | `skills/validation/skill.md` | Skill | Read-only, risk-proportional validation and cross-artifact consistency analysis |
| Requirements | `skills/backlog-planning/skill.md` | Skill | Build or refine traceable planning items while preserving source semantics |
| Requirements | `commands/shape-change.md` | Command | Orchestrate the risk-proportional Requirements path from available evidence through validated planning without duplicating specialist workflows |
| Requirements | `commands/elicit-requirements.md` | Command | Start requirements discovery |
| Requirements | `commands/specify-requirements.md` | Command | Start formal requirement definition |
| Requirements | `commands/validate-requirements.md` | Command | Start the separate requirement-quality gate |
| Requirements | `commands/build-backlog.md` | Command | Build a structured backlog from supported sources |
| Requirements | `commands/refine-backlog.md` | Command | Refine existing planning items without changing source semantics |
| Requirements | `agents/requirements-elicitor.md` | Agent | Own discovery scope, provenance, clarification, and elicitation handoff |
| Requirements | `agents/requirements-specifier.md` | Agent | Own formal requirement semantics, evidence discipline, and validation routing |
| Requirements | `agents/backlog-planner.md` | Agent | Own backlog decomposition, traceability, dependencies, tracker alignment, and readiness boundaries |
| Testing | `rules/testing.md` | Rule | Automated-testing standards and quality invariants |
| Testing | `skills/generate-tests/skill.md` | Skill | Test-design, generation, verification, and diagnosis workflow |
| Testing | `commands/generate-tests.md` | Command | Start automated-test creation or modification |
| Testing | `agents/test-engineer.md` | Agent | Own testing specialization, evidence discipline, and scope boundaries |
| Git | `rules/git.md` | Rule | Repository-state, history, synchronization, worktree, composition, and remote safety |
| Git | `rules/gitflow.md` | Rule | Gitflow applicability and branch-lifecycle invariants |
| Git | `rules/semantic-commit.md` | Rule | Commit semantics, message structure, and atomicity invariants |
| Git | `rules/semantic-version.md` | Rule | Semantic-version compatibility and increment invariants |
| Git | `rules/pull-request.md` | Rule | PR boundary, reviewability, decomposition, template, description, readiness, traceability, and remote-creation invariants |
| Git | `skills/create-semantic-commits/skill.md` | Skill | Atomic staging, verification, message derivation, commit creation, and post-check workflow |
| Git | `skills/determine-semantic-version/skill.md` | Skill | Compatibility analysis, version-policy evaluation, and evidence-backed semantic-version recommendation |
| Git | `skills/manage-branch-work/skill.md` | Skill | Branch, synchronization, integration, and worktree decision and verification workflow |
| Git | `skills/manage-pull-request/skill.md` | Skill | Plan, prepare, and explicitly create coherent pull requests with scoped authorization |
| Git | `commands/commit.md` | Command | Start explicitly requested semantic commit creation |
| Git | `commands/determine-semantic-version.md` | Command | Start semantic-version analysis without release mutation |
| Git | `commands/plan-pull-requests.md` | Command | Plan coherent PR boundaries without repository mutation |
| Git | `commands/prepare-pull-request.md` | Command | Inspect the final change and prepare a truthful PR without remote mutation |
| Git | `commands/create-pull-request.md` | Command | Create a remote PR with explicit creation-only authorization |
| Git | `agents/git-engineer.md` | Agent | Own Git specialization, evidence discipline, operation routing, and boundaries |
| Cross-context | `contracts/requirements.md` | Contract | Neutral elicitation and requirement-definition handoff semantics |
| Cross-context | `contracts/work-item.md` | Contract | Neutral planning-item handoff semantics |
| Cross-context | `contracts/test-basis.md` | Contract | Optional portable Scenario Set and behavioral evidence handoff for Testing |
| Cross-context | `contracts/test-evidence.md` | Contract | Scenario-to-automation coverage and verification evidence |

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
* Cross-context agent or skill composition is allowed only when the invoked workflow explicitly spans those contexts. Data acquisition alone is not sufficient justification for cross-context orchestration.
* Git and Testing must remain independently usable when Requirements artifacts are absent.
* Requirements must remain independently usable when no repository exists.
* Vendor adapters may depend on canonical artifacts; canonical artifacts never depend on a vendor adapter.

## Behavioral Scenario Traceability

When scenarios are first-class behavioral knowledge, preserve semantic identity across contexts:

```text
Requirement / Rule / Use Case / Slice
                │
                ▼
          Scenario Set
                │
        ┌───────┴────────┐
        ▼                ▼
     Examples       Counterexamples
        │                │
        └───────┬────────┘
                ▼
          Test Basis
                │
                ▼
         Automated Tests
                │
                ▼
          Test Evidence
```

`scenario_id` belongs to the semantic Scenario Set. It must not be replaced by a Gherkin title, test method, filename, test-management identifier, or other adapter-specific identity.

`contracts/test-basis.md` carries the portable Scenario Set into Testing. `contracts/test-evidence.md` records scenario-to-automation and verification relationships without mutating upstream requirement semantics.

Scenario, Example, and Automated Test are distinct concepts. The architecture permits one-to-many and many-to-one traceability where the relationship is explicit.

## State Models

Operational state machines belong in skills when they describe how a reusable task progresses.

Agents may contain a routing state model when it represents specialist-level orchestration rather than a reusable task procedure.

Rules remain authoritative for constraints even when a state graph exists.

Iterative or mutating skills should state explicit preconditions and stop conditions when continued execution could otherwise require guessing, unsafe mutation, out-of-scope work, or unproductive retries.

A workflow may diagnose an out-of-scope defect without gaining authority to mutate the affected artifact. Mutation authority comes from the invoked command or separate explicit authorization.

## Change Boundary and Knowledge Batches

Requirements distinguishes three related boundaries:

* **Work Scope** — the broader organizational/change work under consideration.
* **Product Boundary** — what responsibility belongs to the product/software versus its environment.
* **Change Boundary** — what a specific bounded change intends to alter, preserve, exclude, or defer.

A Change Boundary may carry its objective, included/excluded/deferred semantics, affected requirements/rules/scenarios, critical guarantees, dependencies, unresolved scope decisions, and expected state after the bounded change.

Scope discovered during elicitation, definition, or planning is not automatically approved scope. Material expansion or narrowing requires an explicit scope decision; related independent needs remain separate change candidates unless authority expands the boundary; missing critical guarantees must be resolved or block the affected slice.

Requirements work should proceed in the smallest coherent **knowledge batch** that can safely support the next material decision or handoff. This is a requirements analogue of small-batch flow, not a request to fragment semantically coupled rules, scenarios, constraints, or guarantees.

Lifecycle claims remain distinct:

```text
elicitation sufficient
        ≠
requirements specified
        ≠
requirements validated
        ≠
planning ready
        ≠
work item ready
        ≠
slice implemented
        ≠
slice accepted
        ≠
outcome demonstrated
```

Requirements may preserve downstream state references for traceability, but it must not infer those states without evidence.

Local requirements templates, schemas, and notations are representation constraints. They may shape how knowledge is expressed, but they do not redefine canonical semantics or make template completion equivalent to requirements completeness.

## Requirements Tailoring

Requirements work follows the principle **just enough requirements, with sufficient rigor for the risk**.

The Requirements context distinguishes `lightweight`, `standard`, and `high-assurance` rigor when classification is useful. Rigor changes the amount of evidence, validation, traceability, examples, review, and change discipline required; it does not create a mandatory document checklist.

Knowledge concerns are conditional. Missing documentation is not equivalent to missing knowledge, and a concern is not `N/A` merely because its preferred artifact is absent.

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
* Command names use a clear verb-object engineering intent and should remain understandable when surfaced outside their physical context. The context namespace may remove redundancy only when the remaining name stays unambiguous.
* Agent filenames name the specialist role.
* Contract filenames name the semantic handoff, not a workflow.

## Command Shape

Commands should use a consistent editorial shape:

```text
# <Command>

## Intent
## Invocation
## Uses
## Inputs
## Output
## Boundary
```

Commands remain thin. `Invocation` defines what the call authorizes; `Boundary` defines what it does not authorize or what must be escalated.

## Accepted Decisions

1. Physical organization is context-first; conceptual ownership remains Rule × Skill × Command × Agent.
2. Requirements is split into Elicitor, Specifier, and Backlog Planner because discovery, formal semantics, and work decomposition have different evidence and failure modes.
3. Requirements rigor is tailored to risk and uncertainty; the framework optimizes knowledge sufficiency rather than artifact count.
4. Elicitation and specification share `contracts/requirements.md` to preserve semantic continuity without creating a workflow-specific mega-contract.
5. Example discovery belongs to Requirements and may hand a portable Scenario Set and semantic evidence to Testing through `contracts/test-basis.md` without invoking Testing internals.
6. Stable scenario identity is preserved across Requirements, planning, Testing, and adapter representations; execution coverage is reported separately through `contracts/test-evidence.md`.
7. Backlog creation and refinement are two invocation modes of one backlog-planning capability.
8. Testing consumes requirements-derived evidence optionally through `contracts/test-basis.md` and never requires Requirements workflows.
9. Git consumes planning intent only as optional evidence and never treats it as stronger than repository state.
10. Detailed atomic commit execution lives in a dedicated skill.
11. Reusable branch/integration/worktree and semantic-version decision procedures live in dedicated skills.
12. Semantic-version analysis has a public command because it has a clear user-facing intent and a non-mutating authorization boundary.
13. Contracts exist because contexts exchange semantics. They remain neutral schemas rather than a new artifact category.
14. A generic `shared/` directory is intentionally avoided.
15. `/requirements/shape-change` is the optional composite Requirements entry point for feature, defect, migration, regulatory, operational, or other change contexts; it routes existing capabilities and does not create a second source of requirement semantics.
16. Requirements may establish a Change Boundary distinct from Work Scope and Product Boundary, reconcile material scope drift explicitly, work in next-decision-oriented knowledge batches, preserve local representation conventions without confusing them with semantics, and keep lifecycle/completion states distinct.
17. Pull-request work is owned by Git as a review/integration concern: durable PR policy lives in `rules/pull-request.md`, reusable plan/prepare/create procedure lives in `skills/manage-pull-request/skill.md`, and separate commands preserve different authorization levels. Implementation remains outside Git.

## Framework Scope Roadmap

This foundation intentionally does not absorb every discipline into Requirements.

Future **Product Discovery** responsibility should own opportunity framing, user/customer discovery, current-work understanding, Impact Mapping, solution hypotheses, Valuable/Usable/Feasible evaluation, product prototypes/experiments, and validated learning. Requirements may preserve Need, Goals, constraints, candidate solutions, and evidence without becoming the owner of the full Product Discovery discipline.

Future **Lean / Delivery Flow** responsibility should make small batches, WIP, queue time, handoffs, feedback delay, flow efficiency, team empowerment, built-in integrity, and whole-system optimization explicit when the delivery system needs those controls.

Architecture/Design should later own design operationalization, DDD tactical design, architectural trade-offs, Use-Case Realization, and ADR workflows. Release Evidence and Solution/Outcome Evaluation should remain separate downstream responsibilities.

## Deferred Candidates

The following do not currently require first-class commands:

* parallel worktree preparation;
* merge/rebase orchestration;
* repository-composition selection.

Promote one to a command only when there is a clear user-facing invocation intent. Reusable internal procedures may remain skills without public command entry points.

See `MIGRATION.md` for structural renames and responsibility movement.
