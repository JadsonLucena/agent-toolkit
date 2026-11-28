# Cloudflare Security Audit — approved local guidance

The upstream MIT-licensed [Cloudflare security-audit-skill](https://github.com/cloudflare/security-audit-skill) is bundled by default in `.agents/skills/security-audit/` (a single canonical copy). `skills-lock.json` pins the reviewed upstream commit and the Skills CLI v2 content hash. The upstream license is preserved at `third_party/licenses/cloudflare-security-audit.LICENSE`.

## Distribution and maintenance

- Cursor and Claude plugin manifests both expose `./.agents/skills`. Do not copy another `SKILL.md` into their own skill directories.
- The files are committed: a clone or plugin installation includes the skill without network requests, Node, Skills CLI, or Git submodules at review time.
- To update, review the upstream diff, use `npx skills add cloudflare/security-audit-skill@<approved-commit> --skill security-audit -a cursor -a claude-code -y` in a disposable workspace, then copy the approved canonical files and generated lock, preserving the license. Do not commit generated host links.
- A separate installation may be specified using `--security-audit-root` only when its full contents match the pinned approved hash.

## Read-only integration

`python3 adapters/security-audit/resolve.py --changed-file src/auth/session.py` verifies the local skill and returns applicability hints with status available, unavailable, rejected, or disabled. It does not execute validators, scripts, subagents, installations, network requests, or reviews.

`adapters/review/prepare_context.py` embeds this result in `optional_helpers.security_audit` after Git inventory preparation. The Security Reviewer reads selected references as **guidance only**; native findings must be independently source-verified. The Code Review Lead retains the single verdict. Failure or irrelevance of this helper does not reduce native coverage.

The upstream full audit workflow requires separate explicit authorization and is not automatically invoked by ordinary review.

## Validation

Run `python3 -m unittest discover -s tests -v`, `python3 scripts/toolkit_lint.py`, and `python3 scripts/claude_plugin_lint.py`. These checks verify static packaging and local integrity; they do not establish actual host activation or the security value of model-generated investigations. Real Cursor and Claude plugin pilots remain necessary.
