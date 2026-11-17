# PR creation dispatch pilots

The `AGENTS.md` host-level route is a **dispatch instruction**, not an executable interceptor or a substitute for the Git PR policy. This directory contains seven provider-neutral agent-host scenarios: direct PT/EN publication requests, combined implementation and creation, provider API bypass, plan-only requests, stale review, explicit Draft, and ready-only with blocked Review.

Run catalog validation without claiming behavioral success:

```bash
python3 scripts/requirements_evals.py --catalog evals/git/pr-creation-routing.json
```

To assess behavior, use a disposable repository and an authorized host that loads `AGENTS.md` or equivalent always-on dispatch guidance. Retain the agent/tool transcript and a named evaluator's per-check observations; feed them to the existing `scripts/requirements_evals.py` evaluator using its `--observations` flag. Do not store credentials or private review material in this repository. Without actual runs, status is **INCOMPLETE**.

For enforcement, separately configure trusted runtime dispatch and provider-tool boundaries; this Markdown file alone cannot prevent another agent from invoking a remote create API.
