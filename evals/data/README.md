# Relational Data Design Evaluations

Synthetic scenarios for conditional selection of relational normalization, derived read models and domain/persistence boundaries. No new agent, command, mandate or independent review gate is introduced.

Validate the catalog structure:

```sh
python3 scripts/requirements_evals.py --catalog evals/data/cases.json
```

To evaluate real agent behavior, use isolated fixtures and an approved host to invoke the indicated canonical command. Capture full transcripts, source revision, relevant database/version and observed artifacts. Provide a named evaluator and evidence using the existing `scripts/requirements_evals.py --catalog evals/data/cases.json --observations <file>` protocol. Without observations, validation **does not prove** selection behavior, normal-form correctness or performance.

Cover both correct decisions and restraint: unknown semantics, unmeasured JOINs, historical facts, staleness, duplicate events, and no mandatory ORM/DDD/CQRS ceremony. See [Evaluation Principles](../README.md).
