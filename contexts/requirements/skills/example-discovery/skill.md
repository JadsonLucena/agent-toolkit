# Example Discovery

## Purpose

Use when concrete examples are needed to refine shared understanding of a requirement, rule, scenario, or planned slice before test automation.

This skill supports Example Mapping and Specification by Example principles without requiring Gherkin, a BDD framework, or the Testing context.

## Uses

* Rule: `contexts/requirements/rules/requirements.md`
* Rule: `contexts/requirements/rules/tailoring.md`
* Contract: `contracts/requirements.md`
* Optional handoff: `contracts/test-basis.md`

## Working State

Maintain, when relevant:

* source requirement, rule, use case, scenario, or slice;
* domain language and applicable business rules;
* concrete examples;
* counterexamples;
* boundary examples;
* open questions revealed by examples;
* assumptions and unresolved conflicts;
* traceability to the source behavior.

## Workflow

1. Inspect the source behavior, rules, acceptance semantics, constraints, and unresolved questions.
2. Identify the material rules or decisions whose behavior is difficult to understand abstractly.
3. Produce concrete domain-oriented examples using the language of the business rather than UI, transport, storage, or test-framework details unless those details are themselves required.
4. Add counterexamples where they clarify what must not satisfy the rule.
5. Identify behavior-change boundaries and include examples immediately around those boundaries when useful.
6. Use examples to expose contradictions, missing rules, hidden assumptions, ambiguous thresholds, and oversized or immature slices.
7. Keep unanswered questions explicit; do not invent an answer merely to complete an example set.
8. Consolidate redundant examples once the underlying rule is clear; examples support the rule rather than replacing it.
9. Preserve traceability from each material example to the rule, requirement, scenario, or slice it illustrates.
10. When test automation will follow, expose the relevant examples, counterexamples, boundaries, rules, and open questions through `contracts/test-basis.md` without coupling this skill to Testing internals.

## Output

Produce an example set containing the applicable rules, examples, counterexamples, boundary cases, open questions, and source references.

The output may contribute to acceptance evidence or a test basis, but it does not itself authorize creating tests or implementation changes.

## Stop Conditions

Stop the affected example-discovery decision and surface the issue when:

* examples reveal materially different plausible behaviors that require stakeholder authority;
* a threshold or rule needed to define the behavior is unsupported;
* examples would require inventing business semantics;
* the source requirement or slice is too immature to illustrate coherently.
