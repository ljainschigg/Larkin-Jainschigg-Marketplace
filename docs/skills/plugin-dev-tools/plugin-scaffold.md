# plugin-scaffold

Generates a complete, correctly structured plugin directory from a plain-language description of what you want the plugin to do. Produces all required files with stubs pre-filled — so you start from a baseline that will pass format compliance checks rather than copying and adapting an example by hand.

---

## Install

```
/plugin install plugin-scaffold@lj-marketplace
```

## Use

```
/plugin-scaffold
```

Claude will ask for:

- What you want the plugin to do (plain language description)
- The plugin name (kebab-case)
- Whether it needs an MCP server (and if so, Python or Node.js)
- Which tier it belongs to (`platform`, `local`, or `extended`)

---

## What it generates

**For all plugins:**

```
<plugin-name>/
├── .claude-plugin/
│   └── plugin.json          # name, description, version pre-filled
├── skills/
│   └── <plugin-name>/
│       └── SKILL.md         # stub prompt based on your description
└── README.md                # template with all required sections pre-filled
```

**Additionally, for MCP plugins:**

```
├── .mcp.json                # server declaration
└── server/
    ├── mcp_server.py        # (Python) FastMCP stub with hello-world tool
    └── package.json         # (Node.js) package stub
    └── index.js             # (Node.js) MCP server stub
```

---

## After scaffolding

The generated files are stubs — they compile and pass format checks, but you need to fill in the actual logic. Run [`plugin-docs-lint`](plugin-docs-lint.md) as you write the README, and [`plugin-security-check`](plugin-security-check.md) when you think it's ready.

---

## Details

| | |
|---|---|
| **Version** | 1.2.6 |
| **Maintained by** | Claude Plugins Marketplace |
