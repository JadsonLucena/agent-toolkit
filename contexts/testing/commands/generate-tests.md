# Generate Tests

## Intent

Create or modify automated tests for an explicitly identified behavior, change, risk, or scope.

## Invocation

This command is an engineering-intent entry point. It delegates the testing procedure rather than duplicating it.

## Uses

* Agent: `contexts/testing/agents/test-engineer.md`
* Skill: `contexts/testing/skills/generate-tests.md`
* Optional contract: `contracts/test-basis.md`

## Inputs

* Target behavior, change, component, defect, or work item.
* Relevant repository context.
* Optional requirements/specification-derived test basis.

## Output

Production-ready tests plus verification evidence, material gaps, and unresolved ambiguity.

## Boundary

Do not invent expected behavior when available evidence supports multiple materially different interpretations.
