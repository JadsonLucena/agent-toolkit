# Causal Tracing Across Boundaries

Use when an observed invalid state appears far from its introduction, or a request/event crosses multiple components. This is a selective technique, not a requirement to instrument every service.

## Backward Trace

1. Identify the **first observed wrong state**, its expected invariant and the evidence tying it to a particular revision and execution.
2. Trace the value or event backward through its producer, callers, state transitions, queue messages and database operations. For each boundary, distinguish what entered, what left and what was persisted.
3. Correlate by a trustworthy request/trace/business-operation identity; a matching timestamp alone does not prove that two events belong to the same causal chain. Prefer existing tracing or structured logs.
4. Inspect version and configuration provenance at each material boundary. Compare working instances or transactions only when meaningful.
5. Select the earliest evidenced divergence that explains the downstream failure. Record uninspectable hops and alternate explanations instead of asserting a complete trace.

## Controlled Instrumentation

Read existing telemetry first. Additional logging, injected spans, test probes, live queries, or changing trace sampling can introduce privacy exposure, traffic and writes; propose them as separate experiments when authorized isolation is unavailable. Never log credentials, payment instruments or personal data. Minimize retention and scope.

## Handoff

Return source-linked call/event chain, causal mechanism or hypotheses, missing edges, contrary evidence and `contracts/debugging-evidence.md` references. Fix placement and changes belong to the receiving authorized context.
