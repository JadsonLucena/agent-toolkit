# Guarded GitHub PR Creation

\`adapters/github/guarded_pr.py\` is an optional **GitHub-specific, executable
pre-creation gate** for the portable Review → Git evidence contract.

The adapter verifies an **SSH-signed review attestation** from an authorized
reviewer and executes all checks specified in a **deployment-protected policy**.
Only after success, and only with explicit \`--create\`, does it invoke
\`gh pr create\`. It then queries the created PR through \`gh api\` and checks
the returned repository, base/head refs **and SHAs**, title, and Draft state.
A mismatch returns \`created_unverified\` with the remote URL and a nonzero exit
code; it never claims success based only on the creation command's stdout.

## Trust model and setup

An invoking **trusted runtime/operator** must own the following, outside the
target repository and outside the implementation author's control:

1. An SSH private signing key **held only by an authorized independent reviewer
   or independent review service**, not the developer who authored the change.
2. A protected OpenSSH allowed-signers file with that reviewer's public key.
3. A protected trust policy listing the authorized review identities, exact
   remote URL, GitHub repository identity and **complete required check argv**.
4. A fixed, protected invocation of this gate. Do not allow untrusted authors
   to supply substitute \`--trust-policy\` paths or override required check
   configuration.

Example protected trust policy (outside the checked-out repository):

\`\`\`json
{
  "schema_version": 1,
  "github_repository": "org/repo",
  "remote_url": "git@github.com:org/repo.git",
  "allowed_signers_file": "/protected/review-allowed-signers",
  "reviewers": ["reviewer@example.com"],
  "checks": {
    "lint": ["python3", "scripts/toolkit_lint.py"],
    "tests": ["python3", "-m", "unittest", "discover", "-s", "tests", "-v"]
  }
}
\`\`\`

Add established coverage and other mandated checks to \`checks\`. The optional
committed \`.github/toolkit-pr-checks.json\` is **not an authority**: when it
exists, this wrapper additionally rejects differences from the protected
check list. The protected policy, not a user-supplied manifest, selects the
actual commands run.

An SSH allowed-signers file contains a principal and a public key per line:

\`\`\`text
reviewer@example.com ssh-ed25519 <PUBLIC_KEY> comment
\`\`\`

The authorized independent reviewer produces a portable JSON file with the
semantics of \`contracts/review-evidence.md\`. The signed profile includes:

\`\`\`json
{
  "repository": "org/repo",
  "review_profile": "gate",
  "review_status": "PASS",
  "coverage_status": "complete",
  "reviewer": "reviewer@example.com",
  "reviewer_independent": true,
  "target": {
    "base_sha": "<full-base-SHA>",
    "head_sha": "<full-head-SHA>"
  },
  "changed_files": [{"path": "src/app.py"}],
  "reviewed_files": [{"path": "src/app.py"}],
  "unreviewed_files": [],
  "blocking_findings": [],
  "unresolved_questions": []
}
\`\`\`

After completing the **actual independent review**, the authorized signer
signs the **exact JSON bytes** (the private key must not be committed, copied
to the implementation workspace, or handed to the code author):

\`\`\`bash
ssh-keygen -Y sign -f /protected/reviewer_key \
  -n agent-toolkit-code-review /protected/review-evidence.json
# produces /protected/review-evidence.json.sig
\`\`\`

The wrapper uses \`ssh-keygen -Y verify\` with a dedicated signature namespace.
It refuses unsigned/tampered evidence, unknown signers, missing complete file
coverage, unresolved review blockers, self-review by matching Git author
email, stale base/head, dirty worktrees, unpublished branches, mismatched
check commands and any failed mandatory check.

**The SSH signature authenticates the signing key, not human independence by
itself.** Trusted reviewer provisioning, private-key custody, author-to-signer
identity mapping and the protected launch path are deployment obligations.
The wrapper's author-email comparison is an additional defense, not sufficient
proof of separation. An attacker allowed to alter the trust policy, review
signing keys or invocation can defeat the gate.

## Usage

\`\`\`bash
# Non-mutating preflight:
python3 /path/to/agent-toolkit/adapters/github/guarded_pr.py \
  --repo . --base main --head feature/example \
  --evidence /protected/review-evidence.json \
  --signature /protected/review-evidence.json.sig \
  --trust-policy /protected/review-policy.json

# Only the explicit --create authorizes remote PR creation:
python3 /path/to/agent-toolkit/adapters/github/guarded_pr.py \
  --repo . --base main --head feature/example \
  --evidence /protected/review-evidence.json \
  --signature /protected/review-evidence.json.sig \
  --trust-policy /protected/review-policy.json \
  --create --title "feat: example" --body-file /tmp/pr-description.md
\`\`\`

Requires Python 3.10+, Git, OpenSSH \`ssh-keygen\`, and authenticated GitHub CLI
only for \`--create\`. The wrapper does not install or configure these tools.
It will fail closed if any required trust anchor or verification is unavailable.

## Boundaries

* \`gh pr create\` is not invoked when preflight fails. A PR may have been
  created **before** post-creation verification fails: the wrapper reports
  \`created_unverified\` and the URL rather than claiming success, closing
  the PR or creating a duplicate automatically.
* This is **not a global GitHub authorization boundary**. Other clients
  can still bypass it unless enforced through an approved runtime,
  permission model and repository/organization policy.
* The wrapper cannot prove that repository tests truly cover every relevant
  behavior; the protected policy must represent effective project checks.
  CI triggered only by PR creation is not a substitute for preflight checks.
* The actual code review belongs to the separate Review context. Neither
  the SSH signature nor the output of the adapter performs a review.

## Tests

\`tests/test_guarded_pr.py\` uses real local Git and bare remote fixtures,
generates temporary SSH signing keys, tests signed/forged/stale evidence and
protected check-policy failures, and simulates \`gh pr create\` plus subsequent
\`gh api\` verification. No real PR is created by the tests.

## Gate Profile Integrity

The protected pre-PR validator accepts only SSHSIG-signed evidence explicitly
declaring `review_profile: gate`. Signed `advisory` results, missing legacy
profiles and independent-looking flags cannot bypass the gate. The profile
is part of the **exact signed JSON bytes**; no adapter may retroactively
promote an advisory finding. An advisory PASS may be useful in an IDE,
but has no PR-creation authority. Explicitly nonmaterial questions with
`material:false` may remain without granting false certainty about
material unresolved issues. The signer and protected runtime remain
responsible for actual reviewer independence.
