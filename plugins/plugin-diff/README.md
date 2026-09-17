# plugin-diff

Produces a plain-language summary of what changed between two versions of a plugin — in both code and behavior. Useful before upgrading an installed plugin, particularly for `extended`-tier plugins where understanding changes to blast radius and external service access matters.

---

## Install

```
/plugin install plugin-diff@claude-plugins
```

## Use

```
/plugin-diff
```

Claude will ask for two plugin folders to compare (or a plugin name to compare your installed version against the latest in the marketplace).

---

## What it covers

**Behavioral changes**

- Changes to what the skill does (SKILL.md diff summarized in plain language)
- New or removed MCP tools
- New or removed external services or endpoints contacted
- Changes to what files or systems the plugin can access

**Security posture changes**

- New permissions or capabilities added
- Changes to blast radius (scope of files touched, services called)
- Dependency additions, removals, or version changes

**Format changes**

- Fields added or removed from `plugin.json`
- Changes to MCP server configuration

**Documentation changes**

- Sections added, removed, or materially rewritten in `README.md`

---

## Output

A structured summary organized by category, written for a non-technical reader where possible. The goal is to answer the question: *"Is it safe and worthwhile to upgrade?"*

---

## Details

| | |
|---|---|
| **Version** | 1.0.2 |
| **Maintained by** | Claude Plugins Marketplace |
