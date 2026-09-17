# example-mcp-python-skill

Demonstrates a skill backed by a Python MCP server. When invoked, it calls a running Python process via the Model Context Protocol and returns a cowsay greeting. Proof of life for the Python MCP plugin pattern.

---

## Prerequisites

[uv](https://docs.astral.sh/uv/) must be installed. It handles Python and dependency management automatically — no separate `pip install` needed.

---

## Install

If you haven't added the marketplace yet:

```
/plugin marketplace add ljainschigg/generic-marketplace-2
```

Then install the plugin:

```
/plugin install example-mcp-python-skill@claude-plugins
```

After installing, run setup to confirm `uv` is present and the server responds:

```
/setup
```

## Use

```
/example-mcp-python-skill
```

Claude will call the `hello_python` MCP tool and return a cowsay greeting.

---

## How it works

On install, a Python MCP server starts alongside Claude Code. The server declares a `hello_python` tool. The skill's only job is to call that tool — all the Python logic lives in the server, not the prompt.

Dependencies (`mcp`, `cowsay`) are declared inline in the script using [PEP 723](https://peps.python.org/pep-0723/) and installed automatically by `uv` on first run.

---

## Details

| | |
|---|---|
| **Version** | 1.1.3 |
| **Runtime** | Python via `uv` |
| **External dependency** | `cowsay` |
| **Maintained by** | Claude Plugins Marketplace |
