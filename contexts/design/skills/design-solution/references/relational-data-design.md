# Relational Data Modeling — Conditional Design Reference

Use when a bounded design changes a relational schema, its constraints, or a derived read model. This is decision guidance, not a mandatory normalization ceremony or a replacement for accepted business semantics. The owning Rule is `contexts/design/rules/design.md`; record material decisions in the existing `contracts/design-evidence.md`.

## Establish facts before choosing tables

- Separate accepted business facts and invariants from the existing schema, an ORM representation, sampled rows, and implementation accidents. Missing semantics return to Requirements; do not infer a universal rule from coincidentally unique production values.
- Identify the fact's meaning, owner, lifecycle, temporal validity, intended consumers, and permitted changes. When material, establish functional dependencies `X -> Y`, **all candidate keys** (not only the declared primary key), foreign-key relationships, and independent multivalued facts.
- A dependency states a constraint on **every valid relation state**, not merely an observed correlation. Evaluate historical facts against their time context: a product's current price and the price agreed for a sold line item are different facts, not automatically a harmful duplication.
- Distinguish domain boundaries (behaviors, invariants, aggregates) from persistence boundaries (tables, keys, mappings, joins). **Never mechanically derive the domain model from the persistence schema.** Neither requires a one-to-one correspondence; a materialized read projection does not automatically create a domain entity or API resource. Simple CRUD models need no obligatory mapper/DDD ceremony.

## Relational normalization and correct decomposition

| Concern | Decision question |
| --- | --- |
| 1NF | Does the relation represent its attributes and domains appropriately, rather than hiding independently managed relationships in delimited values? Atomicity is contextual; JSON/arrays alone do not prove a violation. |
| 2NF | Does a non-prime attribute depend on a proper subset of any candidate key? |
| 3NF | For every nontrivial `X -> A`, is `X` a superkey **or** `A` prime (in some candidate key)? |
| BCNF | For every nontrivial functional dependency, is its determinant a superkey? |
| 4NF | Do independent, nontrivial multivalued dependencies require separating independent sets of facts? |
| 5NF | Are nontrivial join dependencies implied by candidate keys, and could a proposed decomposition create spurious tuples? |

For material decompositions, demonstrate **lossless join** (no missing or spurious tuples) and assess **dependency preservation** (can applicable functional constraints still be enforced without reconstructing the original join?). A lossless BCNF decomposition may fail to preserve dependencies; 3NF synthesis can preserve functional dependencies. Do not select BCNF universally or split a relation merely because more tables seem cleaner.

Counterexample: `R(A,B,C)` with `AB -> C` and `C -> B` has candidate keys `AB` and `AC`. It satisfies 3NF (B is prime) but not BCNF (C is not a superkey). The lossless decomposition `(C,B)` and `(A,C)` does not locally preserve `AB -> C`. Explicitly weigh the constraint-enforcement cost.

Normalization is **not** sufficient for business integrity. Verify applicable `PRIMARY KEY`, `UNIQUE`, `FOREIGN KEY`, `CHECK`, null semantics, transaction boundaries, concurrency control and cross-row invariants. Database-specific SQL behavior matters. Do not infer that a normal form ensures valid state transitions or exactly-once effects.

## Optimize read access only for a supported need

Before adding redundant data, capture the consumer's consistency and latency requirements, query shape, cardinality, read/write frequency, data distribution, growth, and measured query plans/resource cost when available. Consider query shape, indexing, selectivity and pagination first. Many JOINs or an unmeasured slow-query claim are not evidence that denormalization is required.

| Candidate | Appropriate when | Principal costs and conditions |
| --- | --- | --- |
| Normalized relations + tuned queries/indexes | Existing semantics and query plans meet observed or accepted needs | JOIN/aggregation cost, index and query maintenance |
| Materialized view with periodic refresh | Repeated expensive reporting/aggregation with acceptable staleness | Refresh CPU/I/O, storage, schedules, readers' freshness, locking, rebuild |
| Incrementally maintained read projection | Frequent derived reads with tighter freshness or selective changes | Event/CDC/outbox delivery, deduplication, ordering, corrections, replay, reconciliation |
| Synchronous transactional denormalization | An operational derived value is repeatedly needed and can be safely maintained atomically | Write amplification, contention, extra invariants, migration and repair |

**Materialization is a form of derived/possibly denormalized storage**, not the conceptual opposite of normalization. Different engines implement it differently:

- **PostgreSQL native materialized views:** `REFRESH MATERIALIZED VIEW` replaces the stored result by executing its defining query; no native automatic incremental refresh is implied. `CONCURRENTLY` preserves concurrent selects only under its documented prerequisites (already populated view and a qualifying all-rows unique index), permits only one concurrent refresh of a given view, and does not promise zero refresh cost or zero staleness.
- **SQL Server indexed views:** eligible indexed views are maintained when base tables change; their read benefits can impose significant DML overhead. Do not generalize their semantics to PostgreSQL or other engines.
- **Custom incremental projections:** choose synchronous or asynchronous maintenance explicitly. For asynchronous flows, define freshness/lag SLOs, idempotent processing, out-of-order/duplicate handling, correction and deletion paths, full reconstruction, reconciliation and operational ownership. A projection is not automatically an authoritative balance.

A financial limit, eligibility decision, inventory reservation, or other correctness-critical action must use authoritative, suitably isolated state (or a derived state with demonstrably equivalent transactional guarantees). A periodically refreshed dashboard snapshot is not a safe authorization source solely because its query is fast.

## Decision evidence and delivery safety

For a consequential schema or access-path change, record only what is material:

- Candidate design and compared alternatives, source semantics/dependencies/keys, constraints and preserved invariants.
- Evidence and measurement gaps: query plans, relevant p95/p99 latency, read/write rates, CPU/I/O, refresh cost, storage, staleness, contention and scale assumptions. Do not invent benchmark results.
- Ownership and propagation of derived data; acceptable freshness and reader guarantees; updates, deletions, corrections, retries and concurrent operations.
- Migration/backfill plan, mixed-version compatibility, source-of-truth cutover, reconciliation, rollback/forward-fix and rebuilding derived state.
- Falsifying tests: lossless/dependency counterexamples, historical-price distinction, stale reads, duplicated/out-of-order events, concurrent writes and missing/late refresh when applicable.

A small, proven relational change need not produce a matrix, ADR or benchmark. If business meaning is unknown, return that ambiguity to Requirements; if the performance hypothesis is unmeasured, retain it as a hypothesis rather than asserting a speedup.

## Foundations (select according to the decision)

- E. F. Codd (1970), *A Relational Model of Data for Large Shared Data Banks* — https://doi.org/10.1145/362384.362685
- Silberschatz, Korth & Sudarshan, *Database System Concepts* — https://www.db-book.com/
- C. J. Date, *Database Design and Relational Theory*, 2nd ed. (2019) — formal relational and normal-form foundations.
- PostgreSQL, *Materialized Views* — https://www.postgresql.org/docs/current/rules-materializedviews.html
- PostgreSQL, *REFRESH MATERIALIZED VIEW* — https://www.postgresql.org/docs/current/sql-refreshmaterializedview.html
- Microsoft, *Create Indexed Views* — https://learn.microsoft.com/en-us/sql/relational-databases/views/create-indexed-views
- Martin Fowler, *Data Mapper* — https://martinfowler.com/eaaCatalog/dataMapper.html

Sources describe their own systems or theories; they do not override accepted project constraints or make any particular architectural pattern mandatory.
