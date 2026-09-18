# Plugin directory structure

Every plugin in this marketplace is a directory with a fixed structure. The plugin loader validates this structure on install — unknown top-level directories cause a load error.

---

## Reference layout

```
<plugin-name>/
├── .claude-plugin/
│   └── plugin.json          # Required: manifest
├── skills/
│   └── <skill-name>/
│       ├── SKILL.md         # Required: skill prompt
│       └── scripts/         # Optional: helper scripts (non-MCP plugins)
│           └── <script>.py
├── README.md                # Required: documentation
├── .mcp.json                # MCP plugins only
└── server/                  # MCP plugins only
    └── mcp_server.py        # or index.js for Node.js
```

---

## Top-level directory rules

Only these entries are valid at the plugin root:

| Entry | Required | When |
|-------|----------|------|
| `.claude-plugin/` | Yes | Always |
| `skills/` | Yes | Always |
| `README.md` | Yes | Always |
| `.mcp.json` | No | MCP plugins only |
| `server/` | No | MCP plugins only (referenced by `.mcp.json`) |
| `run-server.sh` | No | Node.js MCP plugins only |

**Any other directory at the plugin root will cause a load error.** Helper scripts, data files, and other assets that don't belong in `server/` must live inside `skills/<skill-name>/`.

---

## Helper scripts (non-MCP)

If your skill needs to run Python or Bash scripts but doesn't require an MCP server, place them inside the skill directory:

```
skills/<skill-name>/
├── SKILL.md
└── scripts/
    └── <script>.py
```

Reference them in `SKILL.md` using the `${CLAUDE_PLUGIN_ROOT}` variable:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/<skill-name>/scripts/<script>.py" <args>
```

This is the correct pattern for plugins that need structured data manipulation, file operations, or reusable logic — without the overhead of a full MCP server.

---

## The `${CLAUDE_PLUGIN_ROOT}` variable

`${CLAUDE_PLUGIN_ROOT}` expands to the plugin's installation path at runtime (e.g. `~/.claude/plugins/cache/lj-marketplace/<plugin-name>/1.0.0`). Use it whenever a `SKILL.md` or `.mcp.json` needs to reference a file bundled with the plugin.

Similarly, `${CLAUDE_PLUGIN_DATA}` expands to a writable per-plugin data directory (`~/.claude/plugins/data/<plugin-name>-lj-marketplace`). Use it for state that should persist across sessions — task lists, caches, user preferences.

---

## The plugin manifest

`.claude-plugin/plugin.json` is required in every plugin:

```json
{
  "name": "<plugin-name>",
  "description": "One-sentence description.",
  "version": "1.0.0",
  "type": "skill"
}
```

`type` is required — one of `skill` | `tool` | `app`. See [Plugin anatomy](plugin-anatomy.md) for the complete manifest and every other field a plugin can declare.

For MCP plugins, add:

```json
  "mcpServers": "./.mcp.json"
```

---

## Quick checklist

Before submitting, verify:

- [ ] `.claude-plugin/plugin.json` exists with `name`, `description`, `version`, `type`
- [ ] `skills/<name>/SKILL.md` exists
- [ ] `README.md` exists
- [ ] No unknown directories at the plugin root
- [ ] Helper scripts (if any) live under `skills/<name>/scripts/`
- [ ] All paths in `SKILL.md` and `.mcp.json` use `${CLAUDE_PLUGIN_ROOT}`, not hardcoded home directories
