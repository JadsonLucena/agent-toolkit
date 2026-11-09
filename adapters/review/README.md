# Review Command Runtime Integration

The canonical `/review/review-code` Command MUST prepare the review context **before inspecting or reviewing changes**. The executable reference integration is `adapters/review/run_review.py`, which invokes `adapters/review/prepare_context.py` and dispatches the resulting JSON context to the approved host reviewer through **stdin**. It never runs a model on its own or grants remote PR approval.

## Configure the host runtime

Map the host's `/review/review-code` entrypoint to the following (the command after `--` must be an authorized, independent host reviewer that reads the JSON context from stdin and writes review-evidence JSON to stdout):

```bash
python3 /path/to/agent-toolkit/adapters/review/run_review.py \
  --repo . --from main --to HEAD \
  -- /path/to/approved-reviewer [reviewer-args]
```

For single-commit review use `--commit HEAD`; for workspace changes omit `--from`, `--to`, and `--commit`. Both `run_review.py` and `prepare_context.py` also accept `--no-ocr`. An optional native-only review:

```bash
python3 /path/to/agent-toolkit/adapters/review/run_review.py \
  --repo . --from main --to HEAD --no-ocr \
  -- /path/to/approved-reviewer [reviewer-args]
```

`/review/review-code` is **canonical Markdown**, not an executable slash-command binding by itself. A Cursor/Claude/other host must map the command to this runner or implement the same required preflight in its own adapter. A host that does not invoke the runner cannot claim it enforced OCR-first ordering.

## Deterministic execution matrix

| Input | Preparation before review | Native reviewer |
| --- | --- | --- |
| Default, OCR >= 1.9.0 | `ocr --version`, `ocr delegate preview`, `ocr delegate rule` | Full review of all Git changed files, with OCR hints |
| Default, OCR missing/old/failing | Git inventory, OCR diagnostic | Full native-only review |
| `--no-ocr`, regardless of installation | **Neutral Git scope only; no OCR import or process** | Full native-only review |

The bridge uses OCR's **delegation** capabilities (file selection and rule resolution), **not a separate OCR LLM Code Review**. A host reviewer remains responsible for the entire native analysis, even of OCR-excluded test files, and supplies the final `PASS`, `FAIL`, or `INCOMPLETE`. An executable returning OCR hints cannot count as reviewed evidence.

## Team planning and isolated Task adapter

Before **any** Task spawn, the Code Review Lead classifies risk and supplies
separable concerns. The runner freezes the Git target including a SHA-256
workspace fingerprint when reviewing uncommitted changes.

Example for an R3 payment/authorization change with Cursor-like isolated Tasks:

```bash
python3 /path/to/agent-toolkit/adapters/review/run_review.py \
  --repo . --from main --to HEAD \
  --risk-profile R3 \
  --concern correctness --concern reliability --concern security \
  --task-capable \
  -- /path/to/host-reviewer-with-task-api
```

`--task-capable` asserts that the runtime supplies *isolated* subagents. Do
not set it for in-process function calls or ordinary subprocesses; doing so
does not create real subagents. In Cursor, each selected specialist is a
separate `Task` within one first-pass turn; the Code Review Lead relays
question/challenge to the same subagent via `resume`, or creates a new
narrow Task if resume is not supported. No direct sibling messaging is
implied. With isolated Tasks but no host-observed direct exchange, the
execution mode is `team-relayed`. `team-live` is permitted only when an
approved runtime audit proves direct peer request AND response delivery.

The host's authorized reviewer process imports
`adapters/review/team_orchestration.py` and implements the `TaskRuntime`
protocol: `task_batch(requests)`, `resume(task_id, message)`, and optional
`direct_message_audit(review_id)`. The module freezes the plan **before**
the first batch, validates common target and distinct task IDs, enforces
R0=0, R1=0–1, R2=2–4, R3=3–5 specialists plus conditional/mandatory
isolated verifier, relays bounded evidence threads, and returns only
candidate evidence until the lead reconciles every file.

`run_review.py` forwards the frozen `team_plan` to the reviewer and
checks team/risk identity and the minimum evidence for a claimed `PASS`.
The runner **cannot itself invoke Cursor's internal Task API**: the approved
host must supply this protocol. Without that binding, a `--task-capable`
claim is invalid and must not be used. Implementation authors must use a
separately independent review lead/session; isolated lenses do not erase
the lead's authorship.

## Reviewer contract

The host reviewer receives a single `review-context` JSON object on stdin with `target`, `changed_files`, `review_required_files`, and `optional_helpers.ocr`. It writes an object conforming to `contracts/review-evidence.md` on stdout, including `review_status`, `target`, `changed_files`, `reviewed_files` and `unreviewed_files`.

The runner compares the returned target/inventory against the preparer's original values. It rejects an unjustified `PASS` with partial native coverage, overwrites any forged helper-execution metadata with bootstrap data, and returns `INCOMPLETE` when dispatch or validation fails. It **does not authenticate the identity or independence of the host reviewer**; the separate signed Git pre-PR gate is responsible for that check. Only run an explicitly authorized reviewer command with permissible source-code access. No shell expansion, software installation, code edits, Git commits or PR operations are performed by the runner.

Use `adapters/review/prepare_context.py` separately for debugging the preparation JSON (without dispatching a reviewer). `tests/test_review_dispatch.py` uses a fake OCR executable, Git fixture, and a fake reviewer to verify end-to-end ordering and all fallback paths. `tests/test_review_context.py` tests the bootstrap alone.
