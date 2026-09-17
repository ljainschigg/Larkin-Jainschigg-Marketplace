---
name: setup
description: One-time setup for researcher. Run this after installing the plugin.
---

Work through these steps **in order, yourself, using the Bash tool** — do not assume anything ran automatically. Report each step's result. **Stop and report if a required step fails; do not continue past a failure.**

> Why this is model-driven: a skill's `` !`…` `` blocks all run at load time, top-to-bottom, before these instructions are read, and any non-zero exit aborts the whole skill. Ordered, conditional, and state-creating setup must therefore be run step-by-step with the Bash tool, not with `` !`…` `` blocks.

This plugin stores your credentials in its own data directory. That absolute path is:

!`echo "${CLAUDE_PLUGIN_DATA}"`

Call that path **`DATA_DIR`** in the steps below, and always use the literal path shown above in your Bash commands (do not use the string `${CLAUDE_PLUGIN_DATA}` in a Bash command — it may not be set in your shell).

## Step 1 — Check Node.js version (must be ≥ 20)

Run with the Bash tool:

```
node --version
```

**Node.js 20 or higher is required** — the Playwright MCP server (`@playwright/mcp`) enforces Node ≥20 at runtime, and Node 18 is end-of-life. The version that matters is whatever `node`/`npx` resolves to on the user's `$PATH`, because the MCP servers launch via bare `npx`.

- If it prints **v20 or higher**, continue.
- If `node` is **not found**, or the version is **below 20**, **stop** and tell the user:

  > researcher's Playwright MCP server needs **Node 20+**, but the `node` on your `$PATH` is **[version shown, or "not found"]**. If you already have Node 20+ installed elsewhere (nvm, `~/.local/node20/`, Homebrew), put its `bin` directory **first on your `$PATH`** and restart Claude Code — a bare `npx` (and Playwright's `#!/usr/bin/env node` shebang) will otherwise keep resolving the old Node. If you don't have Node 20+ at all, install it from https://nodejs.org.

## Step 2 — Install the Playwright browser

Run with the Bash tool (this can take a minute — it downloads Chromium):

```
npx playwright install chromium
```

Safe to re-run — it confirms the binary is up to date if already installed. If it fails, report the full error and stop; Playwright is required for JS-rendered pages and gated PDFs.

## Step 3 — Create the contact-details file (only if missing)

Check whether `DATA_DIR/.env` already exists (use the literal `DATA_DIR` path from the top of this skill):

```
test -f "DATA_DIR/.env" && echo EXISTS || echo MISSING
```

- **If MISSING**, create it — make the directory, then write these exact contents to `DATA_DIR/.env` (use the Write tool, or a Bash heredoc):

  ```
  RESEARCHER_NAME=
  RESEARCHER_EMAIL=
  RESEARCHER_COMPANY=
  RESEARCHER_TITLE=
  RESEARCHER_PHONE=
  RESEARCHER_COUNTRY=
  RESEARCHER_STATE=
  ```

  Then tell the user:

  > Your contact-details file has been created at `DATA_DIR/.env`. Open it and fill in your work contact details (name, email, company, title, phone, country, state). This is contact info used to fill forms on gated research landing pages — **profile data, not credentials**. It stays on your machine (in the plugin's data dir, outside any project repo) and is never shared.

- **If EXISTS**, do **not** overwrite it. Read it, and if any `RESEARCHER_` value is blank, prompt the user to fill it in before running research.

## Step 4 — Verify the Playwright MCP server

Attempt a Playwright tool (e.g. navigate to `about:blank`). If it responds, confirm to the user. If not:

> The Playwright MCP server is not running. It's configured in `.mcp.json` and starts automatically when Claude Code loads the plugin. Restart Claude Code; if it still fails, confirm `node --version` reports 20+ on your `$PATH` and that Step 2 completed.

## Step 5 — Verify the extract-pdf MCP server

Call the `extract_pdf` tool with a clearly invalid source to confirm it responds (an error message is fine — that means the server is up). If unavailable:

> The extract-pdf MCP server is not running. It starts via `run-server.sh` when the plugin loads. Confirm Node.js and npm are on your `$PATH`.

## Done

If all steps pass, tell the user:

> Setup complete. You're ready to run `/research`.
