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

## Knowledge Batch Size

Requirements work should proceed in the smallest coherent knowledge batch that can safely support the next material decision.

For each batch:

* identify the next decision, handoff, or planning horizon that the knowledge must support;
* gather and define only the knowledge needed to make that decision safely at the selected rigor;
* keep semantically coupled rules, scenarios, constraints, and guarantees together when splitting them would create misleading or unsafe understanding;
* defer distant detail that has no current decision value and is likely to change before use;
* expand the batch when risk, dependency, irreversibility, compliance, security, financial integrity, or critical guarantees require earlier knowledge;
* prefer learning work when uncertainty is more valuable to reduce than scope is to specify;
* revisit the next batch after validation or a material decision rather than attempting to fully specify the entire future solution up front.

Small batches reduce speculative requirements work, but batch size must not be optimized at the expense of semantic coherence or required assurance.

Requirements work must use **incremental reconciliation**: after each meaningful step, re-evaluate the resulting knowledge state against the intended next decision or readiness target before selecting another step.

Choose only the smallest coherent, safe, evidence-backed transition that reduces the material gap. Do not execute additional foreseeable downstream work merely because it is likely to be needed later.

Combine multiple changes only when separating them would leave an incoherent, unsafe, misleading, or unverifiable intermediate state. Stop when the intended state is reached or when the next transition requires missing evidence, authority, or a downstream responsibility.

## Tailoring

For the selected context:

* identify which knowledge concerns are applicable before requiring an artifact;
* record the rationale for the rigor level when the level materially changes the workflow;
* distinguish required knowledge from optional documentation form;
* scale traceability, validation, examples, reviews, and verification to the risk;
* surface both under-engineering and over-engineering;
* prefer a smaller artifact set when it represents the same knowledge with less duplication;
* prefer the smallest coherent knowledge batch that safely supports the next decision;
* avoid ceremony that has no identifiable consumer or decision value.

## Representation Conventions

When an applicable local template, schema, notation, or documentation convention already exists:

* preserve it when doing so does not compromise semantic integrity;
* distinguish representation requirements from requirements meaning;
* do not require a canonical artifact shape merely because the toolkit can produce one;
* do not fill unsupported fields or invent semantics to satisfy a template;
* surface material ambiguity when more than one local representation could apply and no selection rule is available.

A local convention may change how requirements are represented; it must not silently change what the requirements mean.

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


## Foundational Guidance

These tailoring rules synthesize risk-proportional requirements engineering, iterative requirements work, adaptive formality, and small-batch flow. The governing objective remains sufficient knowledge for the next material decision, not maximal documentation.

Foundational references used to shape this rule include:

* ISO/IEC/IEEE 29148:2018, *Systems and software engineering — Life cycle processes — Requirements engineering*.
* Klaus Pohl (2010), *Requirements Engineering: Fundamentals, Principles, and Techniques*.
* Suzanne Robertson and James Robertson (2012), *Mastering the Requirements Process: Getting Requirements Right*, 3rd Edition.
* Donald Reinertsen (2009), *The Principles of Product Development Flow*.
* Jez Humble and David Farley (2010), *Continuous Delivery*.

The flow-oriented references inform batch size, feedback, and incremental decision-making; they do not impose a delivery framework on Requirements.
