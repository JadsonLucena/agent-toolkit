# Optional SQLite FTS5 index (CX04)

The **default remains native Git/file search** from `adapters/context/native.py`.
Importing this adapter does not load SQLite. A normal search does not inspect
the index, probe SQLite, create files, or index code.

## Activation policy

Three separate conditions must be satisfied:

1. SQLite's Python `sqlite3` module **and** FTS5 trigram tokenizer exist.
   Neither pip installation nor extension loading is attempted.
2. Indexed retrieval is **necessary**: an explicitly indexed request, or
   the bounded native scan returned `incomplete` and the host explicitly
   enabled optional fallback. A native `complete` or `truncated` result
   never activates the index in `auto` mode.
3. An **existing, explicitly approved** local index belongs to the exact
   repository/Git HEAD, includes all requested scopes, and the tracked
   working tree is clean. No implicit rebuild is permitted.

Search modes:

- `auto` (default): native only unless `--enable-optional` is set; even
  then use the existing index only after native reports `incomplete`.
- `native`: native only, regardless of flags or SQLite availability.
- `indexed`: explicit request to use an existing index; if unavailable,
  stale, out-of-scope, dirty or unsupported, fall back to native and
  report the actual backend and reason.

## Explicit index creation

Only use on a machine whose owner approved local persistence of the
**selected Git-tracked source text**. Select narrow, authorized scopes.
Do not run on private/secrets-bearing corpora without evaluating content
retention and local access controls. Automatic and background indexing are
not supported.

```sh
mkdir -p -m 700 "$HOME/.local/state/agent-toolkit"
python3 -m adapters.context.fts5 --repo . \
  --db "$HOME/.local/state/agent-toolkit/index.sqlite3" \
  --scope contexts --scope contracts --build --approve-cache
```

The existing private parent directory must be mode 0700, and the database
must remain outside the source repository. Stored index data are readable
code text, **not encrypted**. Source names resembling secret/credential
files are excluded, but that is not a reliable detector of sensitive
content. The index reports skipped files; partial indexing does not mean
complete coverage. Restrict scopes and manage retention/deletion externally.

## Search examples

Native first, with fallback to an already built index **only if needed**:

```sh
python3 -m adapters.context.fts5 --repo . \
  --search "Change Boundary" --scope contexts --scope contracts \
  --db "$HOME/.local/state/agent-toolkit/index.sqlite3" --enable-optional
```

Explicitly inspect an existing index without making it mandatory:

```sh
python3 -m adapters.context.fts5 --repo . \
  --search "Change Boundary" --scope contexts \
  --db "$HOME/.local/state/agent-toolkit/index.sqlite3" --mode indexed
```

When available, SQLite FTS5 uses a trigram index to find candidate text
files; Python verifies literal case-insensitive matching line by line.
It does not perform semantic similarity, infer requirements, or evaluate
evidence completeness. No source-content result may override current
instructions or grant access to missing sources.

## Freshness and fallback

Indexes are bound to one absolute Git root, exact HEAD and explicitly
approved directory scopes. Dirty tracked sources, moved HEAD, mismatched
scope, insufficient SQLite capability, incompatible schema or missing
index all trigger native fallback with a diagnostic. A query never
creates or modifies an index. The builder refuses dirty source state,
writes into a temporary private file, and atomically replaces the index
only after successful completion and source revalidation.

FTS5 is an **optional speed/coverage experiment**, not a new authority,
a complete source inventory, or a requirement to run any canonical
context. Compare actual tasks via the existing
`evals/context/` behavioral corpus and
`scripts/context_compare.py` (PR #43).
Benchmark index creation separately from repeated warm searches.
