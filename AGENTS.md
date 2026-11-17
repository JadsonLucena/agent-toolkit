# Agent Toolkit — Host-Level Command Routing

These are **host-facing routing instructions** for an agent whose runtime loads this repository's root `AGENTS.md`. They do not replace the canonical Commands or enforce tool permissions. When the toolkit is used from another repository, that host must load equivalent routing guidance **before skill selection**.

## Remote Pull-Request Creation

- If the user's intent is to **create, open, or publish a remote pull request** (for example, "Crie o PR", "Abra um pull request", "Publish this PR", or "Implement and create a PR"), route the publication request through **`contexts/git/commands/create-pull-request.md` as the sole publication entry point**.
- **Before** calling `gh pr create`, a hosting-provider API, an MCP connector, or any other remote PR-creation tool, read and follow that Command. This routing takes precedence over the Skill or Agent initially matched to the user's request. A non-Git workflow may implement or prepare the change, but must hand off publication to the Git Command; it must not publish directly.
- The Command owns invocation and authorization, and selects its existing Git workflow. **`contexts/git/rules/pull-request.md` alone owns ready/Draft/blocked eligibility**, including acquisition and freshness of independent Review evidence. Do not duplicate or relax that decision here, or treat a test result, diff inspection, or another PR Skill as a substitute for the Command.
- If the Command, its required checks, or its authority cannot be established, **stop publication and report the limitation**. Do not fall back to direct PR creation. This route does not grant push, merge, release, or deployment.
- Requests **only** to plan PR boundaries, prepare descriptions, inspect existing PRs, or review code are not publication requests. Use their existing read-only entry points; never infer remote creation authorization from them.

## Host Integration Boundary

For a GitHub host that requires technical publication control, expose the
approved `adapters/github/guarded_pr.py` entry point with a protected reviewer
command and check policy. Give the coding agent **no direct remote PR-creation
capability or credentials**. In advisory-ready mode the adapter invokes the
approved read-only reviewer and validates its actual result before creating
the PR. The signed `gate` path stays independent and stricter; a Draft still
requires explicit authorization. See `adapters/github/README.md`.


This file is effective only in hosts that actually ingest it. A consuming project or agent platform must expose this route at its always-loaded instruction/dispatch layer; installing only an optional Skill is insufficient. For a technical guarantee, configure the host/tool boundary to disallow direct PR-creation calls outside the Command's authorized preflight. Repository Markdown alone cannot intercept unrestricted `gh` or API calls.
