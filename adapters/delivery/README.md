# Optional durable Delivery checkpoints

This optional SQLite adapter stores **bounded execution metadata**, not
repository policy, chat transcripts, approved Requirements, or source code.
The native context adapter is the dependency for verifying stored source
hashes on save and on resume. The database is **not** a memory database,
source of truth for authorization, or a substitute for real Git/external
state inspection.

Requirements: Python stdlib sqlite3 with SQLite available; a caller-created
private (0700) local directory; explicit absolute database path.
Do not put the DB in the source tree or on a shared network filesystem.
The adapter does not install SQLite or create the parent directory.

## API

- Construct a source-linked pack with
  adapters.context.native.prepare_context(repo, sources, critical).
- Build bounded checkpoint metadata using snapshot_from_pack(pack,
  execution_id, context_id, stage, target_stage, ...).
- Save with an expected generation (new execution uses zero). Generation
  mismatches fail rather than overwriting concurrent or newer state.
- Before attempting an external effect, record_effect(..., status="planned")
  with a stable execution-scoped effect ID. After observing the actual result,
  record "confirmed" with a checked evidence reference, or "unknown".
- Resume using resume(execution_id, repo). It verifies recorded file hashes
  and Git HEAD; critical source drift and outstanding external effects block.
  Even inspect-only is **not authorization to execute**.

No integration automatically calls external APIs, mutates the Git tree,
publishes branches/PRs or replays effects. This adapter is a reference
persistence component, not an executable Delivery Coordinator.

Example CLI (metadata file must come from approved host state):

```sh
python3 -m adapters.delivery.checkpoints --db "$HOME/.local/state/agent-toolkit/checkpoints.sqlite3" \
  save --snapshot /secure/path/checkpoint.json --expected-generation 0

python3 -m adapters.delivery.checkpoints --db "$HOME/.local/state/agent-toolkit/checkpoints.sqlite3" \
  effect --execution-id execution-1 --effect-id effect-1 \
  --operation create-payment-intent --status planned

python3 -m adapters.delivery.checkpoints --db "$HOME/.local/state/agent-toolkit/checkpoints.sqlite3" \
  resume --execution-id execution-1 --repo /path/to/git-worktree
```

The state directory must already exist, be private and be backed by a
local filesystem. Keep it outside tracked repositories. The DB is created
as owner-only (0600); SQLite WAL files follow the DB's local access rules.

## Failure and authority semantics

- Missing sqlite3: only checkpoint persistence is unavailable. Native
  context selection and all canonical Markdown procedures remain usable.
- Missing or stale source: never silently trust the saved stage.
- Changed HEAD with unchanged selected files: require source/dependency
  reconciliation rather than assuming unchanged behavior.
- Planned or unknown effect: block automatic replay. Journal status does
  not prove whether the external operation occurred; independently inspect
  the real provider and use its idempotency/reconciliation mechanisms.
- A confirmed journal entry stores an evidence *reference*, not external
  proof. A host must verify that evidence remains valid at resumption.
- Saved authorization_ref is historical context, never a new permission.
- Checkpoint writes are a local operational side effect and require the
  host/user's explicit persistence permission. No automatic capture.
- Store only references and hashes; do not copy secrets, raw prompts or
  production payloads into SQLite. Protect backups and retention.

This module intentionally does **not** create an FTS index, install
ai-memory, infer outcomes, or auto-run specialist stages.
