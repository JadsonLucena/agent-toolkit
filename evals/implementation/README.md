# Fresh-session implementation host pilots

Structural and fake-host checks in
`tests/test_fresh_plan_executor.py` do **not** establish real agent session
isolation. For a native host pilot, reuse the protocol in
`adapters/implementation/README.md` with disposable repositories and no
production secrets, remote writes or external effects.

Record the host binary/version, installed toolkit SHA, source baseline,
authorized plan identities, exact prompt/source selection (securely stored
when permitted), `thread.started` session IDs and terminal events. Collect
the Git file inventory and successful execution of each required check after every plan, without
trusting a model's report.

Required scenarios: two plans produce distinct observed sessions; the second
receives updated verified source evidence without inheriting a transcript;
an unavailable host uses native fallback or blocks under `require`; a
missing critical source blocks before spawn; a repeated session ID, stale
source, out-of-scope write, uncommitted change or failed execution stops the
next plan. Include a negative test for instructions embedded in a source
excerpt, and observe the actual tool permissions rather than only final text.

Use `evals/context/` and `scripts/context_compare.py` for comparative
measurements (tokens, elapsed time, completion, intervention, source
freshness). Match model, harness, repository revision and authority before
comparing fresh-session and native-baseline runs. Never infer independent
Review, security enforcement or functional correctness from a finished
Codex process. Mark unavailable real-host observations **NOT_MEASURED**.
