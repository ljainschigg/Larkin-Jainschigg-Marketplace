---
name: setup
description: One-time setup check for example-mcp-node-skill. Run this after installing the plugin.
---

Run the following checks in order. Report the result of each step clearly. Stop and report if a step fails — do not proceed past it.

## Step 1 — Check Node.js and npm

!`node --version 2>&1 && npm --version 2>&1 || true`

Node.js and npm must both be installed ([nodejs.org](https://nodejs.org)). If either is missing, stop and tell the user to install Node.js before continuing — `run-server.sh` needs both to install dependencies and start the MCP server.

## Step 2 — Verify the MCP server is available

Call the `hello_node` MCP tool with any name argument. If it returns a figlet greeting, the server is running correctly.

If the tool is not available, tell the user:

> The example-mcp-node-skill MCP server is not responding. It's configured in `.mcp.json` and starts automatically when Claude Code loads the plugin, via `run-server.sh`. Try restarting Claude Code. If it still fails, check that `node` and `npm` are on your PATH — you can test the wrapper manually with `bash run-server.sh` from the plugin directory (with `CLAUDE_PLUGIN_ROOT` and `CLAUDE_PLUGIN_DATA` set).

## Done

If both steps pass, tell the user:

> Setup complete. Run `/example-mcp-node-skill` to see it in action.
