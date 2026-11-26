# Output Disclosure and Data Protection — Review Investigation

Select only when a frozen diff affects outbound contracts, sensitive data or reachable disclosure channels. The Code Review Lead owns the risk classification and single verdict under `contexts/review/rules/code-review.md`. This is a **read-only falsification aid**, not another review gate or a mandatory Presenter pattern.

| Possible defect | Falsifiable counterexample | Evidence to inspect |
| --- | --- | --- |
| Accidental property exposure | Adding an ORM field exposes it through default serialization or a nested relationship | Controller/output mapping, serializer config, actual response |
| Broken property-level authorization | Caller with legitimate object access receives a restricted field through `fields`, `include` or alternate endpoint | Authorized roles, query projections, integration tests and accepted policy |
| Masking mistaken for access control | Restricted PII reaches an unauthorized caller but is only masked in a browser component | Backend payload and caller-specific response contract |
| Cross-channel disclosure | HTTP response is protected but a reachable log, error, trace, event, export or cache contains the complete value | Actual code path, error/log capture, event schema and cache policy |
| False anonymity | Partial CPF/e-mail or reversible token is claimed to be anonymous without re-identification assessment | Data flow, context and applicable classification |
| Presenter overengineering | Reviewer demands Presenter/OutputBoundary classes despite a safe established mapper/DTO contract | Existing architecture, risk and boundary evidence |

A potential issue is not a finding without an actual reachable path, supported access policy or demonstrable contract violation. **No Presenter class** is not, by itself, a defect. A safe internally used DTO is not automatically an information leak. Distinguish PII, contextual SPII, LGPD sensitive personal data and credentials; severity depends on harm, exposure and authorization, not solely terminology.

Verify the selected base/head, caller, affected properties and contrary evidence. Use synthetic fixtures and do not paste real identity or financial data into reports. Return only review evidence under `contracts/review-evidence.md`; never claim compliance certification from a code review.

Sources: [OWASP API3:2023](https://api-security.owasp.org/editions/2023/en/0xa3-broken-object-property-level-authorization/), [OWASP Logging](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html), [LGPD](https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709compilado.htm).
