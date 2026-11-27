# Claude-format plugin integration

Agent Toolkit is a portable engineering guidance repository. This **optional** Claude-format package registers the **existing canonical** Skills, Commands, and Agents in the root checkout, without copying or rewriting their source content. Claude Code supports custom component paths in `.claude-plugin/plugin.json`; VS Code's Copilot harness recognizes that manifest format, but **format recognition alone does not prove all three component types work**.

## Package contents and limits

| Capability | Registration | What is not guaranteed |
| --- | --- | --- |
| Skills | All 20 canonical `SKILL.md` files under eight `contexts/*/skills/` scan roots | Selection, activation, and cross-repository references |
| Commands | All 18 canonical `contexts/*/commands/*.md` files by explicit path | Slash-command mapping or execution in every Copilot client |
| Agents | All 17 canonical `contexts/*/agents/*.md` files by explicit path | Delegation support, identity isolation, allowed tools, or review-gate attestation |
| Rules | **Not registered by this manifest** | Claude format has no equivalent top-level Rule paths field; Cursor Rule metadata does not make Claude or Copilot inject them |
| Contracts | Remain in `contracts/` inside the same checkout | Loading just because a canonical Markdown document mentions a contract |

Rules remain the **normative sources** for toolkit procedures, but this first integration does not claim implicit injection or route them automatically. Skills, Commands and Agents reference those files using repository-relative canonical paths. Whether the host can resolve those references from an **unrelated consumer workspace** must be tested. When it cannot, report the unresolved dependency rather than claiming the Rule or Contract was applied.

This plugin adds **no** hooks, MCP servers, binaries, installation scripts, file copies, symlinks or provider-specific mutations to the canonical `contexts/` and `contracts/` trees. Names and permission boundaries in canonical Commands remain unchanged; the manifest is discoverability metadata, **not authorization**.

## Claude Code: verify locally

Run the following from a full checkout of the proposed branch:

```sh
python3 scripts/claude_plugin_lint.py
claude plugin validate . --strict
claude --plugin-dir .
```

The Python check validates manifest structure and exact canonical coverage; it cannot emulate Claude Code's parser or runtime. The Claude CLI validation is the **host's** manifest check. In a fresh Claude session, inspect the installed plugin name, the Skills/Commands/Agents list, and use a **disposable** task to verify invocation. For Claude Code, commands are namespaced under the plugin, for example `/agent-toolkit:review-code`; discovery is not proof that review-read-only or `gate` semantics are enforced.

## VS Code with GitHub Copilot: verify locally

1. Use a VS Code release that supports Agent Plugins and select the **Copilot** harness in the Agent Customizations editor. Enable `chat.plugins.enabled` if needed.
2. Use **Install a plugin from source** to point at this full checkout, or register it for development using experimental `chat.pluginLocations`. Do not point to `.claude-plugin/` by itself; the plugin root contains the canonical sources.
3. In the plugin details, inspect the available Skills, Agents and Commands **individually**. Do not infer component parity from the recognized manifest.
4. In a **different disposable repository**, run a safe scenario such as reviewing a specified diff read-only. Capture host events for Skill loading, slash-command resolution, delegated Agent identity, Rule/Contract path resolution, and any missing capability.
5. Record the exact host version, harness, plugin revision and observed events in `evals/routing/`, marking capabilities `unsupported` or `not-run` when evidence is unavailable.

Do not configure VS Code as a duplicate Claude agent runtime or assert that `AGENTS.md` from the plugin root is automatically added to the consumer workspace. Add host-specific adapters **only after** a demonstrated incompatibility.

## Regression and release conditions

```sh
python3 scripts/claude_plugin_lint.py
python3 -m unittest tests.test_claude_plugin -v
python3 scripts/toolkit_lint.py
```

CI can attest manifest paths, identity, and coverage. It **cannot** attest native installation, actual selection, delegated isolation, tool permissions, canonical path resolution, or Review gate independence. Until those are observed in both hosts, describe this as a **statically validated, runtime-unverified** integration.

Primary specifications:
- https://code.claude.com/docs/en/plugins/manifest-reference
- https://code.visualstudio.com/docs/agents/reference/agent-plugin-reference
- https://code.visualstudio.com/docs/agent-customization/agent-plugins
