# HTTP API Design — Conditional Reference

Load only when the bounded Design slice creates, changes or materially assesses an HTTP API. This is **supporting interpretation**, not another Rule, mandatory template, universal REST score, authorization to change requirements, or a substitute for accepted project contracts. Refer to `contexts/design/rules/design.md` and hand off material decisions through `contracts/design-evidence.md`.

## Establish the Governing Interface

1. Identify intended consumers, existing endpoints and representations, published contract and its revision, declared architectural style (REST/hypermedia, HTTP RPC, etc.), compatibility commitments and critical domain behavior.
2. Separate **HTTP protocol semantics** from **REST architectural constraints** and from local/API-style preferences. The Richardson levels describe adoption of resources, HTTP semantics and hypermedia; they do not grade reliability, security or business suitability.
3. Apply standards to the semantics they govern, and apply JSON:API, OData, Google AIPs or vendor conventions only when actually chosen or inherited. For an existing API, characterize published behavior and affected consumers before recommending a breaking change.
4. Prefer the smallest coherent contract that satisfies demonstrated needs; preserve evidence, trade-offs, verification plan and material unknowns. Lack of a stated consumer need does not authorize adding speculative features.

## Resource Modeling and Domain Boundaries

Model the **public interface** from supported business capabilities, interactions and consumer needs before deciding resource URIs or HTTP methods. If Domain-Driven Design (DDD) is useful in the established system, examine its Bounded Contexts, ubiquitous language, Entities, Value Objects, Aggregates and invariants **as inputs to the decision**, not as an HTTP resource template. DDD is not a prerequisite for an HTTP API.

* Explore what business concept, collection, process, request, projection or other meaningful abstraction a consumer must identify or interact with. A resource may expose a stable identity while its representations and state evolve; REST's resource is a conceptual mapping, not inherently a document or a particular domain entity.
* Respect model ownership, consistency boundaries and business operations. An Aggregate defines a consistency/invariant boundary; an Aggregate Root is **not automatically** an endpoint or the only public resource, and an HTTP resource is **not automatically** an Aggregate, Entity, table, ORM model or DTO.
* Distinguish a public resource identifier from internal identity or persistence. Exposing a collection, read projection or process resource need not introduce a corresponding Aggregate Root, database table or stateful domain object.
* Where multiple Bounded Contexts or consumer-specific read models exist, weigh contract translation and independent evolution rather than exposing an internal object graph or assuming every internal object needs CRUD endpoints.
* Identify invariants and relevant domain transitions before selecting update operations. An interface can expose intent without exposing unrestricted mutation of aggregate internals. Do not impose event sourcing, CQRS, process resources or a one-to-one resource model without a supported reason.
* Preserve the established semantics of published identifiers and compatibility commitments; separate changes in resource meaning from changes in a particular representation. Escalate unsupported business meaning to Requirements instead of choosing a convenient design by convention.

**Decision prompts, not a mandatory checklist:** What capability does the consumer need? Which domain language and ownership boundaries constrain it? Which state changes need atomic consistency? What is the stable meaning of the public resource identifier? Can a view, collection or process represent the interaction without leaking internal structures? What costs and compatibility risks follow from each option?

**Illustration, not a prescribed mapping:** `/subscriptions/{id}` may expose an active subscription, `/subscriptions/{id}/invoices` a read projection, and `/subscriptions/{id}/cancellation-requests` a business request. This does **not** establish that each is a separate aggregate, or that any particular HTTP shape is required.

## HTTP Protocol Semantics

Use these as **protocol-grounded questions**, not a catalog of mandatory features. The applicable published contract may intentionally expose HTTP RPC rather than claim Fielding-style REST. RFC requirements govern the semantics they actually define; project conventions govern chosen representations and API structure within those constraints.

| HTTP concern | Semantics when applicable | Verification / design question |
| --- | --- | --- |
| GET / HEAD | GET and HEAD are safe methods; HEAD omits the content but generally mirrors GET response fields subject to HTTP exceptions. Safety does not prohibit incidental server logging. | Can a normal retrieval or automated prefetch cause an intended payment, cancellation or other unsafe action? |
| POST | Asks the target resource to process the representation. Creation is one possible outcome; 201 describes creation and Location can identify the created resource when useful. | Does the method and response truthfully describe the actual result, rather than treating POST as create-only? |
| PUT / DELETE | Idempotent method semantics apply to the **intended effect**, not to identical response status or absence of logging. PUT typically creates or replaces the target's state; DELETE removes its association. | Can repeat requests violate the stated method semantics, or is PUT silently implemented as arbitrary partial merge? |
| PATCH | RFC 5789 does not make PATCH inherently idempotent; a patch document must be applied atomically. Conditional requests may help protect concurrent updates. | Is repeat safety claimed and actually established for this patch format and behavior? |
| Status / errors | Status codes convey specific HTTP outcomes (e.g. 201 created, 202 accepted but not completed, 401 authentication challenge, 403 refusal, 412 failed precondition). RFC 9457 is an optional selected error format. | Do wire responses align with the real execution state and the accepted error contract? |
| Conditional requests | Validators and preconditions such as ETag, If-Match and If-None-Match have protocol-defined interpretation when used; ETag is **not universally mandatory**. | Could stale updates bypass the expected precondition or a validator misrepresent the chosen representation? |
| Caching / negotiation | Cache-Control, Vary, Accept and representation metadata have defined semantics when relevant, including authenticated/shared-cache boundaries. | Could an intermediary reuse a private or incompatible representation? |

## Conditional Requests and Optimistic Concurrency

Apply this reasoning **only** when a supported contract, lost-update risk or explicit HTTP precondition warrants it; an ETag is neither obligatory for every API nor evidence of concurrency safety by itself.

### Distinguish the Two Purposes

* **Cache revalidation:** a GET/HEAD with `If-None-Match` can receive `304 Not Modified` when the selected representation matches; a successful response can carry an appropriate `ETag`. Caching authorization and shared-cache isolation remain separate design decisions.
* **Lost-update prevention:** a client reads a representation and retains a **strong** ETag, then sends an update with `If-Match: "v7"`. The origin server must apply the HTTP **strong comparison** function; `W/"v7"` cannot satisfy `If-Match`. A failed precondition normally yields `412 Precondition Failed` without applying the requested mutation, subject to RFC 9110's narrow already-succeeded exception.
* **Existence is not freshness:** `If-Match: *` requires a current representation but does not assert which version was read. `If-None-Match: *` can condition creation on absence. If server policy requires a condition and it is missing, `428 Precondition Required` (RFC 6585) may apply; a domain-state conflict independent of an HTTP precondition can warrant `409 Conflict`. Follow RFC 9110 evaluation ordering and method semantics; do not treat these codes as interchangeable.

### Bind Representation Semantics to Atomic State Changes

1. Decide **what the selected public representation means** and which concurrent changes should invalidate it. A domain Aggregate version may help generate an ETag, but it is **not inherently** a strong validator for all representations, media types, content codings, field projections, authorization-dependent masks or negotiated variants. Validators must follow the actual selected representation's semantics.
2. Ensure the version check and mutation are **atomic at the authoritative write boundary**, e.g. a conditional update `UPDATE ... SET version = version + 1 WHERE id = ? AND version = ?` within a transaction that also preserves the affected domain invariants. A `SELECT` that checks a version before a separate unguarded `UPDATE` has a race window. A zero-row result also requires distinguishing stale state from missing/unauthorized resources without leaking their existence.
3. Define the client recovery behavior: on `412`, fetch current state and reconcile intent where supported; never blindly replace the ETag and replay a noncommutative update. A network timeout or replay can mean the first operation succeeded; `412` on retry is **not** proof it failed.
4. Keep separate guarantees separate: `If-Match` does not supply operation idempotency, financial deduplication, atomic cross-resource effects, outbox delivery or exactly-once execution. Consider accepted idempotency keys, transactions, uniqueness constraints and external provider behavior only when their risks apply.
5. Respect method-specific validator constraints: RFC 9110 restricts emitting an ETag in a successful **PUT** response if the received representation was transformed before storage. Do not promise a new ETag on every write irrespective of the method and actual representation semantics.

### Verification Counterexamples

For material risk, verify two concurrent requests using the same validator: only the allowed change succeeds and the resulting state satisfies invariants. Exercise missing required preconditions, stale and weak tags, mismatched variants, authorization/tenant scopes, a timeout after commit and the actual storage isolation/atomicity. Unit mocks and an `ETag` response header do not establish the write guarantee. Avoid tests that charge live payment providers.

## Architectural and Contract Design Heuristics

These concerns are **contextual choices**, not universal RFC obligations or evidence that an API has reached a particular Richardson level.

| Concern | Contextual decision | Risk to investigate |
| --- | --- | --- |
| Hypermedia and links | When the adopted REST style benefits from runtime navigation and state transitions, decide which relations, controls and media types the client needs. | Treating a few unrelated links as proof of HATEOAS, or requiring hypermedia for every HTTP RPC interface |
| Operation and representation boundaries | Map business capabilities into coherent public interactions without assuming one route per entity, table or aggregate. | Public contract exposes arbitrary internal mutation, couples consumers to persistence, or hides required business invariants |
| Compatibility and evolution | Decide which published clients, resource meanings, errors, fields and transition paths must remain supported. | Changing behavior or a response format without assessing real consumers |
| Resilience and asynchronous workflows | Where background work or external effects matter, design lifecycle/status representations, retry conditions and recovery semantics. | Returning 202 while claiming completed effects, or assuming an idempotency key alone prevents duplicate side effects |

HTTP statelessness concerns self-contained request semantics, not an instruction to avoid persisted resource state. Client-server, cacheable, layered system, uniform interface and optional code-on-demand are REST constraints with architectural trade-offs. Code-on-demand means transferable executable code, not AJAX itself.

## Distributed Effects and Safety

* For money movement, webhook processing, cancellation and other durable effects, examine duplicate/replay windows, concurrency, request-scoped idempotency and external deduplication. A header alone is not exactly-once execution.
* Bound timeout/retry budgets, including upstream provider behavior; identify authoritative terminal versus pending state. An asynchronous 202 response must not assert completion.
* Separate authentication, authorization per resource/object and property, and browser CORS. `fields` and `include` parameters must not expand access.
* Prefer secure defaults for secrets/PII; cacheability and HTTP intermediaries must honor the scope of any personalized representation.
* Do not replace the project's accepted contract or invent business semantics. Escalate unresolved requirements to Requirements; record undecided technical options instead of filling templates.

## What to Record for Material API Decisions

Within the existing `contracts/design-evidence.md` semantics, keep only consequential information: resource and operation identity, source standard/version and project contract, method/status/representation choices, authentication and authorization, compatibility and evolution, concurrency/cache semantics, failure model, key assumptions, rejected alternatives, and verification needs. Include query-collection concerns only when applicable; consult `collection-query-design.md` when it exists.

## Normative and Interpretive Sources

* [RFC 9110 — HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110.html) (ETag §8.8.3; If-Match §13.1.1; PUT §9.3.4); [RFC 9111 — HTTP Caching](https://www.rfc-editor.org/rfc/rfc9111.html); [RFC 5789 — PATCH](https://www.rfc-editor.org/rfc/rfc5789.html); [RFC 6585 — 428 Precondition Required](https://www.rfc-editor.org/rfc/rfc6585.html#section-3).
* [RFC 9457 — Problem Details](https://www.rfc-editor.org/rfc/rfc9457.html); [RFC 8288 — Web Linking](https://www.rfc-editor.org/rfc/rfc8288.html); [RFC 9700 — OAuth 2.0 Security BCP](https://www.rfc-editor.org/rfc/rfc9700.html).
* [Roy Fielding's REST dissertation, chapter 5](https://roy.gbiv.com/pubs/dissertation/rest_arch_style.htm); [Fielding on hypertext](https://roy.gbiv.com/untangled/2008/rest-apis-must-be-hypertext-driven); [Richardson Maturity Model — Martin Fowler](https://martinfowler.com/articles/richardsonMaturityModel.html).
* [OpenAPI Specification](https://spec.openapis.org/oas/latest.html); [JSON:API](https://jsonapi.org/format/); [OData 4.01](https://docs.oasis-open.org/odata/odata/v4.01/); [Google API Improvement Proposals](https://google.aip.dev/).
* [Eric Evans — Domain-Driven Design (2003)](https://www.domainlanguage.com/ddd/); [Martin Fowler — DDD Aggregate](https://martinfowler.com/bliki/DDD_Aggregate.html); [Microsoft — Map REST to DDD patterns](https://learn.microsoft.com/en-us/azure/architecture/microservices/design/api-design). Domain modeling informs boundary choices, not a prescribed one-to-one mapping.
* [OWASP API Security](https://owasp.org/API-Security/); [Microsoft REST API design guidance](https://learn.microsoft.com/en-us/azure/architecture/best-practices/api-design). These practice guides inform decisions, but are **not an automatic requirement** for every HTTP API.
