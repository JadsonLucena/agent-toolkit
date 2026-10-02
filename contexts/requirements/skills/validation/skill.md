# Requirements Validation

## Purpose

Use as a separate quality gate for requirement definitions before downstream planning or implementation.

## Uses

* Rule: `contexts/requirements/rules/requirements.md`
* Contract: `contracts/requirements.md`

## Finding Taxonomy

Classify each material finding by what was discovered:

* `defect` — the specification contradicts supported evidence, its own semantics, or an applicable rule and an evidence-backed correction can be described without inventing stakeholder intent;
* `ambiguity` — multiple materially different interpretations remain plausible;
* `gap` — information required for the intended downstream use is absent;
* `conflict` — supported sources, requirements, rules, or decisions disagree;
* `risk` — the specification remains usable but carries material uncertainty, dependency, feasibility concern, or consequence that must stay visible.

Finding type is distinct from workflow status. Multiple findings may contribute to one overall readiness decision.

## Workflow Status

Classify the validation result separately from individual finding types:

* `sufficient` — no material issue blocks the intended downstream use;
* `needs-revision` — one or more evidence-backed revisions are required before the intended downstream use;
* `needs-clarification` — stakeholder or developer input is required;
* `blocked` — required evidence or validation capability is unavailable.

When useful, report the target separately as `readiness_for`, such as stakeholder review, backlog planning, design, or implementation. Do not encode the target stage into the status itself.

## Workflow

1. Identify the specification scope, intended downstream use, sources, decisions, assumptions, conflicts, and unresolved questions.
2. Check each material requirement for evidence, clarity, consistency, singularity, verifiability, traceability, and sufficient completeness.
3. Check acceptance criteria for observable evidence and semantic alignment with their source requirement.
4. Check business rules, constraints, assumptions, dependencies, states, invariants, and non-functional requirements for contradictions, unsupported precision, duplicate obligations, and solution leakage.
5. Classify each material finding as `defect`, `ambiguity`, `gap`, `conflict`, or `risk`.
6. For each correctable defect, describe the evidence-backed revision without mutating the specification under this validation workflow.
7. Route semantic ambiguity, gaps, and unresolved conflicts to the appropriate stakeholder or developer authority.
8. Identify relationships and traceability that would require revalidation if a proposed revision is later authorized and applied.
9. Determine the overall workflow status independently from the finding type and report the actual readiness target.
10. Do not convert unresolved findings into a pass merely to keep downstream work moving.

## Output

Produce a concise validation report containing:

* overall `status`;
* optional `readiness_for`;
* findings with type, affected identifiers, evidence, and material impact;
* evidence-backed revision recommendations;
* unresolved questions or decisions;
* evidence required to resolve remaining findings.

## Boundary

Validation is read-only unless a separate command or explicit authorization permits modifying the specification. This skill may describe an evidence-backed revision but must not apply it silently.

## Stop Conditions


Stop the affected validation decision and surface the issue when:

* a material ambiguity, gap, or conflict requires authority not available to the validator;
* required source evidence cannot be obtained or inspected;
* validation would require inventing expected semantics;
* repeated validation cycles are not reducing the material findings;
* a downstream-readiness conclusion cannot be supported by evidence.
