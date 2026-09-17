---
name: plugin-security-check
description: Deep security and compliance inspection of a Claude Code plugin folder
---

Perform a comprehensive security and compliance review of a Claude Code plugin folder. If the user has not provided a path, ask for one now. Do not proceed without a path.

Read all files in the folder systematically: `.claude-plugin/plugin.json`, `skills/*/SKILL.md`, `.mcp.json` (if present), any `server/` code files, `README.md`, and any other files present.

Evaluate against each category below, then produce the report described at the end.

---

## Format compliance

- `plugin.json` exists, is valid JSON, and has `name`, `description`, and `version` fields
- `version` follows semantic versioning (e.g., `1.0.0`)
- Plugin name in `plugin.json` matches the folder name exactly
- `skills/<name>/SKILL.md` exists, where `<name>` matches the plugin name
- If `mcpServers` is declared in `plugin.json`, it must be a file path to `.mcp.json` — not an inline object
- If `.mcp.json` exists: it is valid JSON and all referenced command paths and scripts exist within the plugin folder
- `README.md` exists and is non-empty
- **[Conventions]** `plugin.json` declares `type` as one of `skill` | `tool` | `app`
  - *🚫 BLOCKER if missing/invalid. See `CONVENTIONS.md`. (There is no `source_of_truth` field — this repo is canonical; plugins are edited in place, not copied from an external source.)*
- **[Conventions]** If the plugin has `.mcp.json`, or shells out to a system binary beyond what its own runtime auto-installs (`git`, `gh`, `ffmpeg`, `pass`, a browser, etc.), it has a `skills/setup/SKILL.md` or a documented inline Step 0 preflight in its main `SKILL.md` checking the same things its README's `## Prerequisites` section lists
  - *🚫 BLOCKER — no rollout warning period for this one. See `CONVENTIONS.md` §5.*
- **[Conventions]** If the plugin uses credentials (declares `requires_credentials`, or its code reads API keys / OAuth secrets / tokens), it follows the credential standard: keys declared in `requires_credentials`; read **server-side** in the order env `<SERVICE>_<FIELD>` → `secret-resolver` → fail loud (a raw secret is never surfaced to the model); and its `setup` runs the credential negotiation (detect `secret-resolver` → ask resolver-or-bring-your-own → instruct storing each key via stdin/env → confirm the read path). Flag a credentialed plugin missing the declaration, the server-side env/resolver read path, or the setup negotiation.
  - *🚫 BLOCKER. See `CONVENTIONS.md` §3 and [Plugin anatomy → Credentials](https://ljainschigg.github.io/generic-marketplace-2/contributing/plugin-anatomy/#credentials).*
- **[Conventions]** If the plugin writes the user's own data (PII — research, transcripts, logs, drafts, downloads, cloned repos) into a project/working folder, its skill ensures that data is `.gitignore`d (creates/appends `.gitignore` for the data/output paths and any cloned material) and never `git add`/commits it. PII lives in a user-owned location — never in the plugin, never via `secret-resolver`. Flag a data-writing plugin with no `.gitignore` step.
  - *🚫 BLOCKER. See `CONVENTIONS.md` §3 and [Plugin anatomy → Personal data](https://ljainschigg.github.io/generic-marketplace-2/contributing/plugin-anatomy/#personal-data-pii).*

## Credential and secret exposure

Scan every file for:
- API keys, tokens, bearer strings
- AWS (`AKIA…`), GCP, or Azure credential patterns
- PEM blocks or private key material
- Variables named `password`, `secret`, `token`, `key`, or `api_key` assigned a literal value
- Included `.env` files
- Connection strings or authentication material of any kind

## Dangerous behaviors

Review `SKILL.md` and any server code for:
- Destructive operations (`rm`, delete, overwrite, database drop/truncate, `git reset --hard`, `push --force`) that do not require explicit user confirmation before executing
- Sending messages, emails, notifications, or posts to external parties without confirmation
- Instructions that bypass user review for any consequential operation
- **Prompt injection risk**: if the plugin reads external content (files, URLs, API responses) and passes it unsanitized to Claude, flag it — malicious content in those sources could redirect Claude's behavior
- For MCP plugins: list every external endpoint the server code contacts

## Blast radius

Rate the plugin's potential impact scope and justify in one paragraph:

- **LOCAL** — operates only on files the user explicitly provides
- **MODERATE** — affects the broader local environment (scans directories, modifies local git state)
- **ELEVATED** — affects external systems, remote repositories, cloud resources, or sends data outside the machine

## Dependency and supply chain (MCP plugins only)

- Are dependency versions pinned or floating?
- Flag any packages with known vulnerability history
- Note if dependencies are pulled from public registries
- Note any license compatibility concerns for internal use

If no MCP server is present, state "N/A".

## Documentation quality

- Does the README accurately describe what the plugin does? Compare against `SKILL.md` and server code and flag discrepancies.
- Are dangerous operations or elevated blast radius documented with warnings?
- Are prerequisites stated?
- Are MCP tools and external services listed?
- Is the README complete enough for a new user to install and use the plugin safely?

---

## Report format

Produce a report with a section per category. Format each finding as one of:

🚫 **BLOCKER:** description
⚠️ **WARNING:** description
ℹ️ **INFO:** description

If a category has no findings, write "No issues found."

Close with:

---
**Verdict: PASS / PASS WITH WARNINGS / FAIL**

- **FAIL** — any BLOCKERs present
- **PASS WITH WARNINGS** — warnings present, no blockers
- **PASS** — only INFO findings or none

---

After the verdict:
- If **FAIL**: list the BLOCKERs that must be resolved and offer to help fix them.
- If **PASS WITH WARNINGS**: list each warning and ask the user to explicitly acknowledge it before any submission proceeds.
