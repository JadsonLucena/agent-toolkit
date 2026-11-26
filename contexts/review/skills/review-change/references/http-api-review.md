# HTTP API Review — Conditional Investigation Reference

Use only when the frozen diff actually affects an HTTP API, its contract, or reachable consumers. The Code Review Lead retains full scope and sole verdict under `contexts/review/rules/code-review.md`. This reference is **read-only**, not a second review gate, a project-wide REST score or an automatic finding checklist. Apply only probes with a reachable path, binding evidence, a contradicted contract/norm or a demonstrated consequence.

## Establish Source Authority Before Interpretation

* Freeze actual base/head (or workspace fingerprint), affected endpoints, representation/media types, OpenAPI/specification revisions, local conventions and consumer versions.
* Identify whether the interface claims Fielding-style REST, HTTP RPC, JSON:API, OData or another declared protocol. Richardson level 3 is not a universal requirement; an absent hypermedia link is not independently a defect.
* Distinguish RFC HTTP semantics (RFC 9110, 9111, 5789) from project policy, optional standards and illustrative conventions. Existing accepted behavior can be a compatibility commitment, not permission to override a norm silently.
* Inspect code, tests and observable consumers. A declared test, schema, header or comment without exercised behavior does not establish compliance.

## Risk-selected Falsification Probes

| Risk | Counterexample to attempt | Relevant evidence |
| --- | --- | --- |
| Unsafe GET | GET, link prefetch or cache invokes requested cancellation/refund/state change | Actual handler and side effects |
| Method/idempotency mismatch | Retry or concurrency of a PATCH/POST produces undesired duplicate effects; PUT is implemented as arbitrary patch | Method intent, retry path, storage/provider boundary |
| Incorrect status/representation | Async 202 claims completion; 200 masks failure; 401/403 are inverted; 201 creation omits contractually required Location | Response paths and accepted API contract |
| ETag/concurrency | Two writers pass a non-atomic `SELECT` version check; stale or weak `If-Match` allows lost update; `If-Match: *` is mistaken for freshness | Selected representation validator, authoritative transactional write/compare-and-swap, race fixture |
| ETag/HTTP semantics | `If-None-Match` cache revalidation confused with `If-Match` updates; `412`, `428`, `409` misclassified; ETag emitted after transforming a successful PUT representation | RFC 9110/6585, HTTP handler, selected variant, observed responses |
| ETag versus idempotency | A timeout followed by stale `If-Match` is treated as proof the payment failed or that replay is deduplicated | Operation identity, transaction/outbox/provider evidence, retry trace |
| Cache and Vary | Shared cache serves another tenant's private data or wrong negotiated representation | Headers, intermediaries, auth and cache config |
| Pagination drift | Offset yields duplicates/omissions when changed data violates an explicit traversal guarantee | Ordered pages plus insert/delete trace |
| Invalid keyset | Equal timestamps are skipped; mixed sort or NULL changes predicate; mutable sort key crosses cursor | Order, tie-breaker, predicate, database plan |
| Cursor misuse | Token replay with changed filter/sort/tenant or tampering exposes a forbidden range | Token binding, signature/state, authorization |
| Filtering/sorting injection | Client field/operator reaches SQL expression without allowlist; expensive query bypasses limits | Parser, query builder, resource bounds |
| Fields and expansion | Projection or include reveals unauthorized property or object; unbounded relationship depth | Authorization and serialization behavior |
| Contract evolution | Removed field, changed sort default, cursor format or error semantics break supported clients | Approved baseline, documented versions, consumers |
| Cache/conditional performance | Revalidation or ETag claims do not reflect representation semantics | Actual validator and cache/config traces |

The correct investigation may conclude **no finding**: offset can be fit for a bounded static collection; keyset is not automatically necessary; `PATCH` may be intentionally idempotent; not every cacheable response needs ETag; not every mutation requires `If-Match`; HATEOAS is relevant only when adopted; JSON:API's `filter` family does not specify one universal filter expression language.

## Review Handoff

For each verified candidate, record changed entry point, governing contract/reference revision, minimal reproducible trigger, realistic consequence, inspected code/test evidence and counterevidence, confidence, impact, and actual file coverage. Use `contracts/review-specialist-evidence.md` for specialist handoff and `contracts/review-evidence.md` for the Lead verdict. Distinguish **not tested**, **test file exists**, **test executed** and **property enforced**. An unavailable live database or external payment provider may require INCOMPLETE for material high-risk claims, not invented verification.

## Sources to Consult Selectively

* [RFC 9110 — HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110.html), [RFC 9111 — HTTP Caching](https://www.rfc-editor.org/rfc/rfc9111.html), [RFC 5789 — PATCH](https://www.rfc-editor.org/rfc/rfc5789.html), [RFC 9457 — Problem Details](https://www.rfc-editor.org/rfc/rfc9457.html), [RFC 8288 — Web Linking](https://www.rfc-editor.org/rfc/rfc8288.html).
* [OWASP API Security](https://owasp.org/API-Security/), [Google AIP-158 Pagination](https://google.aip.dev/158), [JSON:API](https://jsonapi.org/format/), [OData 4.01](https://docs.oasis-open.org/odata/odata/v4.01/), [Use The Index, Luke!](https://use-the-index-luke.com/sql/partial-results/fetch-next-page).
