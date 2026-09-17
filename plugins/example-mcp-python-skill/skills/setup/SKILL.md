---
name: setup
description: One-time setup check for example-mcp-python-skill. Run this after installing the plugin.
---

Run the following checks in order. Report the result of each step clearly. Stop and report if a step fails — do not proceed past it.

## Step 1 — Check `uv`

!`uv --version 2>&1 || true`

`uv` manages Python and installs the server's dependencies (`mcp`, `cowsay`) automatically on first run — no separate `pip install` needed. If not found, stop and tell the user to install it from https://docs.astral.sh/uv/ before continuing.

## Step 2 — Verify the MCP server is available

Call the `hello_python` MCP tool with any name argument. If it returns a cowsay greeting, the server is running correctly.

If the tool is not available, tell the user:

> The example-mcp-python-skill MCP server is not responding. It's configured in `.mcp.json` and starts automatically when Claude Code loads the plugin, via `uv run`. Try restarting Claude Code. If it still fails, check that `uv` is on your PATH and that Step 1 passed.

## Done

If both steps pass, tell the user:

> Setup complete. Run `/example-mcp-python-skill` to see it in action.
