---
description: "Govern read-only, evidence-based investigation of observed technical failures, causal uncertainty, authority boundaries and proportionate escalation."
alwaysApply: false
---

# Debugging Rules

## Scope and Causal Integrity

* Debugging investigates observed deviations between expected and actual software behavior. It does not own business intent, architectural approval, code remediation, test creation, Code Review verdicts or delivery milestones.
* Establish the source of expected behavior. Distinguish stakeholder report, inspected observation, erroneous state, candidate defect, contributing factor, hypothesis and supported causal mechanism. An ambiguous expectation is not automatically a software defect.
* Record source and environment identity, time window, inspected evidence and counterevidence when material. Do not present an unexecuted experiment or uninspected log reference as observed fact.
* Prefer reproductions and discriminating contrasts, but absence of deterministic reproduction does not invalidate intermittent or distributed failures. Identify observable predictions and competing explanations.
* Scale depth with impact, uncertainty and information value. When attempts produce no new evidence, revisit the strategy or seek new expertise; three failed attempts do not prove defective architecture.
* Report `confirmed`, `probable`, `inconclusive` or `blocked` diagnosis. Confirm only a mechanism demonstrably supported within its observed scope; confidence is not impact or severity.

## Safety and Authority

* Default to read-only inspection of authorized files, Git history, existing tests, logs and traces. Do not edit production code, tests, specifications, configuration, Git state or infrastructure as part of diagnosis.
* A test run, telemetry query, reproduction, instrumentation or external call may have side effects. Before execution, assess permissions, isolation, costs, private data and potential writes; request separate scoped approval when effects are not demonstrably safe. Otherwise report a proposed, not-run experiment.
* Prefer bounded/redacted telemetry. Do not expose secrets, payment data or personal information for diagnostic convenience. Tools with broad permissions do not expand invocation authority; runtime enforcement must be verified or the unsafe capability withheld.
* Urgent mitigation options may be identified but may only be executed by separately authorized operational owners. Recommendations never authorize Implementation, Testing, Design, Requirements, Git, Review or deployment operations.
* Cross-context consumers receive `contracts/debugging-evidence.md` and must revalidate source freshness. Debugging cannot issue or change a Review PASS/FAIL, stakeholder decision or accepted specification.

## Foundational Guidance

Andreas Zeller, *Why Programs Fail* (experimental causal investigation); David Agans, *Debugging: The 9 Indispensable Rules* (disciplined evidence gathering); and Google SRE, *Effective Troubleshooting* (distributed-system hypotheses) motivate these principles. Superpowers systematic-debugging informs conditional tactics, not mandatory test-first remediation or a fixed three-patch architectural conclusion.
