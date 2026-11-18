# Context Engineering behavioral pilots

This catalog tests failures **not already covered** by the Delivery corpus:
compaction, cross-session continuity, project/slice isolation, incomplete retrieval,
optional-backend fallback, and prompt injection via remembered content.

Run existing Delivery cases DL-05, DL-08, DL-25, DL-26, and DL-27 **as part
of the same evaluation matrix**. Those cases own source supersession, side-effect
replay, bounded slice context, inaccessible sources, and selective invalidation.
Do not copy or rewrite their criteria here.

The catalog is **not evidence of agent behavior**. CI checks structure only.
A passed unittest or a catalog parse does not prove context retention, security,
or recovery in a real agent host.

## Evaluation protocol

1. Prepare disposable projects with versioned authoritative inputs, bounded
   permissions, and isolated sessions. Never use production credentials or
   private transcripts. Pin the model, harness version, base/head, and task.
2. Run the **native** Git/file-search baseline first, without SQLite, MCP
   memory, or optional rerankers. Run each test multiple times to expose variance.
3. Save the complete permitted tool trace and explicit source identity.
   A compaction test requires a real compaction event; otherwise mark it
   INCOMPLETE. A cross-session test requires two observed distinct sessions.
4. Repeat the same tasks with one optional retrieval capability at a time.
   Record indexing/build cost, tokens, runtime, failed lookups, relevant evidence,
   safety violations, and final task result. Do not compare an indexed warm
   cache against a cold native run without recording that difference.
5. Have a reviewer independently assess the trace, artifact revisions and
   actual side effects. Negative-path claims require full-trace inspection.

## Run

```sh
python3 scripts/requirements_evals.py --catalog evals/context/cases.json
python3 scripts/requirements_evals.py --catalog evals/context/cases.json --observations /path/to/context-observations.json
python3 scripts/requirements_evals.py --catalog evals/delivery/cases.json --observations /path/to/delivery-observations.json
```

The first command validates the catalog; **no behavior is evaluated**.
Missing, unavailable or unobserved host executions remain INCOMPLETE.

## Comparison record

For each task and host run, record the execution ID, task ID, model/harness,
repository revision, source baseline, authority, retrieval configuration,
optional backend availability, index build time, total elapsed time, tokens
when reported by the host, source refs inspected, verified obligations,
resulting code/test evidence, reviewer and result. Never invent unavailable
metrics. Compare task success and required-source coverage first, then
latency/cost. Do not treat hit@k as complete-evidence recall, or a cached
memory result as a new authoritative decision.

Do not introduce a vector database or any mandatory retrieval backend until
observed runs demonstrate benefit for a relevant class of tasks without
regressing authorization, source freshness, or critical-guarantee retention.
