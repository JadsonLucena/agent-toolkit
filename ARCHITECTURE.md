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
│   │   ├── elicitation/SKILL.md
│   │   ├── definition/SKILL.md
│   │   ├── example-discovery/SKILL.md
│   │   ├── validation/SKILL.md
│   │   └── backlog-planning/SKILL.md
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
├── design/
│   ├── rules/design.md
│   ├── skills/design-solution/SKILL.md
│   ├── commands/design-solution.md
│   └── agents/design-engineer.md
├── testing/
│   ├── rules/testing.md
│   ├── skills/generate-tests/SKILL.md
│   ├── commands/generate-tests.md
│   └── agents/test-engineer.md
├── review/
│   ├── rules/code-review.md
│   ├── skills/
│   │   ├── review-change/SKILL.md
│   │   ├── coordinate-review-team/SKILL.md
│   │   └── verify-findings/SKILL.md
│   ├── commands/review-code.md
│   └── agents/
│       ├── code-reviewer.md
│       ├── specification-reviewer.md
│       ├── correctness-reviewer.md
│       ├── security-reviewer.md
│       ├── reliability-reviewer.md
│       ├── testing-reviewer.md
│       ├── architecture-reviewer.md
│       └── finding-verifier.md
└── git/
    ├── rules/
    │   ├── git.md
    │   ├── gitflow.md
    │   ├── semantic-commit.md
    │   ├── semantic-version.md
    │   └── pull-request.md
    ├── skills/
    │   ├── create-semantic-commits/SKILL.md
    │   ├── determine-semantic-version/SKILL.md
    │   ├── manage-branch-work/SKILL.md
    │   ├── resolve-merge-conflicts/SKILL.md
    │   └── manage-pull-request/SKILL.md
    ├── commands/
    │   ├── commit.md
    │   ├── determine-semantic-version.md
    │   ├── plan-pull-requests.md
    │   ├── prepare-pull-request.md
    │   ├── resolve-conflicts.md
    │   └── create-pull-request.md
    └── agents/git-engineer.md

contracts/
├── requirements.md
├── work-item.md
├── test-basis.md
├── test-evidence.md
└── review-evidence.md
```

## Optional Vendor Adapters

`adapters/` contains noncanonical provider/runtime-specific integrations. For example, `adapters/ocr/` bridges Alibaba OpenCodeReview's **delegation-mode** file/rule discovery into structured supplemental data for Review. It is excluded from the canonical artifact matrix: adapters may consume canonical semantics, while canonical rules, skills, agents, commands and contracts must remain fully operable without them.

Agent Teams runtime integration is optional as well. The Review context defines team roles and a provider-neutral messaging workflow; **actual peer-to-peer delivery, isolated agent spawning, and progress tracking require a runtime adapter capable of those actions**. No Markdown file or OCR adapter creates runtime messaging by itself. Where unsupported, the lead uses relayed or native-solo review and reports the actual execution mode.

`adapters/review/run_review.py` is the reference entrypoint for canonical `/review/review-code`: it calls `prepare_context.py` **before** the approved reviewer, verifies Git head/diff or workspace fingerprint afterward, and freezes R0–R3 risk/concerns before any advertised Task spawn. Preparation prioritizes OCR >=1.9.0 when allowed and preserves neutral inventory in `adapters/review/git_scope.py`; `--no-ocr` never imports OCR. `adapters/review/team_orchestration.py` is the provider-neutral Task protocol: risk-proportionate N from the canonical coordinate-review-team skill, including small critical diffs with fewer genuine concerns; isolated Tasks without observed direct exchange are `team-relayed`, not `team-live`. A host must actually bind its Task API to the protocol: Markdown alone never spawns or isolates agents. `adapters/teams/peer_bus.py` implements bounded in-process peer messages with explicit request/response/resolution tracking for host-supplied role handlers, not independent model spawning or a `team-live` review. `adapters/github/guarded_pr.py` is an explicitly invoked GitHub CLI preflight-and-create adapter: it verifies SSH-signed review evidence from a key approved by an **external protected policy**, executes the policy's required checks, and verifies the created remote PR after mutation. The trusted runtime must protect signer keys, policies and their selection. No wrapper can prevent bypass through unrelated GitHub clients without separate platform authorization enforcement.

An adapter must not claim review coverage, bypass verification, publish remote changes, install dependencies or mutate project artifacts merely because the helper exists. OCR's excluded/unaccounted paths remain in the independent review's Git inventory. Adapter failures trigger native fallback when Git context is still inspectable.

## Responsibility Model

| Artifact kind | Owns | Must not own |
|---|---|---|
| Rule | Durable principles, constraints, invariants, safety and quality standards | Step-by-step workflow, invocation routing, specialist persona |
| Skill | Reusable procedure, operational state, verification loop, task output | Global policy, user entry-point semantics, specialist identity |
| Command | Explicit engineering intent, input selection, authorization policy, thin invocation-level routing, workflow entry point, expected result | Detailed policy or duplicated specialist procedure |
| Agent | Specialist scope, evidence discipline, dynamic specialist orchestration, boundaries, handoffs | Detailed reusable task procedure |
| Contract | Neutral handoff semantics and schema meaning | Policy, workflow, orchestration, specialist behavior |

Contracts are supporting artifact kinds outside the four canonical behavioral artifact types (Rule, Skill, Command, Agent). They carry neutral schemas rather than behavior.

Rules may include an optional `## Foundational Guidance` section when established standards, specifications, books, papers, or engineering practices materially shaped the rule. The section documents conceptual provenance and interpretation; it must not contain reusable procedure or silently override repository, organization, stakeholder, or domain-specific policy. Include only material references, and do not add the section merely for structural symmetry.

## Artifact Matrix

| Context | Artifact | Type | Authoritative responsibility |
|---|---|---|---|
| Requirements | `rules/tailoring.md` | Rule | Risk-proportional rigor, applicable-knowledge selection, governance, and anti-bureaucracy invariants |
| Requirements | `rules/requirements.md` | Rule | Strategic framing, requirement semantics, evidence, ambiguity, quality, acceptance, change impact, and traceability invariants |
| Requirements | `rules/backlog.md` | Rule | Backlog integrity, decomposition, readiness, dependency, tracker compatibility, refinement, and closure invariants |
| Requirements | `skills/elicitation/SKILL.md` | Skill | Discover and consolidate supported stakeholder needs and unknowns |
| Requirements | `skills/definition/SKILL.md` | Skill | Transform supported needs into verifiable requirement definitions at the required rigor |
| Requirements | `skills/example-discovery/SKILL.md` | Skill | Discover domain examples, counterexamples, boundaries, and questions before test automation |
| Requirements | `skills/validation/SKILL.md` | Skill | Read-only, risk-proportional validation and cross-artifact consistency analysis |
| Requirements | `skills/backlog-planning/SKILL.md` | Skill | Build or refine traceable planning items while preserving source semantics |
| Requirements | `commands/shape-change.md` | Command | Route the minimum necessary Requirements capabilities toward validated planning; specialist orchestration remains with agents |
| Requirements | `commands/elicit-requirements.md` | Command | Start requirements discovery |
| Requirements | `commands/specify-requirements.md` | Command | Start formal requirement definition |
| Requirements | `commands/validate-requirements.md` | Command | Start the separate requirement-quality gate |
| Requirements | `commands/build-backlog.md` | Command | Build a structured backlog from supported sources |
| Requirements | `commands/refine-backlog.md` | Command | Refine existing planning items without changing source semantics |
| Requirements | `agents/requirements-elicitor.md` | Agent | Own discovery scope, provenance, clarification, and elicitation handoff |
| Requirements | `agents/requirements-specifier.md` | Agent | Own formal requirement semantics, evidence discipline, and validation routing |
| Requirements | `agents/backlog-planner.md` | Agent | Own backlog decomposition, traceability, dependencies, tracker alignment, and readiness boundaries |
| Design | `rules/design.md` | Rule | Technical decision, risk, traceability, compatibility and reversible slice invariants |
| Design | `skills/design-solution/SKILL.md` | Skill | Evidence-backed design of the next bounded implementation slice |
| Design | `commands/design-solution.md` | Command | Start scoped technical design without implementation authority |
| Design | `agents/design-engineer.md` | Agent | Own technical design decisions and handoff integrity |
| Testing | `rules/testing.md` | Rule | Automated-testing standards and quality invariants |
| Testing | `skills/generate-tests/SKILL.md` | Skill | Test-design, generation, verification, and diagnosis workflow |
| Testing | `commands/generate-tests.md` | Command | Start automated-test creation or modification |
| Testing | `agents/test-engineer.md` | Agent | Own testing specialization, evidence discipline, and scope boundaries |
| Review | `rules/code-review.md` | Rule | Advisory/gate profiles, calibrated findings, documentation drift and evidence-driven Review policy |
| Review | `rules/high-risk-patterns.md` | Rule | Eight source-grounded risk counterexamples used as investigation heuristics |
| Review | `skills/review-change/SKILL.md` | Skill | Native review of a complete diff with context, coverage, risk, optional helpers, and evidence |
| Review | `skills/coordinate-review-team/SKILL.md` | Skill | Risk-based Agent Team coordination, peer messaging, challenge routing, verification and native fallback |
| Review | `skills/verify-findings/SKILL.md` | Skill | Falsification, verification, deduplication, and triage of candidate findings |
| Review | `commands/review-code.md` | Command | Start read-only independent review of a bounded code change |
| Review | `agents/code-reviewer.md` | Agent | Lead independent reviews, select specialists, coordinate team exchanges and issue one evidence-backed verdict |
| Review | `agents/specification-reviewer.md` | Agent | Investigate specification and contract compliance |
| Review | `agents/correctness-reviewer.md` | Agent | Investigate behavioral correctness and regressions |
| Review | `agents/security-reviewer.md` | Agent | Investigate security and privacy boundaries |
| Review | `agents/reliability-reviewer.md` | Agent | Investigate data integrity, concurrency and resilience |
| Review | `agents/testing-reviewer.md` | Agent | Investigate assertion and test/CI evidence adequacy |
| Review | `agents/architecture-reviewer.md` | Agent | Investigate architecture, compatibility and operational constraints |
| Review | `agents/finding-verifier.md` | Agent | Independently falsify candidate findings and challenge peer conclusions |
| Git | `rules/git.md` | Rule | Repository-state, history, synchronization, worktree, composition, remote safety, and commit-safety verification gates |
| Git | `rules/gitflow.md` | Rule | Gitflow applicability and branch-lifecycle invariants |
| Git | `rules/semantic-commit.md` | Rule | Commit semantics, message structure, and atomicity invariants |
| Git | `rules/semantic-version.md` | Rule | Semantic-version compatibility and increment invariants |
| Git | `rules/pull-request.md` | Rule | PR boundary, reviewability, decomposition, template, description, readiness, traceability, and remote-creation invariants |
| Git | `skills/create-semantic-commits/SKILL.md` | Skill | Atomic staging, verification, message derivation, commit creation, and post-check workflow |
| Git | `skills/determine-semantic-version/SKILL.md` | Skill | Compatibility analysis, version-policy evaluation, and evidence-backed semantic-version recommendation |
| Git | `skills/manage-branch-work/SKILL.md` | Skill | Branch, synchronization, integration, and worktree decision and verification workflow |
| Git | `skills/resolve-merge-conflicts/SKILL.md` | Skill | Three-way intent reconstruction, reconciliation, authorized patching and integrated-behavior verification |
| Git | `skills/manage-pull-request/SKILL.md` | Skill | Plan, prepare, and explicitly create coherent pull requests with scoped authorization |
| Git | `commands/commit.md` | Command | Start explicitly requested semantic commit creation |
| Git | `commands/determine-semantic-version.md` | Command | Start semantic-version analysis without release mutation |
| Git | `commands/plan-pull-requests.md` | Command | Plan coherent PR boundaries without repository mutation |
| Git | `commands/prepare-pull-request.md` | Command | Inspect the final change and prepare a truthful PR without remote mutation |
| Git | `commands/resolve-conflicts.md` | Command | Begin read-only conflict diagnosis or explicitly authorized scoped application |
| Git | `commands/create-pull-request.md` | Command | Create a remote PR with explicit creation-only authorization |
| Git | `agents/git-engineer.md` | Agent | Own Git specialization, evidence discipline, operation routing, and boundaries |
| Cross-context | `contracts/design-evidence.md` | Contract | Portable technical design decisions and handoff to Implementation |
| Cross-context | `contracts/review-evidence.md` | Contract | Portable independent code-review evidence and pre-PR eligibility semantics |
| Cross-context | `contracts/review-specialist-evidence.md` | Contract | Self-contained specialist and verifier evidence |
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
* A skill may invoke another skill in the same context when the nested capability is independently reusable, its procedure is not duplicated, and the dependency remains acyclic.
* Agents may depend on rules, skills, and contracts, but not on commands.
* Commands may select agents and skills and reference rules or contracts, but remain thin. A composite command may route between existing capabilities to fulfill its invocation, but does not own their internal workflows.
* Agents own dynamic specialist-level orchestration and handoffs; the command chooses the invoked capability, not the implementation of its procedure.
* Commands define the authorization granted by invocation; authorization does not silently expand to adjacent mutations or downstream operations.
* Contracts must not depend on a context implementation.
* A context must not invoke another context's internal agent or skill merely to obtain data.
* Cross-context integration should pass semantic evidence through contracts or explicit inputs.
* Cross-context agent or skill composition is allowed only when the invoked workflow explicitly spans those contexts. Data acquisition alone is not sufficient justification for cross-context orchestration.
* Git and Testing must remain independently usable when Requirements artifacts are absent.
* Requirements must remain independently usable when no repository exists.
* Vendor adapters may depend on canonical artifacts; canonical artifacts never depend on a vendor adapter.

## Authorization Policy and Runtime Enforcement

A Command declares **canonical authorization policy** for an invocation. Its Markdown text does not, by itself, enforce a security boundary or prevent an agent from invoking a tool with broader permissions.

Platform adapters and runtimes are responsible for enforcing the declared scope at the actual side-effect boundary, when the platform supports such controls:

* Expose only the tools/capabilities required for the authorized operation, with scoped credentials and resource permissions where possible.
* Apply tool-level policy checks and approvals **before** sensitive or irreversible actions; do not rely only on agent instructions or output checks.
* Treat authority as operation-specific: creating a pull request does not authorize push, merge, auto-merge, release, or deployment.
* Deny or pause out-of-scope operations rather than inferring authorization from an adjacent action.
* Report which restrictions are technically enforced and which are only instruction-level policy. When enforcement is unavailable, do not represent Markdown instructions as a security control; use an external approval/control or withhold the sensitive capability.

An adapter's inability to enforce a control never expands canonical authorization. Runtime enforcement is a deployment responsibility, not a new canonical artifact type.

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

* Context names are stable engineering nouns: `requirements`, `design`, `testing`, `review`, `git`.
* Rule filenames name the governed concern.
* Skill directories name the reusable capability.
* Command names use a clear verb-object engineering intent and should remain understandable when surfaced outside their physical context. The context namespace may remove redundancy only when the remaining name stays unambiguous.
* Agent filenames name the specialist role.
* Contract filenames name the semantic handoff, not a workflow.

## Skill Format and Portability

Canonical Skills are stored at `contexts/<context>/skills/<capability>/SKILL.md` and follow the [Agent Skills specification](https://agentskills.io/specification). The file starts with YAML frontmatter:

* `name` matches the capability directory: lowercase letters, digits, and hyphens.
* `description` says what the skill does and when to use it. Hosts compare the request with this field and load the body only when it matches, or when the user invokes the skill by name.

The body states the procedure once, as a diagram under Workflow. A decision node names the rule section that owns the invariant and does not restate it. Do not keep a numbered list that retells the diagram. Foundational Guidance stays in the rule as the theoretical reference for reviewers of the artifact. Do not add provider metadata such as model, reasoning effort, or tool allowlists to the canonical frontmatter.

A host install path, such as `.claude/skills/` or `.agents/skills/`, may symlink or copy the canonical file. That installation is not a second source of truth.

## Command Terminology

A Toolkit **Command** is an explicit invocation artifact, not necessarily a mutating operation in Command–Query Separation (CQS), nor an implementation of the GoF Command pattern. A read-only invocation such as `/git/determine-semantic-version` is still a Toolkit Command.

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
11. Reusable branch/integration/worktree and semantic-version decision procedures live in dedicated skills. Merge-conflict semantic reconciliation has a dedicated Git skill; the existing Git Engineer coordinates it.
12. Semantic-version analysis has a public command because it has a clear user-facing intent and a non-mutating authorization boundary.
13. Contracts exist because contexts exchange semantics. They remain neutral schemas rather than a new artifact category.
14. A generic `shared/` directory is intentionally avoided.
15. `/requirements/shape-change` is the optional composite Requirements entry point for feature, defect, migration, regulatory, operational, or other change contexts; it routes existing capabilities and does not create a second source of requirement semantics.
16. Requirements may establish a Change Boundary distinct from Work Scope and Product Boundary, reconcile material scope drift explicitly, work in next-decision-oriented knowledge batches, preserve local representation conventions without confusing them with semantics, and keep lifecycle/completion states distinct.
17. Pull-request work is owned by Git as a review/integration concern: durable PR policy lives in `rules/pull-request.md`, reusable plan/prepare/create procedure lives in `skills/manage-pull-request/SKILL.md`, and separate commands preserve different authorization levels. Implementation remains outside Git.

18. Code Review is a separate, read-only context. It operates natively without required providers/adapters; OCR and similar helpers are optional. Requirements, Testing, and Git retain their own authority.
19. Independent review, applicable tests, and lint are distinct pre-creation prerequisites for PRs. Git consumes `contracts/review-evidence.md` without depending on Review's internal procedures. Enforcing this policy requires runtime/CI controls; Markdown alone cannot block unauthorized remote creation.
20. Review uses an optional risk-driven Agent Team, with the Code Review Lead coordinating specialist-to-specialist evidence exchange and independent falsification. R2/R3 favor relevant collaborative specialists where runtime support exists; native-solo and lead-relayed fallback remain valid. Provider-specific team orchestration is a runtime responsibility, not a requirement for canonical review.
21. One fact has one owner. A command states the authorization and points at the skill. An agent routes to the skill. The skill diagram names the rule section for each decision. The rule owns the invariant and its Foundational Guidance. The contract owns the evidence shape.

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

### Portable Review Execution

The canonical Rule/Skill/Agent/Command/Contract artifacts define the required
semantics. Adapters in `adapters/review/` are optional reference implementations,
not the source of truth for any IDE, model, issue tracker, Git host or runtime.

Host-native Review follows the same **prepare → independent investigation →
validate evidence** contract as a subprocess reviewer. Preparation freezes
repository, base/head or workspace fingerprint, full inventory and R0–R3
risk before any isolated task. The validator checks that the same snapshot
remains current. Optional OCR hints never reduce native review coverage.

Canonical concerns: `contract`, `correctness`, `security`, `reliability`,
`testing`, `architecture`. The CLI accepts aliases `spec`,
`specification` and `arch`. `--base-branch` resolves local/cached
refs without fetch; `--output-language` selects human report prose.

## Advisory and Gate Review Semantics

Canonical `contexts/review/rules/code-review.md` owns the two review
profiles and calibrated finding policy. `advisory` can support complete
read-only local reviews without independent session attestation; it must be
visibly labeled and **cannot** satisfy remote PR preflight. `gate` additionally
requires independently executed review and protected, externally verified
SSHSIG evidence. The Git adapter rejects missing/legacy/advisory profile
regardless of a PASS, signer or local success.

`contracts/review-evidence.md` defines portable `review_profile`, optional
`likelihood`, `origin`, `lead_confirmed`, and pinned
`external_evidence[]`. Source-based falsification prompts live **only** in
`contexts/review/rules/high-risk-patterns.md`, referenced by specialist
agents rather than copied into their prompts. Repository-owned, versioned
conventions can be discovered from existing project documentation; no
specific IDE format, tracker, provider, model or execution engine is required.

## Documentation Consistency in Code Review

The Review Rule is the sole normative source for documentation drift:
the Lead examines relevant documentation (including unchanged files) against
the actual code and applicable contracts. The existing specification and
architecture agents may contribute; no separate documentation agent or
platform-dependent review concern is created. The review skill performs
the bounded inspection and the evidence contract optionally records
`documentation_assessment`. Missing, obsolete, contradictory, ambiguous
or duplicated knowledge becomes a finding only with relevant observed impact,
not by checklist matching. The signed Git gate, reviewer independence and
risk-proportionate review policies are unchanged.
