---
name: plugin-scaffold
description: Generates a complete, correctly structured Claude Code plugin directory from a plain-language description
---

Generate a new Claude Code plugin directory. Gather the following from the user before creating any files:

1. What the plugin should do (plain language)
2. Plugin name — suggest a kebab-case name based on their description and confirm it
3. Does it need external code?
   - **No** — pure prompt/skill with no scripts
   - **Helper scripts (no MCP)** — bundled Python or Bash scripts called from the SKILL.md
   - **MCP server — Python** (via `uv`)
   - **MCP server — Node.js** (via `npm`)
4. Which tier: `platform`, `local`, or `extended`
5. Their name or team name (for the README maintainer field)
6. Beyond the MCP runtime itself (if any), does it shell out to any other system binary — `git`, `gh`, `ffmpeg`, a browser, etc.? Only relevant for helper-script or MCP plugins; skip for pure prompt skills.

Create a new directory named `<plugin-name>` in the current working directory containing the following files:

---

### `.claude-plugin/plugin.json`

```json
{
  "name": "<plugin-name>",
  "description": "<one-sentence description derived from what the user told you>",
  "version": "1.0.0",
  "type": "<skill|tool|app>"
}
```

Add `"mcpServers": "./.mcp.json"` if the plugin uses MCP.

Set `type` per `CONVENTIONS.md`: **`tool`** if it needs credentials or reaches an external service (MCP/API); otherwise **`skill`** (`app` is reserved for personal instances). There is no `source_of_truth` field — this repo is canonical; the plugin is developed and edited in place here.

---

### `skills/<plugin-name>/SKILL.md`

Write a real SKILL.md prompt based on what the user described — not a placeholder. Keep it concise and action-oriented. If you cannot write the full logic from the description alone, write the best stub you can and note clearly what the user needs to fill in.

---

### `README.md`

Generate a complete README with these sections in order:
- `# <plugin-name>` — H1 heading
- Description paragraph (what it does and why it's useful)
- `## Prerequisites` — if the plugin requires any tools, accounts, or permissions; omit this section if there are none
- `## Install` — with the `/plugin install <plugin-name>@lj-marketplace` command
- `## Use` — with the `/<plugin-name>` invocation and a brief description of what happens
- `## How it works` — one short paragraph on the implementation approach
- `## Details` — table with Version, Tier, and Maintained by fields

---

### For plugins with helper scripts (no MCP), also create:

**`skills/<plugin-name>/scripts/<plugin-name>.py`** (Python) or **`skills/<plugin-name>/scripts/<plugin-name>.sh`** (Bash) — a real, self-documenting script stub based on what the user described. Include:

- A module-level docstring listing all subcommands and their arguments
- At least one meaningful subcommand stub (not just `pass`) that reflects the plugin's actual purpose
- Argparse (Python) or `case` statement (Bash) for structured CLI invocation

In the `SKILL.md`, reference the script using `${CLAUDE_PLUGIN_ROOT}`:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/<plugin-name>/scripts/<plugin-name>.py" <subcommand> [args]
```

Do **not** place scripts at the plugin root — the loader only allows `skills/`, `server/`, `.claude-plugin/`, `.mcp.json`, `run-server.sh`, and `README.md` at the top level.

---

### For MCP Python plugins, also create:

**`.mcp.json`**
```json
{
  "<plugin-name>-server": {
    "command": "uv",
    "args": ["run", "${CLAUDE_PLUGIN_ROOT}/server/mcp_server.py"]
  }
}
```

**`server/mcp_server.py`** — FastMCP stub with PEP 723 inline dependencies and one placeholder tool named after the plugin's purpose. Include the uv script header:
```python
# /// script
# dependencies = ["mcp", "fastmcp"]
# ///
```

---

### For MCP Node.js plugins, also create:

**`.mcp.json`**
```json
{
  "<plugin-name>-server": {
    "command": "bash",
    "args": ["${CLAUDE_PLUGIN_ROOT}/run-server.sh"]
  }
}
```

**`run-server.sh`** — install-and-run wrapper that checks for `node_modules` in `${CLAUDE_PLUGIN_DATA}`, runs `npm install` on first run, copies the server to the data directory, and starts it with Node. Make it executable.

**`server/package.json`** — minimal package with `"type": "module"` and `@modelcontextprotocol/sdk` as a dependency.

**`server/index.js`** — ES module MCP server stub with one placeholder tool.

---

### For any MCP plugin (Python or Node.js), also create a `setup` skill

Per `CONVENTIONS.md` §5, every MCP-equipped plugin ships a `skills/setup/SKILL.md` so users can verify the runtime before their first real use, rather than hitting a confusing failure mid-workflow. Model it on the reference implementations (`example-mcp-python-skill`, `example-mcp-node-skill`, `researcher`):

```markdown
---
name: setup
description: One-time setup check for <plugin-name>. Run this after installing the plugin.
---

## Step 1 — Check the runtime

!`uv --version 2>&1 || true`   <!-- or `node --version 2>&1 && npm --version 2>&1 || true` for Node -->

If not found, stop and tell the user to install it before continuing.

## Step 2 — Verify the MCP server is available

Call the `<placeholder-tool-name>` MCP tool. If it responds, the server is running correctly.

If not, tell the user the server isn't responding, that it starts automatically via `.mcp.json` when Claude Code loads the plugin, and to try restarting Claude Code / check the runtime is on PATH.

## Done

Tell the user setup is complete and how to invoke the plugin.
```

**Keep `` !`…` `` blocks to lightweight checks only.** Every `` !`…` `` block in a skill runs at load time, top-to-bottom, *before* the model reads any content, and a non-zero exit **aborts the whole skill** — which is why the check above ends in `|| true` (so a missing tool yields readable output instead of killing setup). Never use `` !`…` `` for heavy installs (e.g. `npx playwright install`), for ordered/conditional logic, or for creating files such as a credentials `.env`. Do that as **model-run Bash/Write steps** so it happens in order and can't abort the skill. See the `researcher` and `get-pdfs` setup skills for the model-driven pattern (create-if-missing, never clobber).

If the user answered "yes" to question 6 (other system binaries), add an extra check step for each one named, in the same fail-loud, stop-don't-guess style — check version/presence, and if missing, tell the user exactly what to install and where.

Reference this skill from the README's `## Prerequisites` section and `/setup` from `## Install`, so the two stay in agreement (CONVENTIONS.md §5's README-agreement rule).

### For helper-script plugins (no MCP) with an external binary named in question 6

No separate `setup` skill needed — add a Step 0 to the main `SKILL.md` that checks the binary is present and stops with clear guidance if not, before any step that depends on it.

### For plugins that need credentials (reach a system of record / artifacts on the user's behalf)

Any plugin that uses a user's API key, OAuth secret, or token must follow the credential standard ([Plugin anatomy → Credentials](https://ljainschigg.github.io/Larkin-Jainschigg-Marketplace/contributing/plugin-anatomy/#credentials); `CONVENTIONS.md` §3). Emit all of this:

1. **Declare the keys** in `plugin.json` → `requires_credentials`, as `<domain>/<service>/<field>` (e.g. `["personal/<service>/client_id", "personal/<service>/client_secret"]`). Never store values.
2. **Read them server-side, in this order,** inside the plugin's MCP server / bundled script — never surface a raw secret to the model:
   1. env var `<SERVICE>_<FIELD>` (bring-your-own — lets the user inject from their own secrets tool),
   2. `secret-resolver` (`get_secret("<domain>/<service>/<field>")`),
   3. else fail loud, pointing at `/setup`.
   (See diet's `server/creds.py` for the reference implementation of this read order.)
3. **Emit a credential negotiation in the `setup` skill** that:
   - detects whether `secret-resolver` is installed/adopted (and runs `secret-resolver status`),
   - asks whether to use `secret-resolver` or the user's own env-injected solution,
   - instructs the user to get each `requires_credentials` key into the chosen solution — via `printf '%s' "$VALUE" | secret-resolver set <key> --stdin` (user enters the value; never argv, never necessarily through the model) **or** by exporting the `<SERVICE>_<FIELD>` env vars from their tool,
   - confirms the read path works before finishing.
   Model it on diet's `/diet setup` Step 4.

The tool is available (`secret-resolver`) and recommended — but the standard is that the plugin uses **a** proper credential mechanism (resolver or bring-your-own), never embeds secrets, and never hands raw credentials to the model.

### For plugins that write user data / PII (research, transcripts, logs, drafts, outputs)

PII is *not* credentials — don't route it through `secret-resolver`. It's the user's own data, which the model does work with; the control is location + keeping it out of version control ([Plugin anatomy → Personal data](https://ljainschigg.github.io/Larkin-Jainschigg-Marketplace/contributing/plugin-anatomy/#personal-data-pii)). Emit this:

- Store project-scoped data in the user's **project/working folder** (`<project-dir>/resources/`, `<project-dir>/outputs/`, etc.); cross-session profile/config can go in `${CLAUDE_PLUGIN_DATA}` (outside any repo). Never in the plugin.
- Add a step to the skill that **ensures a `.gitignore`** covers the data/output paths (and any cloned reference material) whenever the plugin writes into a folder that could be a git repo — create or append it — and **never `git add`/commit** the user's data.

---

After creating all files, summarize what was created and what the user needs to fill in. Suggest running `/plugin-docs-lint` on the README as they develop, and `/plugin-security-check` when they think it's ready.
