# Generate Tests

## Intent

Create, extend, or modify automated tests for an explicitly identified behavior, change, risk, defect, or implementation scope.

## Invocation

This command selects the Test Engineer and test-generation workflow. It authorizes testing work only; Requirements-derived evidence is optional and does not create a dependency on Requirements agents or skills.

## Uses

* Agent: `contexts/testing/agents/test-engineer.md`
* Skill: `contexts/testing/skills/generate-tests/skill.md`
* Rule: `contexts/testing/rules/testing.md`
* Optional input contract: `contracts/test-basis.md`
* Output contract: `contracts/test-evidence.md`

## Inputs

* Target behavior, change, component, defect, or work item.
* Relevant project and repository context.
* Optional requirement specification, acceptance/fit criteria, rules, portable Scenario Set, examples, counterexamples, boundaries, failure model, or test basis.
* Verification constraints and established testing conventions.

## Output

Production-ready tests, test strategy, traceability to supported behavior, and `contracts/test-evidence.md`-compatible scenario coverage when stable scenario identities exist, plus regression/verification evidence, material gaps, blockers, and unresolved ambiguity.

## Boundary

Do not invent expected behavior when evidence supports multiple materially different interpretations. Preserve supplied scenario identities; this command may map them to tests but must not redefine their business semantics. This command does not authorize unrelated production refactoring or Git mutation.
