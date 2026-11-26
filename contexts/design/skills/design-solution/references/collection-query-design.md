# Collection Query Design — Conditional Reference

Use only when Design is making a material decision about an HTTP collection's filtering, ordering, pagination, projection or expansion. This is supporting decision guidance under `contexts/design/rules/design.md`, **not** an independently enforced policy or an instruction to rewrite an accepted API. Record approved choices and open needs through `contracts/design-evidence.md`. Requirements owns consumer guarantees; Implementation owns the realization.

## Start With Consumer Guarantees

Capture only decision-relevant facts: collection size and growth, mutation/update patterns, need for numbered pages or sequential traversal, acceptable duplicates/omissions, snapshot or export obligations, target database and indexes, latency and cost bounds, security/tenant scope, compatible clients and published syntax.

Do **not** infer that a public collection must use keyset or that a small internal collection needs opaque cursors. A query parameter spelling is a contract choice, not a REST requirement.

## Pagination Decision

| Strategy | Fits | Limitations / falsification probes |
| --- | --- | --- |
| `page` / `pageSize` | Human UI with explicit page numbers, modest stable datasets | Commonly offset underneath; large page numbers may discard many rows; concurrent writes can shift membership |
| `limit` / `offset` | Simple bounded or nearly static collections, random positioning | Scan/skip cost; inserts/deletes before an offset can duplicate/skip rows |
| Cursor | Clients navigate opaque continuation tokens | Cursor alone says nothing about DB strategy; bind to query/authorization context and document expiry/invalid-token behavior |
| Keyset / seek | Large ordered collections, forward sequential navigation, adequate composite indexes | Needs deterministic total order and stable seek predicate; not arbitrary direct page access |
| Time window + cursor | Events, temporal partitioning, exports | Timestamp collisions, late arrivals and mutable sort keys need a tie-breaker/watermark or other explicit handling |
| Snapshot / asynchronous export | Audit/reconciliation requiring a fixed set | Snapshot semantics require real storage or materialization guarantees and resource/expiry handling |

A cursor is an API-level continuation contract; keyset is a query technique. Offset is not automatically wrong; keyset alone is **not** snapshot isolation. A temporal window can bound a query without solving pagination within the window.

## Deterministic Ordering and Keyset

* Declare default sort order even when the client does not supply one. A nonunique key (such as `createdAt`) requires a stable, unique tie-breaker (such as `id`) when a total order matters.
* For `ORDER BY createdAt DESC, id DESC`, continue with `createdAt < :last_createdAt OR (createdAt = :last_createdAt AND id < :last_id)`; consider database row-value expressions where supported. The last key must describe the final **returned** record, not an extra lookahead row.
* Mixed ascending/descending order, NULL placement, collations, type precision and mutable sort columns change the seek predicate; do not copy a DESC example blindly.
* Examine index compatibility, real query plans, data distribution and the storage engine. An in-memory test or index presence alone does not prove performance.
* For bidirectional navigation, specify reverse ordering/cursors and stable semantics, not merely decrementing offset.
* Use page-size caps and a well-defined empty page and end-of-collection result. A `limit + 1` query can establish `hasMore`; exact `totalCount` is optional and potentially expensive.
* Reordering or filtering a live mutable collection may still cause omission/duplication under keyset; if the consumer needs a fixed membership, explore snapshot, version boundary or export.

## Sorting, Filtering, Fields, Relationships

* Sorting: choose a documented syntax and allowed fields/directions; define default order, ties, nulls and errors. Never interpolate raw client-provided sort expressions into SQL.
* Filtering: start with explicit allowed fields and operators (`eq`, `gte`, `lt`, `in`, etc.) supported by consumer needs. For more expressive queries, weigh language/parsing cost, operator precedence, nesting, indexes and resource limits.
* Time filters: define units, timezone, inclusive/exclusive bounds (often `[from,to)`), field meaning (`createdAt` versus `paidAt`) and precision.
* Field projection (`fields` / sparse fieldsets) chooses attributes, not records. Define identity and required fields, omitted versus null semantics, validation and property-level authorization. Do not project disallowed fields merely because they exist in persistence.
* `include` / `expand` is distinct from `fields`; bound relationship depth, fan-out and cost, and authorize every exposed object/property.
* Combine filtering and authorization **before** pagination; bind cursor to scope, filters, order and (where needed) projection and version. Decide whether page-size changes are allowed. Opaque base64 is encoding, not tamper protection.
* Define count semantics (exact/estimated/omitted), invalid or expired token behavior, cursor versioning, maximum query complexity and migration compatibility.

## Traceable Design Examples

**Stable, bounded admin list:** numbered `page` with total count if needed for a UI, a deterministic order and an offset/deep-page limit if justified.

**Large invoice history:** `sort=-createdAt,-id`, keyset and opaque cursor with fixed filter/authorization context; if finance requires completeness at a point in time, add an independently justified snapshot/export mechanism.

**Real-time event sync:** temporal window plus cursor, with a strategy for late/mutable events; a wall-clock timestamp alone may not provide correct incremental sync.

Record in existing design evidence the chosen strategy, query syntax, sort/cursor keys, guardrails, affected consumers, supported guarantees, index/performance assumptions, alternative considered and the testable counterexample that would refute the choice. Leave unverifiable claims unresolved.

## Standards vs Patterns

* [Google AIP-158 Pagination](https://google.aip.dev/158), [AIP-132 List](https://google.aip.dev/132), [AIP-160 Filtering](https://google.aip.dev/160), [AIP-157 Partial Responses](https://google.aip.dev/157): a specific guidance family; not universal HTTP semantics.
* [JSON:API 1.1](https://jsonapi.org/format/): `sort`, `fields[TYPE]`, `include`; `page` family without prescribing the pagination algorithm; filtering family without one universal expression language.
* [OData 4.01 URL Conventions](https://docs.oasis-open.org/odata/odata/v4.01/os/part2-url-conventions/odata-v4.01-os-part2-url-conventions.html): selected query protocol including `$filter`, `$orderby`, `$select`, `$expand`, `$top` and `$skip`.
* [Markus Winand — Fetching the Next Page](https://use-the-index-luke.com/sql/partial-results/fetch-next-page): SQL offset vs seek performance analysis; verify against the actual DB.
* [RFC 8288 Web Linking](https://www.rfc-editor.org/rfc/rfc8288.html): `rel="next"` is useful when the chosen contract supports navigation links.

Choose one coherent protocol/convention, not an accidental mix of incompatible formats. In particular, adopting JSON:API implies its full applicable media type and document rules; reusing `sort=-createdAt` alone does **not** establish JSON:API compliance.
