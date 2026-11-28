# Fresh Plan Executor — optional runtime integration

This adapter runs a list of already authorized implementation plans **one at
a time**, using a **new non-resumed Codex CLI session for each plan**. It does
not create waves, parallel workers, another canonical agent, or a new source of
requirements. Each launch requires a `thread.started` event with a unique
thread ID; `turn.completed` and process exit are checked, but neither proves
tests passed or code is correct.

## What it requires

- Python 3.10+ and Git, plus an already installed and authenticated Codex CLI
  for the optional concrete backend. Nothing is installed automatically.
- A **clean Git worktree** rooted at the selected repository. In-progress
  changes are intentionally not overwritten or auto-stashed.
- The complete agent-toolkit installation containing the canonical
  Implementation and Git sources. A partial copied adapter is insufficient.
- A locally prepared, explicitly approved JSON plan list. `authorization_ref`
  is traceability, **not** independently verified permission; the human or host
  must enforce scoped permissions before invoking the adapter.
- Only use in an approved sandbox / disposable repository until host
  enforcement and real execution evidence have been established.

Example input (a template, not a claim that the example has been run):

```json
[
  {
    "plan_id": "plan-1",
    "objective": "Implement the approved bounded behavior",
    "authorization_ref": "approved-change-ref",
    "sources": ["docs/accepted-change.md"],
    "critical_sources": ["docs/accepted-change.md"],
    "allowed_paths": ["src/", "tests/"],
    "allow_local_commits": true
  }
]
```

Example invocation from the agent-toolkit installation with a consumer
repository checked out:

```sh
python3 -m adapters.implementation.fresh_plan \
  --repo /path/to/clean/consumer-repository \
  --plans /secure/path/approved-plans.json \
  --policy require --approve-execution
```

The user/host supplies and protects the plan list. Never pass credentials,
secrets, production data, or unapproved documents to the host. The adapter
uses the canonical sources installed beside it and retrieves only explicit
Git-tracked source references from the target repository with
`adapters/context/native.py`. Each subsequent plan reloads the references
from the current repository revision, rather than sharing the first agent's
conversation.

## Policies and statuses

- `prefer` (default): use fresh Codex sessions when installed, otherwise
  return `native-required` for the owning Implementation host to continue
  without falsely claiming context isolation.
- `require`: fail closed when Codex or session evidence is missing.
- `off`: return `native-required` without invoking an external host.
- `blocked`: stop on invalid/stale sources, unsafe workspace, missing
  events, duplicate session IDs, out-of-scope paths, uncommitted changes,
  failed process, or uncertain effects. Never auto-retry.
- `executed-unverified`: the CLI process was observed to finish and changes
  were committed within its declared path scope. **It is not Implementation
  acceptance, passing checks, independent Review, or a PR-ready verdict.**

Each plan executes in the **same sequential Git worktree**, with a new model
session. This does not create separate filesystem sandboxes for each plan.
The Codex CLI uses `--sandbox workspace-write`; it is the host's sandbox,
not per-path enforcement. `allowed_paths` is validated **after** execution
and cannot prevent an in-flight unauthorized write. The launcher also does
not authenticate authorization references, prevent all network/external effects,
or verify every model tool operation. For high-risk use, protect filesystem,
network, credentials and approval boundaries outside this adapter.

The adapter never runs Git commands that commit, push, create PRs or merge.
The fresh implementation session may create permitted atomic local commits
under the canonical Git rules. The launcher detects an uncommitted working
tree and stops rather than proceeding to the next plan. Fresh context does
not replace independent Code Review or Git pre-publication gates.

On timeout or unexpected exit, inspect the real Git/external state before
any retry. Optional `adapters/delivery/checkpoints.py` can persist metadata
only when separately approved; this adapter does not silently write to it
or pretend that a checkpoint reverses side effects.

## Verification

```sh
python3 -m unittest tests.test_fresh_plan_executor -v
python3 scripts/toolkit_lint.py
python3 -m unittest discover -s tests -v
```

Behavioral tests use a fake host and temporary Git workspaces. They validate
protocol, sequential ordering and failure handling, **not** genuine Codex
session creation or host sandbox enforcement. A real Codex installation,
approved disposable test repository, and observed host events are required
to make those claims. Never describe unit-test results as a completed
runtime pilot.
