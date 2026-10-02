# Requirements Tailoring Rules

## Principle

Apply **just enough requirements, with sufficient rigor for the risk**.

The objective is not to maximize the number of artifacts. The objective is to establish enough correct, coherent, traceable, and verifiable knowledge to make the next decision safely without unnecessary work.

Do not treat absence of a document as absence of knowledge when the required knowledge is adequately represented elsewhere.

## Context Assessment

Before deciding how much requirements work is needed, consider the material risk and uncertainty of the change, including when relevant:

* business criticality and customer impact;
* financial impact;
* security and privacy;
* compliance or regulation;
* domain and technical complexity;
* distributed-system behavior and number of integrations;
* number of teams or organizational boundaries;
* migration, legacy, or transition complexity;
* reversibility of important decisions;
* uncertainty and expected learning;
* expected frequency of change;
* expected lifetime of the solution.

Do not infer a higher rigor level from implementation size alone.

## Rigor Levels

Use one of these semantic rigor levels when a rigor classification is useful:

### Lightweight

Use when the change is low risk, well understood, locally scoped, readily reversible, and inexpensive to validate.

Prefer the smallest representation that preserves the required knowledge.

### Standard

Use when material ambiguity, integration, business impact, multiple rules, non-trivial quality concerns, or coordination makes explicit requirements and traceability useful.

This is the default only when evidence supports it; do not select it merely by habit.

### High Assurance

Use when failure could cause substantial financial loss, security or privacy harm, compliance breach, data loss, irreversible damage, or similarly high consequences.

High Assurance should increase evidence, review, traceability, verification, and change discipline only where those controls reduce actual risk. Do not use it by default.

## Tailoring

For the selected context:

* identify which knowledge concerns are applicable before requiring an artifact;
* record the rationale for the rigor level when the level materially changes the workflow;
* distinguish required knowledge from optional documentation form;
* scale traceability, validation, examples, reviews, and verification to the risk;
* surface both under-engineering and over-engineering;
* prefer a smaller artifact set when it represents the same knowledge with less duplication;
* avoid ceremony that has no identifiable consumer or decision value.

## Governance

When material, establish:

* who has authority to clarify or approve stakeholder intent;
* who has authority to change critical business rules or constraints;
* how requirements will be validated;
* how material changes will be recorded and propagated;
* what traceability is necessary for the selected rigor;
* what evidence must exist before the next irreversible or high-risk decision.

## Guardrails

* Do not classify missing knowledge as not applicable merely because a document is absent.
* Do not require every known requirements technique for every change.
* Do not use High Assurance as a synonym for more paperwork.
* Do not lower rigor merely because implementation is urgent.
* Do not preserve obsolete or redundant artifacts solely because a process template expects them.
