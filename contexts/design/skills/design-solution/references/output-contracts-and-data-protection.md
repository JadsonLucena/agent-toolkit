# Output Contracts and Data Protection — Conditional Design Reference

Use when a bounded change materially creates, changes or assesses a consumer-facing representation or protected-data disclosure. HTTP is **not** required. This is supporting Design interpretation, not a mandatory Clean Architecture layer, legal determination, new acceptance contract or permission to change Requirements. Preserve material decisions in `contracts/design-evidence.md`.

## Determine the Supported Output Contract

1. Identify the caller/recipient, purpose, existing published representation, accepted business and access policies, affected channels and compatibility commitments. If any policy or purpose is materially unknown, return the question to Requirements or the policy owner; do not invent entitlement.
2. List consumer-required attributes and their precision; distinguish public contract identity from domain entities, aggregate internals, persistence models and ORM graphs. Prefer explicit field selection/allowlisting at the outward boundary when accidental disclosure is plausible.
3. Evaluate absence before transformation: **omit** unnecessary data; otherwise use the smallest authorized disclosure (e.g. generalized, masked or complete) supported by the use case. A masked value is often still personal data; do not assert masking, pseudonymization, encryption or tokenization is legal anonymization.
4. Verify **object-level and property-level authorization** before data reaches an untrusted recipient; `fields`, `include`, nested links, GraphQL selection and serializers must never enlarge entitlement. Domain invariants and authorization policy remain authoritative even if the output adapter formats results.
5. Follow the data across relevant boundaries: HTTP body/headers, pagination and error responses, logs, traces, metrics labels, event payloads, exports, caches and downstream services. Consider tenant scope, access lifetime and intermediate redaction, not just frontend rendering.

## Presenter Versus Authorization

In *Clean Architecture*, an Output Boundary/Output Port allows a Use Case Interactor to supply output data to a Presenter (an Interface Adapter), which builds an audience-specific ViewModel. The **source-code dependency** direction remains inward through abstractions; the flow of output data does not mean domain code depends on a presenter framework.

This is one possible realization, **not** a universal class/DTO/interface count:
- Use a dedicated Presenter where use-case/application output must be adapted to materially different consumer representations or formatting policies.
- Use an explicit response DTO, mapper, serializer or existing adapter when it provides the needed decoupling and verification with less indirection.
- Keep business rules, entitlements and consistency invariants in their owning layers. A Presenter can enforce an already-approved redaction policy at the output boundary, but **cannot grant access** or replace upstream authorization.
- If an internal model changes, it must not silently enlarge the public contract. Forbid indiscriminate entity/ORM serialization where sensitive or internal attributes could leak.

**Illustrative, not prescribed:** An authorized subscription summary may expose status and next billing date, mask a contact address for an approved limited-view audience, and omit payment tokens, full identity documents and internal fraud scores. This does not prescribe a `SubscriptionPresenter` class or establish business entitlement to the address.

## Classification, Minimization and Protection

- PII is personally identifiable information. SPII (*sensitive personally identifiable information*) is context-dependent terminology in some security programs; do **not** equate it with the LGPD-defined Brazilian category `dado pessoal sensível`. Classification must follow the actual jurisdiction and organization policy, considering combinations, linkability and harm.
- Distinguish omission, generalization, **masking** (partial display), pseudonymization (linkability remains) and genuine anonymization (requires evaluating re-identification risk under the applicable definition). Do not describe a partially redacted CPF/e-mail as automatically anonymous.
- Do not assume every personal-data field must be masked; authorized full disclosure can be necessary. Nor does masking make unauthorized disclosure safe. Apply purpose limitation, necessity, least privilege, and applicable retention/security obligations proportionally.
- Coordinate per-consumer representations and shared-cache policies: a private response, role-dependent fields or masking can affect `Cache-Control`, `Vary`, conditional validators and cache keys. Do not assume an internal aggregate version uniquely identifies all public representations.
- Record material trade-offs, caller/field policy decisions, transformation rules, observed exposure paths, compatibility needs, and verification scenarios; do not create a second requirements/Design contract.

## Selective Evidence and Sources

* [Robert C. Martin — The Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html) and *Clean Architecture* (2017), on separating use cases from interface adapters.
* [OWASP API Security Top 10 API3:2023](https://owasp.org/API-Security/) — broken object property level authorization; [OWASP Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html).
* [NIST SP 800-122](https://csrc.nist.gov/pubs/sp/800/122/final) — PII confidentiality protection; [Brazil LGPD, Lei 13.709/2018](https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709compilado.htm), including Arts. 5–6. External frameworks inform decisions only where applicable.
