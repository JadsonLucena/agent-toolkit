# Reliability Review — Conditional Investigation Reference

Use when a **changed, reachable operation** has a credible data-integrity, concurrency,
availability, fault-containment or recovery risk. This is a risk-selected falsification
aid within a single read-only Review, not an independent gate, universal checklist or
reason to demand resilience patterns by name. The Lead retains full changed-file
coverage and sole verdict under `contexts/review/rules/code-review.md`.

## Investigation Protocol

1. **Name the operation and guarantee.** Identify the changed entry point and
   affected consumer; state the protected invariant or service objective (e.g.,
   payment uniqueness, durable handoff, bounded work, recovery). Apply actual
   documented SLOs/SLIs if available; do not invent a target or equate HTTP 200
   with a completed business outcome.
2. **Select a credible failure.** Inspect before/during/after an effect: remote
   timeout, response loss, crash, concurrent execution, reordering, dependency
   degradation, overload or restart, only if applicable to the changed path.
3. **Trace a bounded counterexample.** Follow caller -> dependency/queue ->
   persistence/external effect -> retry/ACK -> observed result. Record relevant
   IDs, state, deadlines, transaction boundaries and ordering without assuming
   wall-clock ordering across hosts.
4. **Seek protections and counterevidence.** Inspect shared clients, SDK retry
   defaults, gateways/proxies, broker settings, database constraints, locks,
   callers, consumers, tests and pinned external contracts before asserting a
   missing safeguard. Note deployment-only behavior as unverified if inaccessible.
5. **Assess the residual consequence.** Consider blast radius, duration,
   affected workflows, fault isolation, detectability, safe recovery and realistic
   exposure. Separate observed/verified failure, source-backed risk, unresolved
   material question and advisory improvement.
6. **Report and hand off.** Include the trigger, minimal failure timeline,
   inspected protections/counterevidence, realistic consequence and smallest
   validation or corrective action under the existing specialist evidence
   contract; assign severity/likelihood/confidence only via the Review Rule.

## Risk-Selected Counterexamples

| Changed surface | Failure to attempt to falsify | Evidence that may defeat the hypothesis |
| --- | --- | --- |
| Remote RPC/HTTP | Timed-out attempt succeeds remotely and a retry duplicates an effect | Stable provider idempotency scope, outcome reconciliation and bounded retry policy |
| Nested client/SDK retries | Independent layers multiply calls during an outage | Measured/configured retry ownership, bounded budgets, backoff and jitter |
| Queues and async handlers | Crash after early ACK loses work, or redelivery duplicates an effect | Durable ACK ordering, broker semantics, atomic state transition and idempotent consumer |
| DLQ and poison messages | Terminal work accumulates without diagnosis, safe replay or retention | Documented recovery ownership, alertable backlog age and idempotent replay |
| Database + event publication | Commit succeeds but process exits before event publication | Transactional outbox or equivalent durable publication guarantee |
| Shared state and leases | Two workers pass check-then-act or a stale lease holder still writes | Atomic uniqueness/compare-and-swap, fencing and downstream enforcement |
| Bounded service operation | Slow dependency outlives caller/transaction/lease budget | End-to-end deadlines, propagated cancellation and bounded cleanup |
| Worker lifecycle | Shutdown/crash strands in-flight work or runs it twice after restart | Persisted checkpoint, lease recovery, deduplication and shutdown behavior |
| Shared pools/queues | A failing dependency retains all threads/connections or creates unbounded work | Effective resource limits, admission control, isolation, backpressure/load shedding |
| Fallback or cache | Dependency failure silently returns misleading success or unsafe stale state | Explicit degraded contract, invariant preservation and source-of-truth checks |
| Rollout or migration | Coexisting versions misread messages/state or rollback cannot undo effects | Version compatibility, expansion/contraction and compensating/reconciliation plan |
| Recovery and observability | Failure remains silent or cannot be correlated/reprocessed | Relevant alerts/metrics, operation IDs, reconciliation paths and runbook evidence |

Each row is **conditional**. A retry, queue, fallback, circuit breaker, bulkhead,
SLO, chaos test or other pattern is never universally required. A safe rejection
or explicit failure may be more reliable than a misleading fallback. A timeout
does not prove the remote side failed or was cancelled. Exactly-once delivery
claims do not automatically cover external side effects. Rollback of code does
not undo durable events, writes or money movement.

## Specialist Collaboration

* **Correctness:** state transitions, semantic invariants and actual result paths.
* **Architecture:** dependency boundaries, isolation, rollout and operational compatibility.
* **Testing:** whether assertions would detect the identified failure trace;
  do not demand chaos/load tests without a credible need and safe authorization.
* **Security:** integrity or abuse consequences that cross trust boundaries.

One defect gets one primary owner and independently verified finding, not
duplicate findings across peers. If a deployment contract or mitigation is
external, follow the Review Rule's pinned external-evidence discipline. Where
evidence is missing, report the exact assumption and its materiality; absence
of a local timeout, circuit breaker, retry or alert is not proof of a defect.

## Selective Foundations

Google *Site Reliability Engineering* (overload, cascading failures and SLOs),
Nygard *Release It!* (stability and isolation), Kleppmann *Designing
Data-Intensive Applications* (distributed fault/consistency semantics), AWS
Builders' Library (retries, jitter and idempotent APIs), and ISO/IEC 25010:2023
(reliability characteristics). These sources motivate investigation; they are
not unconditional project policies.
