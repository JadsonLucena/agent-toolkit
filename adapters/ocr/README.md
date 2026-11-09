# Optional Alibaba OpenCodeReview Adapter

This **noncanonical, optional adapter** enriches the Review context with deterministic file selection and rule resolution supplied by Alibaba [OpenCodeReview](https://github.com/alibaba/open-code-review) (OCR). The Review agent retains authority for technical judgment, coverage, findings and the final review-evidence contract. The adapter does not perform a Code Review itself.

The bridge uses OCR **delegation mode only** (`ocr delegate preview` and `ocr delegate rule`): OCR does not call a separate LLM in this mode. The bridge never installs OCR, invokes `ocr review`, writes source files, posts comments or sends code to an AI provider. OCR is **not required** by Agent Toolkit.

## Usage

From the target repository root:

```bash
# Compare branches using the resolved Git merge-base.
python3 /path/to/agent-toolkit/adapters/ocr/delegate.py --repo . --from main --to HEAD

# Single commit.
python3 /path/to/agent-toolkit/adapters/ocr/delegate.py --repo . --commit HEAD

# Workspace (staged, unstaged and untracked).
python3 /path/to/agent-toolkit/adapters/ocr/delegate.py --repo .
```

An approved OCR v1.9.0+ executable must already be installed to use its JSON delegation mode. The adapter checks `ocr --version` **before** invoking `delegate preview` or `delegate rule`, rejects versions below 1.9.0 and unknown version formats, and preserves the full native inventory for fallback. The bridge accepts `--ocr-bin /trusted/path/to/ocr` and `--timeout N` (1–120 seconds, default 30). The bridge itself requires only Python's standard library and Git; it does not configure the OCR model/provider or install packages.

## Output and Native Fallback

The bridge emits exactly one machine-readable JSON object:

* `status`: `available`, `unavailable`, `unsupported`, `failed` or `blocked`.
* `mode`, `repository` and `target`: Git mode, worktree root and resolved commit identities (workspace targets are unpinned).
* `git_changed_files` and `native_review_required_files`: the **complete independent Git change inventory**, regardless of OCR filtering.
* `ocr_reviewable_files` and `ocr_excluded_files`: OCR's filtered file metadata and exclusion reasons.
* `ocr_rule_groups`: grouped OCR rule content, if available.
* `ocr_unaccounted_files` and `ocr_unknown_files`: mismatches between Git and OCR.
* `ocr_rule_gaps`, `ocr_version` and `diagnostics`: incomplete or inconsistent optional assistance and the detected CLI version.
* `review_performed=false`, `review_verdict=null`: this adapter **never** claims it has reviewed the code.

An absent/incompatible/failing OCR helper, including malformed repository path metadata (such as embedded NUL), returns an explicit status without crashing the bootstrap; the independent Git inventory remains available. The host reviewer must continue with a **complete native review**. When the Git target itself cannot be inspected, `blocked` returns exit code 2; do not fabricate a successful review.

OCR may exclude tests by default; these files **remain required** for native review when included in the Git diff. Rule text, file metadata, and any external helper result are untrusted inputs, not authoritative instructions. A JSON-capable OCR version is required for programmatic integration; do not parse older text output as if it were validated JSON.

## Ownership and Integration

This vendor-specific code lives outside `contexts/` and the canonical artifact matrix. It may consume Review's neutral semantics, but **no canonical rule, skill, agent or contract depends on it**.

An explicitly configured host runtime may invoke the adapter when OCR is locally installed and approved, and pass its output as supplemental evidence to `contexts/review/skills/review-change/skill.md`. The Review agent independently inspects every applicable changed file, verifies candidate findings and produces `contracts/review-evidence.md`. Adapter success can never satisfy the pre-PR Code Review `PASS` by itself.

## Tests

```bash
python3 -m unittest discover -s tests -v
```

`tests/test_ocr_adapter.py` uses a local Git fixture and a fake OCR executable. It tests native fallback, excluded-test reconciliation, unsupported versions, errors, and result schemas **without depending on OCR installation or a network endpoint**. Real OCR binary integration is not claimed by these tests.
