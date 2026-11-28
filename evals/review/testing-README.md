# Testing Review — adversarial evaluation fixtures

This catalog is a **benchmark specification**, not evidence that an LLM/agent passed. It tests whether the read-only `testing-reviewer` can identify weak or deceptive test evidence while avoiding unsupported defects, fake gates and compulsory new tests.

- [testing-cases.json](testing-cases.json): 13 source-backed cases (9 deficiencies, 3 adequate controls, 1 ambiguous source authority), each with an independent evaluation rubric.
- [build_testing_fixtures.py](build_testing_fixtures.py): creates a new, disposable two-commit Git repository for one case; refuses to overwrite an existing directory.
- `tests/test_review_testing_evals.py`: runs the sample green suites on both revisions and checks independent behavioral witnesses; also validates a skipped test, order-dependent test and stale CI artifact.

## Run the deterministic fixture checks

```sh
python3 scripts/requirements_evals.py --catalog evals/review/testing-cases.json
python3 -m unittest discover -s tests -p 'test_review_testing_evals.py' -v
python3 evals/review/build_testing_fixtures.py --case TR-02 --out /tmp/agent-toolkit-testing-evals
```

Each witness run uses Python's `-B` mode to avoid timestamp-based bytecode cache reuse when switching rapidly between similarly sized Git revisions. The builder returns the exact `base_sha`, `head_sha` and repository path. Run `/review/review-code` against that frozen diff in an authorized host. Assess the specialist's actual evidence and the Lead's output, not just the test name or terminal exit code.

## Evaluate observed model behavior

Capture complete, genuine agent output and tool actions for each fixed case. Have a separate evaluator review the transcript against each `presence`/`absence` rubric. Use the existing evaluator:

```sh
python3 scripts/requirements_evals.py --catalog evals/review/testing-cases.json \
  --observations /path/to/testing-observations.json
```

An empty observation set is **INCOMPLETE**, never a pass. The executable witnesses establish *fixture ground truth*, not the ability of an LLM to recognize it. Measure missed material weaknesses, false positives on the non-defect controls, evidence quality and repeatability across runs/hosts before claiming improved detection or any numeric performance score.

## Safety and scope

Fixtures contain only synthetic inputs, Python standard-library tests and local Git operations. They do not contact live services, run production payments, modify an existing case directory or invoke an AI provider. No new Review gate, mandatory Test Engineer workflow, universal coverage threshold or vendor-dependent adapter is introduced. Missing requirements and ambiguous sources are not fabricated into test oracles.
