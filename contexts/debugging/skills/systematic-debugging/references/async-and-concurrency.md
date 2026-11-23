# Async, Timing and Concurrency Diagnosis

Select when failure depends on message ordering, non-deterministic timing, shared state, retry, duplicate processing, cancellation or distributed delivery. Do not require this technique for ordinary synchronous defects.

## Investigation

1. Establish the correctness invariant and supported timing semantics (event order, deadlines, cycles, deduplication, transaction boundaries and external effects). If product timing semantics are disputed, return that decision to Requirements.
2. Build a **bounded event timeline**: emit/receive/acknowledge, process, persist, retry, external side effect and observable failure. Record missing or reordered events and the actual correlation identities. Avoid assuming wall-clock ordering across hosts.
3. Compare successful and failing executions, including races around check-then-act, transaction commits, lease expiry and at-least-once delivery. A retry or duplicate is not automatically a bug unless it violates a supported guarantee.
4. Prefer isolated deterministic scheduling, fakes, controlled clocks or replay when available and authorized. Never replay a charge, send real messages or alter queue consumers in production to demonstrate the issue.
5. For flaky tests, prefer waiting for an **observable condition** with a bounded timeout to arbitrary `sleep`. This applies when testing completion rather than the passage of time; use controlled clocks for debounce/throttle behaviors. The check must read fresh state, avoid uncontrolled polling and preserve failure diagnostics.
6. Identify the smallest causal explanation supported by the experiment; a passing stress run is not proof of absence of races.

## Safety and Escalation

Repeated attempts without new timing evidence call for a different experiment or capability, not another speculative patch. If no safe reproduction exists, retain `intermittent` or `not-attempted` and propose telemetry/experiment requirements for an authorized owner.
