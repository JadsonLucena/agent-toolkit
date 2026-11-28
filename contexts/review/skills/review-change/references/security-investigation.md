# Security Investigation — Conditional Review Reference

Use for a security-relevant changed behavior or reachable dependent surface. This is a **native, provider-neutral falsification aid**, not a mandatory checklist, new gate, or standalone audit. The Security Reviewer owns adversarial investigation; `contexts/review/rules/code-review.md` owns risk, findings, and verdict policy. Investigate only categories supported by the frozen change, its affected consumers, and plausible exposure.

## Investigation method

1. **Protected property and asset:** Name the confidentiality, integrity, availability, authentication, authorization, privacy, or business-security invariant at risk. Distinguish an approved requirement from a reviewer hypothesis.
2. **Adversary and capability:** Identify the principal, entry point, controllable inputs, available privileges, and necessary environment conditions; do not presume unrestricted access.
3. **Trust boundary and reachable path:** Follow relevant callers, guards, transformations, consumers and sinks beyond the diff where needed. For injection/data disclosure trace *source → transformation → boundary → sink*; for authorization examine *principal → action → resource → policy enforcement*; for temporal/state abuse examine *event order → guards → side effects → invariant*.
4. **Actual defenses and counterevidence:** Inspect middleware, policy checks, prepared statements, key scoping, transactions, idempotency, external enforcement, configuration and tests **at the reviewed revision**. Try to falsify the alleged exploit before reporting it.
5. **Exploitability and consequence:** Establish reachable preconditions and a realistic security consequence. A missing pattern or standard reference alone is not a vulnerability. Unobserved external enforcement is unknown, not automatically present or absent.
6. **Evidence and handoff:** Report exact source locations, triggering path, protection/violation, supporting and contradicting evidence, uncertainty and smallest effective remediation. For complex findings use optional `security_context` under `contracts/review-specialist-evidence.md`; leave inapplicable fields unset. The independent verifier and Lead classify findings via the shared contract.

Do not require executable exploits for unambiguous source-proven defects. Never execute untrusted repository code, target tests, fuzzers or probes outside authorized isolated checks. Do not probe live identities, infrastructure or external services.

## Conditional attack-surface probes

| Relevant change | Questions that can falsify an assumed security guarantee | Inspect |
| --- | --- | --- |
| Identity, sessions or tokens | Can an attacker assume another principal's identity, reuse a revoked credential, confuse audience/issuer or bypass sensitive reauthentication? | Authentication middleware, cryptographic verification, session lifecycle, expiry/revocation, recovery flows |
| Object, function, field or tenant authorization | Can a valid principal act on another resource/field/tenant, via a second entry point, job or indirect consumer? | Principal/action/resource relationship, policy enforcement, default deny, cache keys, authorized negative tests |
| Injection, files and untrusted content | Can attacker-controlled data reach an interpreter, query, path or rendered output as instructions rather than inert data? | Sources, parsers, normalization, parameterization, contextual encoding, sink and platform behavior |
| Cryptography and secret lifecycle | Are approved primitives used with correct key identity, confidentiality/integrity guarantees, nonces and rotation? Are secrets exposed by storage, logging or CI? | Usage context, library configuration, key/nonce lifecycle, authenticated encryption, logs and pipeline permissions |
| Sensitive-data lifecycle | Can protected data leak through response fields, errors, logs, traces, messages, caches, exports or retention? | Field-level policy, actual serializers/projections, cross-channel consumers, data classification |
| API, webhooks, RPC and messaging | Can a spoofed sender, replay, reordered message or confused deputy perform an unauthorized operation? | Signature/authenticity checks, replay protection, correlation IDs, retry/deduplication, service authority |
| Security-sensitive business state | Can concurrent, repeated or reordered legitimate-looking operations bypass quotas, approvals, balances, ownership or separation of duties? | State transitions, transactional guards, TOCTOU, uniqueness boundary, idempotency and authorization context |
| Errors and exceptional conditions | Does failure of an upstream dependency, timeout, parser, policy lookup or guard permit an operation that should be denied? | Fail-open paths, fallback defaults, partial effects, exception handling and recovery |
| Dependencies, delivery and cloud configuration | Can untrusted code gain secrets or privileges through package scripts, actions, workflows, images, workloads or IAM? | Pinned provenance, privileges, artifact integrity, public exposure, secrets and execution isolation |
| Browser, desktop, mobile and native memory | Is a hostile origin/IPC/file/binary input able to reach privileged browser APIs, command execution, unsafe parsing or memory-unsafe operations? | Applicable client/runtime boundaries, platform mitigations and realistic sink reachability |
| AI, model tools or agent systems | Can lower-trust prompts, retrieval, tool results or memory authorize actions or disclose another principal's data? | Model-to-tool permission boundary, tool arguments, resource scoping, confirmation and output channel |

Some categories overlap Correctness, Reliability, Architecture or Testing. Request only the missing evidence using `coordinate-review-team`; group duplicate candidates by demonstrable root cause under `verify-findings`.

## Reference selection and scope

- For applicable **web/API assurance**, consult [OWASP ASVS 5.0.0](https://github.com/OWASP/ASVS/tree/v5.0.0) by **version and specific requirement ID** where the requirement applies. ASVS is a verification reference, not an automatic universal merge gate or mandatory L3 assessment.
- Use [OWASP Secure Code Review](https://cheatsheetseries.owasp.org/cheatsheets/Secure_Code_Review_Cheat_Sheet.html) for investigation practice, [OWASP API Security Top 10:2023](https://owasp.org/API-Security/editions/2023/en/0x11-t10/) for relevant API abuse classes, and [MITRE CWE](https://cwe.mitre.org/) to classify a demonstrated weakness. The OWASP Top 10 is not a complete test checklist.
- [NIST SSDF SP 800-218](https://csrc.nist.gov/pubs/sp/800/218/final) informs lifecycle governance; it does not itself demonstrate that a code-level security property is satisfied.
- A project's accepted requirements, threat model, configuration, and deployed control evidence may be necessary. Preserve source authority; never invent a requirement, external mitigation, compliance certification, or threat model.
- Cloudflare `optional_helpers.security_audit` references are **additional advisory context only**. Absence or irrelevance cannot skip this native investigation. Never execute the external skill's full audit from Code Review.

## Decision and reporting

Use the shared severity, likelihood, confidence, `confirmed/supported/unverified/refuted`, blocker and source-falsification policy. When a material high-impact precondition remains inaccessible, document it for the Lead rather than asserting a confirmed vulnerability or a clean security assessment. No individual specialist issues PASS/FAIL.
