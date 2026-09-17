---
name: plugin-diff
description: Plain-language summary of what changed between two versions of a Claude Code plugin
---

Summarize the differences between two versions of a Claude Code plugin in plain language. Ask the user for the two versions to compare if they have not provided them. They may give you two local folder paths, or a plugin name plus two version tags or branch names to check out.

Read all relevant files in both versions: `plugin.json`, `skills/*/SKILL.md`, `.mcp.json`, server code, and `README.md`.

Produce a structured summary. Only include categories where something actually changed — omit empty sections.

---

## Behavioral changes

What the skill now does differently. Summarize `SKILL.md` changes in plain language — what the skill will do differently for the user, not just that text changed. If the instructions are substantively the same, say so.

## MCP tools and external services

New or removed MCP tools. New or removed external endpoints or services contacted. If this didn't change, omit.

## Security posture

New permissions, capabilities, or blast radius changes. New or resolved dangerous behaviors. Dependency additions, removals, or version pin changes.

## Configuration changes

Fields added, changed, or removed in `plugin.json` or `.mcp.json`.

## Documentation changes

Sections added, removed, or materially rewritten in `README.md`. Do not report minor wording edits.

---

Close with a plain-language recommendation: is this a safe and worthwhile upgrade? Specifically call out any changes that warrant careful review before upgrading, particularly for `extended`-tier plugins where blast radius changes matter.
