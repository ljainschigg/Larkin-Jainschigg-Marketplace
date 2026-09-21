---
description: "Check that a plugin's README meets this marketplace's documentation standards, and see what is missing."
---

# plugin-docs-lint

Fast check that a plugin's `README.md` meets the documentation standards required for marketplace submission. Lighter-weight than [`plugin-security-check`](plugin-security-check.md) — useful to run frequently as you write, rather than waiting until the plugin is finished.

---

## Install

```
/plugin install plugin-docs-lint@Larkin-Jainschigg-Marketplace
```

## Use

```
/plugin-docs-lint
```

Claude will check the `README.md` in your current directory, or ask for a path if one is not found.

---

## What it checks

**Structure**

- All required sections are present: description, install instructions, usage, details table
- No sections are empty or contain only placeholder text
- The details table includes version and maintainer fields

**Content quality**

- The description accurately conveys what the plugin does (no vague or generic language)
- Prerequisites are stated if the plugin has any
- If the plugin uses MCP tools or external services, they are listed
- Dangerous operations are documented with appropriate warnings
- The README matches what the `SKILL.md` and any MCP server code actually do

**Style**

- Headers follow sentence case per the marketplace documentation style guide
- No broken markdown (unclosed fences, malformed tables, etc.)

---

## Output

A list of findings with suggested fixes. Unlike [`plugin-security-check`](plugin-security-check.md), all findings are advisory — this tool does not block anything. Its purpose is to help you write good documentation, not to gate submission.

---

## Details

| | |
|---|---|
| **Version** | 1.1.4 |
| **Maintained by** | Claude Plugins Marketplace |
