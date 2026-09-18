# Claude Plugins Marketplace

This project utilises Mkdocs with the Material theme and Mermaid for
diagrams. Currently the docs are published using github actions on github pages
from the branch gh-pages, which contains static site files generated from
Markdown documents and assets. The overall configuration of the site is
stored in mkdocs.yml in the root directory of the repo. If making contributions
to docs, it can be useful to host it locally to see the effect of changes.

## Project layout (root directory)

    mkdocs.yml                # The configuration file
    requirements.txt          # mkdocs requirements file for pip, used to locally install mkdocs and its plugins (normally in a Python venv)
    Dockerfile                # Docker manifest for locally serving the site through a container (alternative to locally installing mkdocs)
    docs/                     # Documentation files in Markdown (.md), subfolders for /img, /assets, /stylesheets, /css, etc.

## Setting up and serving MkDocs locally (Linux)

A `Makefile` in the repo root handles setup and serving for you. You don't need to manually create a venv, activate it, or install requirements.

1. Clone repo and cd to its root:

    ```bash
    git clone git@github.com:ljainschigg/Larkin-Jainschigg-Marketplace.git
    cd Larkin-Jainschigg-Marketplace
    ```

2. See available make targets:

    ```bash
    make help
    ```

3. Serve the site to 127.0.0.1:8000 (auto-runs setup if needed, live-reloads on file changes):

    ```bash
    make serve
    ```

    That's it. `make serve` will create the venv and install all dependencies from `requirements.txt` automatically if they aren't already present.

4. Create a feature branch for your changes:

    ```bash
    git checkout main
    git pull origin main
    git checkout -b my-feature-branch
    (make changes)
    git push -u origin my-feature-branch  # push to origin and file Pull Request
    ```

5. To clean up the local venv:

    ```bash
    make clean
    ```

## Use containerized mkdocs instead (assumes you have Docker installed locally)

1. Build the container from the provided Dockerfile

    ```bash
    docker build -f Dockerfile -t mk-local .
    ```

2. Clone repo as in Step 1, above, and cd to repo root

3. Create and checkout your working branch, as in steps 4 and 5, above.

4. Open a new terminal session (so you can stop the container later by pressing CTRL-C) and run the container

    ```bash
    docker run --rm -it -p 8000:8000 -v ${PWD}:/docs mk-local
    ```

# Documentation Standards

By default, we follow the [Google developer documentation style guide](https://developers.google.com/style). 

## Header Capitalization

All header text should be capitalized.

---

# Plugin Development Guide

> **The canonical, always-current guide lives on the docs site:** [Plugin anatomy](https://ljainschigg.github.io/Larkin-Jainschigg-Marketplace/contributing/plugin-anatomy/) (what every plugin needs), [Plugin structure](https://ljainschigg.github.io/Larkin-Jainschigg-Marketplace/contributing/plugin-structure/) (directory layout), and [Build & submit a plugin](https://ljainschigg.github.io/Larkin-Jainschigg-Marketplace/contributing/build-and-submit/) (the process). The enforceable rules are in [`CONVENTIONS.md`](CONVENTIONS.md). The primer below covers the basics and the MCP server patterns; where it and the docs site differ, the docs site wins.

This repo is a monorepo of Claude Code plugins. Each plugin lives under `plugins/<plugin-name>/` and is independently installable via the marketplace. CI automatically discovers plugins and regenerates `marketplace.json` on every push to `main`.

## Plugin types

A plugin can contain any combination of:
- **Skills** — prompt files (`SKILL.md`) invoked with `/skill-name`
- **MCP servers** — processes that expose tools Claude can call, started automatically when the plugin loads
- Agents, hooks, LSP servers (not covered here)

A plain skill (no MCP server) is just a prompt. An MCP-equipped skill is a prompt that calls tools provided by a bundled server process.

---

## Directory structure

### Plain skill (prompt only)

```
plugins/
  my-skill/
    .claude-plugin/
      plugin.json
    skills/
      my-skill/
        SKILL.md
```

### MCP-equipped skill (Python)

```
plugins/
  my-skill/
    .claude-plugin/
      plugin.json        ← references .mcp.json
    .mcp.json            ← declares the MCP server
    skills/
      my-skill/
        SKILL.md         ← calls MCP tools by name
    server/
      mcp_server.py      ← Python MCP server with inline dependencies
```

### MCP-equipped skill (Node.js)

```
plugins/
  my-skill/
    .claude-plugin/
      plugin.json
    .mcp.json
    run-server.sh        ← wrapper: installs deps on first run, then starts server
    skills/
      my-skill/
        SKILL.md
    server/
      index.js           ← Node.js MCP server
      package.json       ← npm dependencies
```

---

## plugin.json

Minimal (plain skill):

```json
{
  "name": "my-skill",
  "description": "What this skill does.",
  "version": "1.0.0",
  "type": "skill"
}
```

With MCP server:

```json
{
  "name": "my-skill",
  "description": "What this skill does.",
  "version": "1.0.0",
  "type": "skill",
  "mcpServers": "./.mcp.json"
}
```

**Note:** Do not declare `mcpServers` inline in `plugin.json` — there is a known bug where inline declarations are silently dropped. Always reference a separate `.mcp.json` file.

---

## .mcp.json

Declares one or more MCP servers. The `command` and `args` are what Claude Code runs to start the server process.

```json
{
  "server-name": {
    "command": "uv",
    "args": ["run", "${CLAUDE_PLUGIN_ROOT}/server/mcp_server.py"]
  }
}
```

### Environment variables available in .mcp.json

| Variable | Value |
|---|---|
| `${CLAUDE_PLUGIN_ROOT}` | Path to the installed plugin directory. Use this to reference bundled scripts. |
| `${CLAUDE_PLUGIN_DATA}` | Persistent directory for this plugin's runtime data. Survives plugin updates. Use this for venvs, `node_modules`, caches, and any stateful data. |

---

## Python MCP server pattern

Use `uv run` to start the server. Declare dependencies inline using [PEP 723](https://peps.python.org/pep-0723/) at the top of the script — `uv` installs them automatically on first run, no manual `pip install` required.

```python
# /// script
# dependencies = [
#   "mcp",
#   "your-dependency-here",
# ]
# ///

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("server-name")

@mcp.tool()
def my_tool(arg: str) -> str:
    """Tool description shown to Claude."""
    return f"Result: {arg}"

if __name__ == "__main__":
    mcp.run()
```

`.mcp.json` entry:

```json
{
  "server-name": {
    "command": "uv",
    "args": ["run", "${CLAUDE_PLUGIN_ROOT}/server/mcp_server.py"]
  }
}
```

**Prerequisite:** `uv` must be installed on the user's machine. Install: `curl -LsSf https://astral.sh/uv/install.sh | sh`

---

## Node.js MCP server pattern

Because `node_modules` must live alongside the script for ES module resolution, a wrapper shell script handles first-run installation into `${CLAUDE_PLUGIN_DATA}`, which persists across plugin updates.

`run-server.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

DATA_DIR="${CLAUDE_PLUGIN_DATA}/node"
SERVER_DIR="${CLAUDE_PLUGIN_ROOT}/server"

mkdir -p "${DATA_DIR}"

# Install dependencies if not present or if package.json has changed
if [ ! -f "${DATA_DIR}/node_modules/.installed" ] || \
   [ "${SERVER_DIR}/package.json" -nt "${DATA_DIR}/node_modules/.installed" ]; then
  cp "${SERVER_DIR}/package.json" "${DATA_DIR}/"
  npm install --prefix "${DATA_DIR}" --ignore-scripts --silent
  touch "${DATA_DIR}/node_modules/.installed"
fi

# Always copy server script so reinstalls pick up code changes
cp "${SERVER_DIR}/index.js" "${DATA_DIR}/"

exec node "${DATA_DIR}/index.js"
```

`server/index.js` (ES module):

```javascript
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { CallToolRequestSchema, ListToolsRequestSchema } from "@modelcontextprotocol/sdk/types.js";

const server = new Server(
  { name: "server-name", version: "1.0.0" },
  { capabilities: { tools: {} } }
);

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [{
    name: "my_tool",
    description: "Tool description shown to Claude.",
    inputSchema: {
      type: "object",
      properties: { arg: { type: "string" } },
      required: ["arg"]
    }
  }]
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { arg } = request.params.arguments;
  return { content: [{ type: "text", text: `Result: ${arg}` }] };
});

const transport = new StdioServerTransport();
await server.connect(transport);
```

`server/package.json`:

```json
{
  "name": "my-skill-server",
  "version": "1.0.0",
  "type": "module",
  "dependencies": {
    "@modelcontextprotocol/sdk": "^1.0.0",
    "your-dependency": "^1.0.0"
  }
}
```

`.mcp.json` entry:

```json
{
  "server-name": {
    "command": "bash",
    "args": ["${CLAUDE_PLUGIN_ROOT}/run-server.sh"]
  }
}
```

**Prerequisite:** Node.js and npm must be installed on the user's machine.

---

## SKILL.md

The skill prompt tells Claude which MCP tool to call. Keep it minimal — the logic belongs in the server, not the prompt.

```markdown
---
name: my-skill
description: What this skill does.
---

Call the `my_tool` tool with the user's input.
Return the result exactly as the tool returns it.
```

---

## Adding a plugin to the marketplace

There are two paths. The full, step-by-step walkthrough (prerequisites, the Plugin
Dev Tools, verification, and what happens after you submit) lives in the docs:
**[Build & submit a plugin](https://ljainschigg.github.io/Larkin-Jainschigg-Marketplace/contributing/build-and-submit/)**.

**Contributors (default) — open a PR:**
1. Scaffold with `/plugin-scaffold`, build your skill, then run `/plugin-docs-lint`
   and `/plugin-security-check` and clear any BLOCKERs.
2. Run `/submit-plugin` — it runs the security check, files a PR with the report,
   and a curator reviews and merges it.

**Maintainers (write access) — direct push of complete, validated work:**
1. Create `plugins/<your-plugin-name>/` following the structure above.
2. Publish in one step: `make publish m="Add <your-plugin-name>"` (or `scripts/publish.sh`).
   This regenerates `.claude-plugin/marketplace.json` from `plugins/`, commits it with
   your changes, and pushes to `main` (a live production deploy).

Either way, users then run `/plugin marketplace update lj-marketplace` to pick up the plugin.

`.claude-plugin/marketplace.json` is the committed index the `github` marketplace source
reads; it is generated entirely from `plugins/` — never hand-edit it. If you ever push
plugin changes without regenerating (e.g. a manual `git push` that bypasses `make publish`),
the `publish-check` workflow fails and tells you to run the generator, so the index can't
silently drift. The docs site on gh-pages redeploys automatically on every push to `main`.

---

## Working examples

| Plugin | Runtime | External dependency |
|---|---|---|
| `example-skill` | None (prompt only) | — |
| `example-mcp-python-skill` | Python via `uv` | `cowsay` |
| `example-mcp-node-skill` | Node.js via `npm` | `figlet` |

