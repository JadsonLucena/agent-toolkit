# High-Risk Review Patterns

## Purpose

This is the single investigation checklist for high-risk failure mechanisms.
Apply only patterns supported by the reviewed diff and its reachable consumers.
For each applicable pattern, inspect the triggering path and attempt to **falsify**
the proposed guarantee with code, tests or observable contract evidence.

**This is an investigative heuristic, not an automatic severity score, finding,
or merge blocker.** A failed checklist item becomes a finding only with a
reachable trigger, inspected source evidence and realistic consequence.
An irrelevant pattern is not an obligation.

## Investigative Patterns

| Pattern | What to inspect | Falsification question | Typical consequence |
| --- | --- | --- | --- |
| External irreversible side effect inside a bounded transaction or lock | Calls that charge, refund, publish, send e-mail or notify a third party while a database transaction/lock is held | Can the side effect succeed, then the transaction time out or roll back, leaving no durable record of the external effect? | Duplicate delivery or irreversible effect with inconsistent local state |
| RPC/HTTP timeout and budget composition | Timeout on each remote dependency; deadline propagation; sum of retry, queue and RPC budgets versus transaction, lock and caller deadlines | Can an unbounded or cumulative remote wait outlive a lease, transaction or client deadline? | Expired lock, overlapping work, delayed failure or duplicate retry |
| Success after persistence failure | Error handling between external side effects, state persistence and response assembly; reconciliation, alerting and outbox | Can the caller receive success although durable state was not committed? Can a subsequent command operate on that inconsistent state? | Invisible partial completion, repeated effect or unrecoverable divergence |
| New state in a state machine | Every guard, negative predicate, query, integration and event consumer that assumes the old state set | Can a new state bypass an old guard such as `state != OPEN` or be interpreted as terminal/eligible incorrectly? | Invalid transitions, access leaks or inconsistent downstream behavior |
| Versioned DDL versus deployed schema | Fresh-database migration sequence, column presence, FK types/signs, nullability, deployment order and data backfill | Does the checked-in migration execute on a fresh database and produce the schema the application actually expects? | Deployment failure, data corruption or runtime schema mismatch |
| Non-idempotent or financial operation | Stable idempotency key, uniqueness boundary, retries, deduplication and claimed protection in other services | Can a timeout, concurrent call or retry trigger the same effect twice? Is external protection actually pinned and proven? | Double charge/refund, duplicate external action or data loss |
| Authentication without action/object authorization | Identity and role/allowlist checks at the operation boundary; resource ownership; scope for money/sensitive data | Can any authenticated app/client invoke a privileged action on another object's resources? | Unauthorized transfer, refund, state change or data disclosure |
| Pessimistic-lock wait longer than transaction deadline | Actual DB lock wait setting versus transaction/caller deadline and lock-busy error handling | Can the transaction expire before the intended busy-lock path runs, leaving the expected protection unreachable? | Hung transactions, wrong fallback, lock contention or duplicate work |

## Investigation Sequence

For applicable rows: (1) identify the exact changed entry point and reachable
call path; (2) state the invariant; (3) construct one concrete counterexample;
(4) inspect implementation, callers and tests for evidence; (5) classify any
finding using the severity/likelihood/confidence policy in
`contexts/review/rules/code-review.md`; (6) preserve uncertainty if the
claim depends on unavailable external runtime or repository evidence.

This checklist does not replace reviewing actual requirements, data
contracts, user-visible behavior, test assertions and rollout impact.
