# Example Discovery

## Purpose

Use when scenarios and concrete examples are needed to refine shared understanding of a requirement, rule, use case, or planned slice before test automation.

This skill supports Example Mapping, Specification by Example, and BDD-oriented behavioral discovery without requiring Gherkin, a BDD framework, or the Testing context.

## Uses

* Rule: `contexts/requirements/rules/requirements.md`
* Rule: `contexts/requirements/rules/tailoring.md`
* Contract: `contracts/requirements.md`
* Optional handoff: `contracts/test-basis.md`

## Working State

Maintain, when relevant:

* source requirement, rule, use case, scenario, or slice;
* a Scenario Set with stable scenario identities;
* domain language and applicable business rules;
* scenario context, preconditions, trigger/action, and expected outcomes;
* concrete examples;
* counterexamples;
* boundary examples;
* open questions revealed by scenarios/examples;
* assumptions and unresolved conflicts;
* traceability to the source behavior.

## Scenario Identity

When scenarios are material:

* assign a stable `scenario_id` within the current scenario set;
* preserve an existing scenario identifier instead of generating a replacement;
* keep identifiers independent from Gherkin line numbers, test names, filenames, classes, methods, or test-framework identifiers;
* do not fabricate identifiers from an external tracker or requirements system;
* when an upstream artifact already owns scenario identity, reuse it exactly.

The identifier exists to preserve semantic traceability across representations, not to prescribe serialization.

## Workflow

1. Inspect the source behavior, rules, use cases, acceptance semantics, constraints, existing scenarios, and unresolved questions.
2. Reuse existing scenario identities and relationships when they already represent the behavior correctly.
3. Identify the material behavioral situations or paths that require explicit understanding. Keep a scenario distinct from the concrete examples that illustrate it.
4. For each material scenario, establish enough supported semantics to make the behavior understandable:
   * source references;
   * useful scenario dimensions;
   * relevant starting context and preconditions;
   * trigger, actor action, event, or condition;
   * expected observable outcomes and guarantees;
   * applicable rules, invariants, and acceptance/fit evidence;
   * material assumptions, risks, and open questions.
5. Produce concrete domain-oriented examples using business language rather than UI, transport, storage, or test-framework details unless those details are themselves required.
6. Add counterexamples where they clarify what must not satisfy the rule or behavior.
7. Identify behavior-change boundaries and include examples immediately around those boundaries when useful.
8. Use scenarios and examples to expose contradictions, missing rules, hidden assumptions, ambiguous thresholds, incomplete paths, and oversized or immature slices.
9. Keep unanswered questions explicit; do not invent an answer merely to complete a Scenario Set.
10. Consolidate redundant examples once the underlying rule or scenario is clear. Examples support scenarios/rules rather than replacing them.
11. Preserve traceability from each material scenario and example to the requirement, rule, use case, slice, or other behavior source it illustrates.
12. When test automation will follow, expose the relevant Scenario Set through `contracts/test-basis.md` without coupling this skill to Testing internals.

## Output

Produce, when scenarios are material, a `contracts/test-basis.md`-compatible Scenario Set containing:

* stable scenario identities;
* source references;
* behavioral intent and useful dimensions;
* context/preconditions;
* trigger/action;
* expected outcomes;
* applicable rules/invariants;
* examples, counterexamples, and boundaries;
* assumptions, risks, and open questions.

The output may contribute to acceptance evidence or a test basis, but it does not itself authorize creating tests or implementation changes.

## Stop Conditions

Stop only the affected scenario/example decision and surface the issue when:

* scenarios reveal materially different plausible behaviors that require stakeholder authority;
* a threshold, rule, precondition, outcome, or guarantee needed to define the behavior is unsupported;
* examples would require inventing business semantics;
* an existing scenario identity conflicts with another artifact and the authoritative source cannot be determined;
* the source requirement, use case, or slice is too immature to describe coherently.
