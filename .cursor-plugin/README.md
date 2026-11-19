# Cursor Plugin Integration

This optional Cursor Plugin consumes the **original canonical sources** under `contexts/` and `contracts/`. The repository root is the plugin root; `.cursor-plugin/plugin.json` declares paths only. No generated bundles, duplicated sources, symlinks, hooks, MCP servers, or additional runtimes are needed.

## Components and limitations

- **Skills, Commands, Agents:** all seven contexts are exposed through explicit manifest paths. Agents contain only portable `name` and `description` metadata. A host-discovered command is not proof of invocation, authorization or enforcement.
- **Rules:** `contexts/review/rules/code-review.md` is the **only pilot** Rule registered. Cursor documents `.md` Rule discovery in plugins but recommends `.mdc` in its Rules format section. The pilot uses `description` and `alwaysApply: false`. Do not enable the other canonical Rules as native plugin Rules before confirming actual discovery, activation and scoping; they remain authoritative dependencies of the relevant canonical Skills and Agents.
- **Contracts and references:** stay at their canonical paths. References to `contexts/...` and `contracts/...` must resolve against the **installed toolkit root**, not an unrelated consuming repository.
- **Runtime behavior:** the manifest does not enforce permission boundaries, provide independent subagent isolation or attest `gate` review. Missing evidence means no claim of independent `gate` or completed review.

## Verify locally with Cursor

1. Clone the **entire repository** as one checkout to `~/.cursor/plugins/local/agent-toolkit`, preserving `.cursor-plugin/`, `contexts/`, and `contracts/` together. This is the ordinary installed checkout, not copied/maintained canonical artifacts inside the source repository. Do not use an external symlink: local plugin symlinks are restricted to targets inside the local plugin folder.
2. Restart Cursor or choose **Developer: Reload Window**. In **Customize**, confirm the plugin and its Skills, Commands, Agents and single Review Rule are discovered. Enterprise administrators may need to allow local plugin imports.
3. In a **different consuming repository**, invoke `review-code` with an explicit diff and confirm that `code-reviewer`, `review-change`, `code-review.md` and `contracts/review-evidence.md` can be read from the plugin checkout. Verify that Review remains read-only and does not claim independent `gate` without actual attestation.
4. Verify that the pilot Rule is **actually loaded** for relevant Review work, and not applied to an unrelated Requirements-only task. Appearance in Customize alone is not sufficient.
5. Invoke a scoped Requirements Command and verify its Agent, Skill, Rules and Contract are resolved from the plugin checkout. Confirm actual permissions and observed effects; Markdown does not enforce them.

If Rule activation, path resolution, dispatch, or authorization fails, report that component as **unverified/incomplete**, not as working. This repository's structural lint cannot test Cursor model behavior, runtime activation or tool permissions.

## Validation

```sh
python3 scripts/toolkit_lint.py
python3 -m unittest discover -s tests -v
```

References: [Cursor Plugins](https://cursor.com/docs/plugins), [Cursor Plugin Reference](https://cursor.com/docs/reference/plugins), [Cursor Rules](https://cursor.com/docs/rules).
