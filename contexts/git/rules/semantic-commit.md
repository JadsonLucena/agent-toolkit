# Semantic Commit Rules

## Core Principles

* Follow the repository's established commit convention; it takes precedence over every default defined in this document. If none exists, use Conventional Commits.
* Use the structure `<type>[optional scope][!]: <summary>`, with an optional body and footer section.
* Derive commit semantics from the intent of the change, not merely from the files modified.
* Derive commit semantics only from supported evidence such as the staged diff, surrounding code, tests, issue context, repository conventions, and explicit developer intent.
* If the primary intention, semantic type, scope, breaking-change status, or relationship between changes cannot be determined with sufficient confidence, ask the developer rather than guessing or inventing semantics.
* The commit message must describe all and only the changes included in the commit.
* Commits must be atomic: each commit must represent one logical intent that is coherent, independently reviewable, and reversible without unrelated collateral changes.

## Specification and Style

* When Conventional Commits applies, it defines the semantic structure of the commit message.
* Follow the Angular Commit Message Guidelines for summary and body style, with the refinements and limits defined below taking precedence.

## Type

* The type must communicate the primary intention of the change.
* Use `feat` when introducing a new capability or feature.
* Use `fix` when correcting incorrect behavior.
* Other types such as `build`, `chore`, `ci`, `docs`, `perf`, `refactor`, `style`, and `test` may be used when they match repository conventions and the actual intent.
* Prefer the most specific applicable type; avoid generic types such as `chore` when another established type communicates the intent more precisely.

## Scope

* A scope is optional and must be used only when it adds meaningful context.
* When used, write the scope in parentheses immediately after the type: `<type>(<scope>): <summary>`.
* Use a noun that intuitively identifies a stable section of the codebase, such as a domain, component, package, subsystem, or other established project area.
* Prefer stable semantic scopes over incidental file paths unless the repository explicitly defines file- or directory-based scopes.
* Keep scope naming consistent with established repository conventions.

## Summary

* Use the imperative, present tense.
* Start with a lowercase letter.
* Do not end with a period.
* Keep the summary concise, specific, and faithful to the committed change.
* Apply the length limit to the entire header line, including type, scope, and `!`, because they share the same budget as the summary.
* Follow the repository's configured header length limit when one exists, such as a commit-message linter rule; otherwise keep the header at or below 72 characters and aim for about 50, treating the Angular limit of 100 characters as the outer bound rather than a target.
* When the summary does not fit, move the detail to the body instead of truncating the intent, abbreviating cryptically, or dropping the type or scope.
* Treat a summary that cannot express the change within the limit as a possible sign of a non-atomic commit, and reconsider splitting before shortening.

## Body

* Separate the body from the header with a blank line.
* Use the imperative, present tense.
* Describe and justify the change when the summary alone is insufficient.
* Explain the motivation, relevant context, tradeoffs, or consequences.
* When useful, compare the previous behavior with the new behavior.

## Footer

* Separate the footer section from the body with a blank line.
* Include only references and metadata supported by repository or user context.
* Use trailer-compatible footer tokens when applicable.
* When Conventional Commits is the fallback, use `<token>: <value>` or `<token> #<value>` semantics and use `-` instead of whitespace in footer tokens except for `BREAKING CHANGE`.
* Do not invent issue identifiers, references, reviewers, acknowledgements, or metadata.

## Breaking Changes

* Mark a backward-incompatible change with `!`, a `BREAKING CHANGE:` footer, or both.
* Place `!` immediately before `:` when no scope exists or immediately after the scope when one exists.
* A breaking change may occur with any commit type.
* If `!` is used without a `BREAKING CHANGE:` footer, the summary must clearly communicate the compatibility break.
* Prefer a `BREAKING CHANGE:` footer when consumer impact, migration requirements, removed behavior, or replacement behavior requires explanation.
* Describe what compatibility is broken and, when known, how consumers should migrate.
* Standardize new messages on `BREAKING CHANGE:`; accept `BREAKING-CHANGE:` when parsing existing Conventional Commit history.

## Atomicity

* Do not combine unrelated intentions in the same commit.
* When a change maps to multiple semantic types, split it whenever the resulting units remain valid, understandable, and appropriately verifiable.
* Split changes that have different purposes or can be meaningfully reviewed or reverted separately.
* Keep changes together when separating them would create an invalid, incomplete, unverified, or misleading intermediate state.
* Implementation and its directly related tests normally belong to the same commit when they jointly constitute one behavior change.
* Atomicity is based on logical intent and dependency, not file boundaries, file count, or diff size.

## Quality Guardrails

* Base the message on the actual staged changes or intended patch when available.
* Verify that the staged diff represents exactly one coherent logical unit before committing, and split it when it does not.
* Do not hide unrelated changes behind a broad or ambiguous commit message.
