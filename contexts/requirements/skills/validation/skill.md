# Requirements Validation

## Purpose

Use as a read-only quality gate for requirements knowledge before a downstream decision. Evaluate whether the available knowledge is sufficiently correct, coherent, traceable, and verifiable for the intended next step at the selected rigor.

Do not judge quality by document count.

## Uses

* Rule: `contexts/requirements/rules/tailoring.md`
* Rule: `contexts/requirements/rules/requirements.md`
* Contract: `contracts/requirements.md`

## Finding Taxonomy

Classify each material finding by what was discovered:

* `defect` — the specification contradicts supported evidence, its own semantics, or an applicable rule and an evidence-backed revision can be described without inventing stakeholder intent;
* `ambiguity` — multiple materially different interpretations remain plausible;
* `gap` — knowledge required for the intended downstream use is absent;
* `conflict` — supported sources, requirements, rules, or decisions disagree;
* `risk` — the knowledge remains usable but carries material uncertainty, dependency, feasibility concern, or consequence that must stay visible;
* `waste` — representation or process appears duplicative, unused, prematurely detailed, or disproportionate to the decision and risk.

Missing documentation is not automatically a `gap`; first determine whether the required knowledge is represented elsewhere.

## Finding Severity

Classify impact independently from finding type:

* `critical` — substantial risk of building the wrong thing, financial harm, security/privacy/compliance breach, data loss, or a fundamental contradiction;
* `high` — significant risk of major rework, divergent interpretation, unsuitable architecture, lost value, or inability to validate;
* `medium` — important improvement, but work may proceed with the issue visible;
* `low` — clarity or maintainability refinement;
* `info` — observation or future opportunity.

Severity is not a confidence score.

## Workflow Status

Classify the overall result independently from individual findings:

* `sufficient` — no material issue blocks the intended downstream use at the selected rigor;
* `needs-revision` — one or more evidence-backed revisions are required before the intended downstream use;
* `needs-clarification` — stakeholder or developer input is required;
* `blocked` — required evidence or validation capability is unavailable.

Report the downstream target separately as `readiness_for`.

## Workflow

1. **Establish validation context.**
   * Identify the intended next decision, supplied artifacts/evidence, rigor profile, applicable concerns, sources, decisions, assumptions, conflicts, and open questions.
   * If no rigor profile exists and rigor materially changes what "sufficient" means, assess the context before judging completeness.

2. **Validate tailoring.**
   * Check whether the selected rigor is proportional to business/customer/financial impact, security, privacy, compliance, complexity, integrations, teams, migration, reversibility, uncertainty, and solution lifetime when relevant.
   * Identify both under-engineering and over-engineering.
   * Do not fail a concern merely because a preferred document type is absent.

3. **Validate strategic framing when applicable.**
   * Check Need, Business Goal, success evidence, Current/Future State, material gaps, Work Scope, Product Boundary, transition needs, and candidate-solution assumptions.
   * Detect solution-first statements, output presented as outcome, and software scope assumed without support.

4. **Validate requirements and business knowledge.**
   * Check each material requirement for evidence, necessity, rationale, scope, clarity, consistency, singularity, feasibility status, verifiability, traceability, and sufficient completeness.
   * Check domain terms, facts, business rules, governance, constraints, assumptions, unknowns, options, dependencies, states, invariants, and scenario semantics where applicable.
   * Check functional, data, quality, security, interface, operational, and transition semantics at the depth required by the selected rigor.
   * Check acceptance and fit evidence for observable behavior and justified precision.

5. **Validate the Use-Case set when Use Cases are a material representation.**
   * Check whether relevant actors and actor goals are covered without requiring a Use Case for every requirement.
   * Detect materially missing actor goals, duplicated goals, inconsistent goal levels, scope inconsistencies, artificial CRUD/technical mini Use Cases, and oversized Use Cases that combine distinct goals.
   * Check whether meaningful alternatives or exceptions required for the intended downstream decision are represented.
   * Apply this review only when Use Cases are actually part of the requirements model.

6. **Validate cross-artifact consistency when the corresponding artifacts exist.**
   * Need/Goal ↔ Requirements.
   * Rules/Policies ↔ Requirements/Use Cases/Scenarios.
   * Requirements ↔ quality/security constraints.
   * Requirements/Use Cases ↔ slices/work items.
   * Rules/Requirements ↔ examples/test basis.
   * Requirements ↔ design/architecture references.
   * Requirements ↔ implementation/test evidence.
   * Success metrics ↔ production/outcome evidence.
   * Identify contradictions, drift, duplicated knowledge, and orphan relationships.

7. **Validate uncertainty and solution decisions.**
   * Surface implicit assumptions, unresolved unknowns, expiring options, unsupported thresholds, and hidden design decisions.
   * Distinguish a missing requirement from a legitimate downstream design choice.
   * Distinguish candidate solution evidence from accepted requirement semantics.

8. **Classify findings.**
   * Assign finding type and severity.
   * Describe evidence, affected identifiers/relationships, material impact, and the smallest evidence-backed remediation.
   * For a correctable defect, describe the revision but do not mutate the specification.

9. **Determine readiness.**
   * Identify relationships that would require revalidation if a recommended revision is later authorized and applied.
   * Determine overall status for the actual `readiness_for` target.
   * Do not convert unresolved findings into a pass merely to keep work moving.
   * Do not require unrelated knowledge merely because the framework knows how to model it.

## Output

Produce a concise validation report containing:

* selected or assessed rigor and rationale when material;
* overall `status` and `readiness_for`;
* applicable concerns evaluated;
* findings with type, severity, affected identifiers, evidence, impact, and remediation;
* cross-artifact contradictions, drift, duplication, and orphan relationships when present;
* missing **knowledge**, not merely missing documents;
* premature solution decisions and implicit assumptions when present;
* evidence-backed revision recommendations;
* unresolved questions/decisions and evidence needed to resolve them;
* prioritized actions, distinguishing blockers from improvements that can proceed incrementally.

## Boundary

Validation is read-only unless a separate command or explicit authorization permits modifying the specification or another artifact. This skill may describe an evidence-backed revision but must not apply it silently.

## Stop Conditions

Stop only the affected validation decision and surface the issue when:

* a material ambiguity, gap, or conflict requires authority not available to the validator;
* required source evidence cannot be obtained or inspected;
* validation would require inventing expected semantics;
* the selected rigor cannot be justified and that uncertainty changes readiness;
* repeated validation cycles are not reducing the material findings;
* a downstream-readiness conclusion cannot be supported by evidence.
