# Guarded GitHub PR Creation

This optional GitHub runtime adapter applies the neutral Git rules and
\`contracts/review-evidence.md\` **before** invoking \`gh pr create\`.
The canonical rules do **not** import this adapter. Creation remains a
separate, explicitly authorized operation.

## Usage

The reviewed feature branch must be published and checked out locally, the
worktree must be clean, and evidence/configuration paths should be outside
the repository unless they are committed. An authenticated GitHub CLI is
needed **only** when using \`--create\`.

Create a JSON configuration of repository-established checks, for example:

\`\`\`json
{
  "checks": {
    "lint": ["python3", "scripts/toolkit_lint.py"],
    "tests": ["python3", "-m", "unittest", "discover", "-s", "tests", "-v"]
  }
}
\`\`\`

Add \`coverage\` or other required checks when the repository establishes them.
Pass the manifest through \`--checks-file\`. Commands use argument vectors
without a shell; never embed shell pipelines.

Supply independent Review evidence in a machine-readable representation
compatible with the neutral contract:

\`\`\`json
{
  "review_status": "PASS",
  "coverage_status": "complete",
  "reviewer": "independent-review-session-id",
  "reviewer_independent": true,
  "target": {
    "base_sha": "<full base SHA>",
    "head_sha": "<full feature-head SHA>"
  },
  "changed_files": [{"path": "example.py"}],
  "reviewed_files": [{"path": "example.py"}],
  "unreviewed_files": [],
  "blocking_findings": [],
  "unresolved_questions": []
}
\`\`\`

This is an **attestation**, not a cryptographically verified approval. Its
origin must be independently trusted and checked by the invoking runtime;
a fabricated JSON file cannot establish an independent review. The wrapper
requires an affirmative independence flag, PASS, complete coverage, exact
head/base and changed-file equality, and no unresolved blockers.

\`\`\`bash
# Validate without remote mutation:
python3 /path/to/agent-toolkit/adapters/github/guarded_pr.py \
  --repo . --base main --head feature/example \
  --evidence /tmp/review-evidence.json \
  --checks-file /tmp/project-checks.json

# Explicitly authorize creation after the same gate:
python3 /path/to/agent-toolkit/adapters/github/guarded_pr.py \
  --repo . --base main --head feature/example \
  --evidence /tmp/review-evidence.json \
  --checks-file /tmp/project-checks.json \
  --create --title "feat: example" --body-file /tmp/pr-description.md
\`\`\`

The wrapper checks a clean local worktree, the final local head and published
remote head, the exact PR diff against merge-base, complete review coverage,
and successful execution of every configured required check. It rechecks
head/base/freshness after checks, then and only then calls \`gh pr create\`.
\`--create\` is **not** implied by a dry-run success.

## Scope and Limits

* An empty/missing check manifest, missing review attestation, failed checks,
  changed branch, dirty worktree, unpublished head or incomplete review
  **blocks** remote creation through this adapter.
* This does **not** prevent another GitHub client or user from bypassing the
  wrapper. Organizations must enforce permissions/branch protections and
  integrate the wrapper as the only permitted creation path where needed.
* The manifest must reflect **all** repository-established checks. The
  wrapper cannot prove that an arbitrary supplied command has the right
  semantic coverage, or that the independent reviewer actually reviewed
  the files; the adapter/operator must trust provenance appropriately.
* The configuration and evidence are treated as inputs and must not be
  allowed to weaken a protected gate. Use a protected/trusted checks manifest
  in production.
* GitHub Actions \`pull_request\` runs are **post-creation** and cannot meet
  this pre-creation requirement. This adapter executes configured checks
  before creation; separate CI review is still useful afterward.
* This implementation is GitHub-specific by design; other hosts can
  implement the same canonical gate with their own API/CLI.

## Tests

\`tests/test_guarded_pr.py\` uses a real temporary Git repository and local
bare Git remote, with fake checks and intercepted \`gh\` invocation. It tests
PASS, failure, stale target, insufficient coverage, dirty/unpublished
branches and proof that \`gh\` is never called when preflight fails.
