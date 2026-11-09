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

## Reviewer contract

The host reviewer receives a single `review-context` JSON object on stdin with `target`, `changed_files`, `review_required_files`, and `optional_helpers.ocr`. It writes an object conforming to `contracts/review-evidence.md` on stdout, including `review_status`, `target`, `changed_files`, `reviewed_files` and `unreviewed_files`.

The runner compares the returned target/inventory against the preparer's original values. It rejects an unjustified `PASS` with partial native coverage, overwrites any forged helper-execution metadata with bootstrap data, and returns `INCOMPLETE` when dispatch or validation fails. It **does not authenticate the identity or independence of the host reviewer**; the separate signed Git pre-PR gate is responsible for that check. Only run an explicitly authorized reviewer command with permissible source-code access. No shell expansion, software installation, code edits, Git commits or PR operations are performed by the runner.

Use `adapters/review/prepare_context.py` separately for debugging the preparation JSON (without dispatching a reviewer). `tests/test_review_dispatch.py` uses a fake OCR executable, Git fixture, and a fake reviewer to verify end-to-end ordering and all fallback paths. `tests/test_review_context.py` tests the bootstrap alone.
