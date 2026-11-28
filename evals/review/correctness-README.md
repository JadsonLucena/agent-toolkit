# Behavioral Correctness Review — Reproducible Evaluation Corpus

This separate catalog avoids coupling correctness evaluation to the existing
specification conformance rubric or concurrent review-specialist PRs.
It evaluates **both** discovery of source-backed functional defects and
rejection of unsupported bug allegations. Its fixtures are small Python
programs with an accepted-behavior document and a frozen two-commit diff.

## Materialize and evaluate

```sh
python3 scripts/requirements_evals.py --catalog evals/review/correctness-cases.json
python3 evals/review/build_correctness_fixtures.py --case CR-01 --out /tmp/correctness-evals
cd /tmp/correctness-evals/CR-01
git log -2 --oneline
git diff HEAD~1 HEAD
```

The generator prints `repository`, `base_sha` and `head_sha` for a host to
pass to `/review/review-code`. The output directory for each case must not
exist. Run each fixture in a disposable environment; never use real credentials,
production integrations or another project's working tree.

Run the actual reviewer against the fixed base/head, capture its transcript
and observed tool actions, and have a separate evaluator assess the checks,
as specified in [Review evaluation instructions](README.md). For example:

```sh
python3 scripts/requirements_evals.py \
  --catalog evals/review/correctness-cases.json \
  --observations /path/to/correctness-observations.json
```

Each case declares a `polarity`: `defect`, `non-defect`, or `uncertain`.
Report these groups separately, especially false-positive controls. Distinguish
demonstrated results from unexecuted cases; an empty observation set is
`INCOMPLETE`. No catalog validation, fixture creation or green unit test
establishes LLM accuracy, precision or recall.

`CR-10` deliberately includes a misleading head test that passes for the
wrong discount. The accepted contract, not test expectations or PR prose,
is the behavioral oracle. No branch is deployed or PR published by this tool.
