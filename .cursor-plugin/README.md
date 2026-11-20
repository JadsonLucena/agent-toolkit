# Cursor Plugin Integration

This optional Cursor Plugin exposes Agent Toolkit's engineering guidance across requirements, design, implementation, testing, review, delivery, and Git. It helps AI coding agents work toward reviewable changes with explicit responsibilities and traceable evidence.

The plugin references the **original canonical sources** under `contexts/` and `contracts/`; the repository root is the plugin root. `.cursor-plugin/plugin.json` declares paths only. No generated bundles, duplicated sources, symlinks, hooks, MCP servers, or additional runtimes are needed.

## Metadata semantics

`name` on Skills and Agents is a **stable invocation identifier**; it is not a display-title rewrite. Changing a Skill directory or Agent filename requires a migration of canonical references, manifests, and callers. Generic Requirements Skill identifiers were clarified as `requirements-definition` and `requirements-validation`; all canonical references and tests were updated together. Other public identifiers remain unchanged.

`description` is a **discovery and routing hint**: identify the supported operation, when it applies, and important scope/authorization limits. It must not promise runtime enforcement, isolation, or completed verification. Rules use their canonical filename as identity, a contextual description, and `alwaysApply: false`; Commands now also expose portable `name` and `description` frontmatter for discovery, while their `## Intent`, `## Invocation`, and `## Boundary` sections remain the source of invocation semantics and authorization.

Structural checks guard names, description shape, and canonical coverage; they do not establish routing relevance, Rule activation, Command dispatch, or Agent isolation. The portable routing evaluation catalog and host-evidence protocol are documented in [`evals/routing/README.md`](../evals/routing/README.md).

## Components and limitations

- **Skills, Commands, Agents:** all seven contexts are covered without copying canonical files. Skills keep directory paths, which Cursor discovers as Skill directories. **Commands and Agents are declared as individual `.md` file paths** because Cursor 3.29.15 silently ignores directory entries inside manifest arrays for these two component types. Agents contain only portable `name` and `description` metadata. A host-discovered command is not proof of invocation, authorization or enforcement.
- **Rules:** all **14 canonical `.md` Rules** are declared individually, with a descriptive `description` and `alwaysApply: false` so they remain requestable rather than globally applied; automatic contextual activation is not assumed. `code-review.md` has already been observed in Cursor 3.29.15 as a requestable Rule; other Rule discovery and **actual automatic activation/non-activation remain to be tested in Cursor**. Cursor's plugin discovery accepts `.md`, while its separate Project Rules documentation recommends `.mdc`. Rules remain normative in their original context paths.
- **Contracts and references:** stay at their canonical paths. References to `contexts/...` and `contracts/...` must resolve against the **installed toolkit root**, not an unrelated consuming repository.
- **Runtime behavior:** the manifest does not enforce permission boundaries, provide independent subagent isolation or attest `gate` review. Missing evidence means no claim of independent `gate` or completed review.

## Importing through Cursor UI

**Import from Disk** or **Add Plugins from Folder** expects a *marketplace*
manifest (`.cursor-plugin/marketplace.json`), not only a single-plugin
`.cursor-plugin/plugin.json`. Select the **repository root** as the marketplace
folder (for example, `~/Documents/GitHub/agent-toolkit`). The marketplace
contains exactly one entry, `source: "."`, which points to the same repository
root and existing canonical plugin manifest. This adds **no copied artifacts**.

Make sure the checkout includes the branch carrying this change before importing.
Then install `agent-toolkit` from that local marketplace. If your Cursor build
does not support a root-source marketplace entry, use the documented direct
local plugin discovery below instead; the UI import remains unverified until
observed in Cursor.

## Verify locally with Cursor

1. Clone the **entire repository** as one checkout to `~/.cursor/plugins/local/agent-toolkit`, preserving `.cursor-plugin/`, `contexts/`, and `contracts/` together. This is the ordinary installed checkout, not copied/maintained canonical artifacts inside the source repository. Do not use an external symlink: local plugin symlinks are restricted to targets inside the local plugin folder.
2. Update/reimport the local marketplace plugin so the installed cache points to the **new Git revision**, then restart Cursor or choose **Developer: Reload Window**. In **Customize**, confirm the plugin and its Skills, Commands, Agents and all 14 Rules are discovered. Verify Commands in the `/` menu and Agents by direct delegation with observable subagent identity; a catalog listing alone does not prove invocation. Enterprise administrators may need to allow local plugin imports.
3. In a **different consuming repository**, invoke `review-code` with an explicit diff and confirm that `code-reviewer`, `review-change`, `code-review.md` and `contracts/review-evidence.md` can be read from the plugin checkout. Verify that Review remains read-only and does not claim independent `gate` without actual attestation.
4. Verify contextual activation with **separate fresh sessions**, for example `code-review.md` during a Review-only task versus a Requirements-only task, and `gitflow.md` only in a repository explicitly using Gitflow. Appearance in Customize alone is not sufficient; non-global `alwaysApply: false` does not itself prove correct selection.
5. Invoke a scoped Requirements Command and verify its Agent, Skill, Rules and Contract are resolved from the plugin checkout. Confirm actual permissions and observed effects; Markdown does not enforce them.

If Rule activation, path resolution, dispatch, or authorization fails, report that component as **unverified/incomplete**, not as working. This repository's structural lint cannot test Cursor model behavior, runtime activation or tool permissions.

## Validation

```sh
python3 scripts/toolkit_lint.py
python3 -m unittest discover -s tests -v
```

References: [Cursor Plugins](https://cursor.com/docs/plugins), [Cursor Plugin Reference](https://cursor.com/docs/reference/plugins), [Cursor Rules](https://cursor.com/docs/rules).
