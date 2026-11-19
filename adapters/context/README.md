# Native context preparation (optional runtime integration)

This adapter produces bounded, read-only **context packs** from explicitly
selected, Git-tracked files. It may be called by an authorized host before
routing a slice to a specialist. It does not authorize source access,
mutations, a review PASS, stage completion, or complete-repository coverage.

There is no SQLite, embedding, model, or network dependency. This is an
implementation of native source resolution, not a new canonical contract.
The governing source remains the repository and the existing contracts.

Example from a Git worktree root:

```sh
python3 -m adapters.context.native --repo . \
  --critical contexts/delivery/rules/delivery.md#L1-L10 \
  --source contexts/delivery/skills/coordinate-delivery/SKILL.md#L1-L14
python3 -m adapters.context.native --repo . \
  --search "Change Boundary" --scope contracts --scope contexts
```

Source selectors use repository-relative tracked paths, optionally
path#LSTART-LEND. Critical source text is loaded first and never truncated.
Missing/inaccessible/over-budget critical text yields blocked status.
Other inaccessible sources yield partial status and explicit diagnostics.
Untracked, symlinked, binary, oversized, or out-of-repository files are not read.
Content hashes cover the full file even for line-range excerpts.

The status is **ready for context inspection**, not task readiness. Source
content is untrusted input; an agent must still verify the meaning of
authority, stage, permission, dependencies and complete affected scope.
The HEAD SHA is not a working-tree fingerprint, and source hashes do not
cover other transitive dependencies. Revalidate on every material handoff.

To verify a pack saved externally after an interruption:

```sh
python3 -m adapters.context.native --repo . --verify /path/to/pack.json
```

A moved Git HEAD returns revalidate even if the selected file bytes match.
A changed critical or requested file returns blocked. Full Context Pack
verification also compares saved excerpts and line provenance against the
reread source; a matching file hash alone cannot validate altered pack text.
Metadata-only checkpoint verification explicitly uses
`verify_context(..., require_content=False)` for hashes, never an excerpt
authentication claim. No external mutation
is performed. The adapter is not a persistent execution checkpoint.

Native search is a bounded literal scan of Git-tracked UTF-8 files under
explicit scopes. Search hits only suggest candidate sources; they are not
complete evidence. The scan has fixed file and result ceilings, and reports
incomplete/truncated results rather than asserting exhaustive coverage.

The separate optional [SQLite FTS5 adapter](FTS5.md) is **not called by this
native entrypoint**. Its default auto mode also stays native-only; it can use
an explicitly approved, already-built local index only when the native scan
reports `incomplete` and the host enables optional lookup, or under an
explicit indexed request. SQLite presence by itself is never activation.

No automatic installation or provider configuration takes place.
