# HTTP API Design — Conditional Reference

Load only when the bounded Design slice creates, changes or materially assesses an HTTP API. This is **supporting interpretation**, not another Rule, mandatory template, universal REST score, authorization to change requirements, or a substitute for accepted project contracts. Refer to `contexts/design/rules/design.md` and hand off material decisions through `contracts/design-evidence.md`.

## Establish the Governing Interface

1. Identify intended consumers, existing endpoints and representations, published contract and its revision, declared architectural style (REST/hypermedia, HTTP RPC, etc.), compatibility commitments and critical domain behavior.
2. Separate **HTTP protocol semantics** from **REST architectural constraints** and from local/API-style preferences. The Richardson levels describe adoption of resources, HTTP semantics and hypermedia; they do not grade reliability, security or business suitability.
3. Apply standards to the semantics they govern, and apply JSON:API, OData, Google AIPs or vendor conventions only when actually chosen or inherited. For an existing API, characterize published behavior and affected consumers before recommending a breaking change.
4. Prefer the smallest coherent contract that satisfies demonstrated needs; preserve evidence, trade-offs, verification plan and material unknowns. Lack of a stated consumer need does not authorize adding speculative features.

## Protocol Semantics and State

| Concern | Design questions | Pitfall / disconfirmation |
| --- | --- | --- |
| Resource identity | What does the URI identify? Does representation/state change without changing identity? | Treating a DB row or JSON payload as the only possible resource |
| GET / HEAD | Is retrieval safe, including links and prefetching? Is HEAD consistent with GET subject to permitted header exceptions? | A GET triggers an intended cancellation, refund or payment |
| POST | Does the target process/create appropriately? For creation, is 201 and a Location useful and available? | Claiming POST can only create, or Location always required |
| PUT / DELETE | Does the effect meet the method's idempotent semantics? How are not-found, existing and created states handled? | Interpreting PUT as an arbitrary field merge |
| PATCH | Which patch media type and atomicity are promised? Is repeat safety specifically designed? | Assuming PATCH is inherently idempotent |
| Status / errors | Are 200/201/202/204, 400/401/403/404/409/412/422/429/503 applied to the actual outcome? Is RFC 9457 appropriate for the selected error format? | Returning business failure as success or treating accepted async work as completed |
| Conditional requests | Are ETag, If-Match/If-None-Match, 304/412 and optimistic concurrency needed? | Lost update or incorrectly treating ETag as mandatory for all responses |
| Caching | Which representations and intermediaries may reuse a response? Cache-Control, Vary, authorization and privacy implications? | Shared cache mixing tenants or representations |
| Links / hypermedia | Do clients benefit from runtime navigation and state transitions? Are relation/media types documented? | Assuming a few related links prove HATEOAS |
| Evolution | Which clients and revisions must remain compatible? How are deprecation, migration and sunset communicated? | Changing a response or cursor semantics without consumer evidence |

HTTP is stateless **per request**, not an instruction to avoid persisted resource state. Client-server, cacheable, layered system, uniform interface and optional code-on-demand are REST constraints with architectural trade-offs. Code-on-demand means transferable executable code, not AJAX itself.

## Distributed Effects and Safety

* For money movement, webhook processing, cancellation and other durable effects, examine duplicate/replay windows, concurrency, request-scoped idempotency and external deduplication. A header alone is not exactly-once execution.
* Bound timeout/retry budgets, including upstream provider behavior; identify authoritative terminal versus pending state. An asynchronous 202 response must not assert completion.
* Separate authentication, authorization per resource/object and property, and browser CORS. `fields` and `include` parameters must not expand access.
* Prefer secure defaults for secrets/PII; cacheability and HTTP intermediaries must honor the scope of any personalized representation.
* Do not replace the project's accepted contract or invent business semantics. Escalate unresolved requirements to Requirements; record undecided technical options instead of filling templates.

## What to Record for Material API Decisions

Within the existing `contracts/design-evidence.md` semantics, keep only consequential information: resource and operation identity, source standard/version and project contract, method/status/representation choices, authentication and authorization, compatibility and evolution, concurrency/cache semantics, failure model, key assumptions, rejected alternatives, and verification needs. Include query-collection concerns only when applicable; consult `collection-query-design.md` when it exists.

## Normative and Interpretive Sources

* [RFC 9110 — HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110.html); [RFC 9111 — HTTP Caching](https://www.rfc-editor.org/rfc/rfc9111.html); [RFC 5789 — PATCH](https://www.rfc-editor.org/rfc/rfc5789.html).
* [RFC 9457 — Problem Details](https://www.rfc-editor.org/rfc/rfc9457.html); [RFC 8288 — Web Linking](https://www.rfc-editor.org/rfc/rfc8288.html); [RFC 9700 — OAuth 2.0 Security BCP](https://www.rfc-editor.org/rfc/rfc9700.html).
* [Roy Fielding's REST dissertation, chapter 5](https://roy.gbiv.com/pubs/dissertation/rest_arch_style.htm); [Fielding on hypertext](https://roy.gbiv.com/untangled/2008/rest-apis-must-be-hypertext-driven); [Richardson Maturity Model — Martin Fowler](https://martinfowler.com/articles/richardsonMaturityModel.html).
* [OpenAPI Specification](https://spec.openapis.org/oas/latest.html); [JSON:API](https://jsonapi.org/format/); [OData 4.01](https://docs.oasis-open.org/odata/odata/v4.01/); [Google API Improvement Proposals](https://google.aip.dev/).
* [OWASP API Security](https://owasp.org/API-Security/); [Microsoft REST API design guidance](https://learn.microsoft.com/en-us/azure/architecture/best-practices/api-design). These practice guides inform decisions, but are **not an automatic requirement** for every HTTP API.
