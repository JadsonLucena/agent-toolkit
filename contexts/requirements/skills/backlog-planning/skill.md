# Backlog Planning

## Purpose

Use to transform sufficiently defined requirements and other supported work sources into a structured, traceable backlog with decomposition and slicing proportional to the context, without silently changing source semantics.

## Uses

* Rule: `contexts/requirements/rules/tailoring.md`
* Rule: `contexts/requirements/rules/requirements.md`
* Rule: `contexts/requirements/rules/backlog.md`
* Contract: `contracts/requirements.md`
* Contract: `contracts/work-item.md`

## Modes

### Build

Create planning items from sufficiently specified source material.

### Refine

Improve an existing backlog while preserving requirement semantics and traceability.

Both modes use the same decomposition and validation workflow. Refinement is not a separate source of requirements.

## State Model

```mermaid
stateDiagram-v2
    [*] --> InspectSources
    InspectSources --> ClassifyWork
    ClassifyWork --> ShapeSlices
    ShapeSlices --> Trace
    Trace --> AnalyzeDependencies
    AnalyzeDependencies --> EvaluateReadiness
    EvaluateReadiness --> Readiness

    state Readiness <<choice>>
    Readiness --> Ready: sufficient for planning horizon
    Readiness --> RevisePlan: decomposition, slicing, or traceability issue
    Readiness --> NeedRequirementsClarification: semantic ambiguity
    Readiness --> Blocked: required source unavailable

    RevisePlan --> ShapeSlices
    NeedRequirementsClarification --> InspectSources: clarified source received
    Ready --> [*]
    Blocked --> [*]
```

## Workflow

1. Inspect validated requirements, rigor profile, applicable concerns, goals, use cases/scenarios when present, examples, defects, risks, decisions, learning needs, the existing backlog when refining, and target tracker conventions when one exists.
2. Separate requirement semantics from planning choices and preserve the actor/user/business goal when one exists.
3. Preserve established tracker hierarchy, item kinds, and required metadata unless they conflict with semantic integrity.
4. Classify work by coherent outcome, behavior, use-case/journey slice, migration/transition obligation, defect, compliance obligation, technical enabler, operational task, or explicit learning objective when those distinctions improve planning. Do not force everything into a User Story.
5. Shape the smallest coherent delivery or learning slices that preserve source semantics:
   * prefer end-to-end, observable, verifiable, informative slices over layer-by-layer decomposition;
   * keep the goal whole while slicing delivery;
   * preserve relevant business rules, quality/security constraints, acceptance evidence, and critical guarantees;
   * when uncertainty is the primary risk, prefer explicit learning work over speculative implementation.
6. Keep technical tasks subordinate to the outcome/slice they realize unless the task itself is independently meaningful work.
7. Record dependencies, preferred sequencing, risks, assumptions, blockers, learning objectives, and unresolved questions.
8. Avoid implementation decomposition that would prematurely select an unsupported solution.
9. Evaluate whether each item has sufficient semantic context for the intended planning horizon and selected rigor; do not require design details that can legitimately be decided later.
10. Identify low-value tail, speculative flexibility, rare variants, or unused configurability that may be candidates for deferment or removal, but do not make that product decision without authority.
11. Perform closure analysis: identify orphan source obligations, orphan work items, duplicated scope, hidden scope expansion, lost critical guarantees, inconsistent acceptance semantics, and unresolved dependency cycles.
12. Account explicitly for material source obligations that are deferred, rejected, external, out of scope, or otherwise intentionally unplanned.
13. Return material semantic ambiguity to requirements definition or elicitation rather than inventing detail.
14. In `refine` mode, preserve source semantics while improving clarity, slicing, traceability, examples, learning intent, and dependency information.

## Output

Produce `contracts/work-item.md`-compatible items with coherent intent, source traceability, acceptance evidence, slice/learning context when applicable, dependencies, risks, assumptions, critical guarantees, and readiness state.

Include closure findings and candidates for learning, trimming, deferment, or removal without silently deciding their disposition.

Do not invent priority, estimates, owners, iterations, deadlines, or product decisions.

## Stop Conditions

Stop only the affected planning decision and surface the issue when:

* decomposition or slicing would require inventing or materially changing source semantics;
* a source conflict or unresolved requirement ambiguity changes item scope, acceptance, critical guarantees, or dependency structure;
* a required slice would be unsafe or invalid without a guarantee that has not been defined;
* an apparently required task would prematurely encode an unsupported design decision;
* required planning evidence is unavailable;
* repeated refinement is not reducing a material traceability, dependency, slicing, or readiness problem.
