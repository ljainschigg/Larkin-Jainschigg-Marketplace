---
name: kb-archive
description: Archives a topic area's current wiki articles for a major version transition, resets them to fresh stubs, and prepares them for recompilation from new sources.
---

This skill runs from the knowledge base root directory (where `CLAUDE.md` lives).

Read `./CLAUDE.md` fully before taking any action.

Use this only when an entire topic area's documentation is being replaced by a
new version — NOT for incremental updates (use the supersession mechanism in
the compile workflow for those).

## Inputs (ask if not provided)
- **Topic area**: the `wiki/<area>/` to archive.
- **Version being archived**: e.g. `v1.x` or `2024`.
- **Reason**: e.g. "v2.0 docs added to raw/ and ready to compile".

## Steps
1. Create `wiki/<area>/archive/<version>/`.
2. **Copy (do not move)** all current article `.md` files from `wiki/<area>/`
   into the archive dir. Do NOT copy `_index.md` or `features/` — substantive
   articles only.
3. Add a stale banner after the frontmatter of each archived article:
   ```
   > [!stale]
   > This article reflects [area] [version]. Current documentation is at
   > [[wiki/<area>/_index|<Area> — Current]].
   ```
4. Reset each current article to a fresh stub: keep frontmatter but set
   `last_compiled: ""`, `sources_used: []` (and `superseded_sources: []` if
   present), replace the body with the placeholder text from
   `wiki/TEMPLATE_article.md`, and add a `> [!uncited]` callout.
5. Add an "Archived Versions" entry to `wiki/<area>/_index.md`:
   ```
   ## Archived Versions
   | Version | Archive Index |
   |---------|--------------|
   | [version] | [[wiki/<area>/archive/<version>/_index|<version> Archive]] |
   ```
   Create `wiki/<area>/archive/<version>/_index.md` listing the archived articles.
6. Update `wiki/_index.md` to note the version transition in the stats block.
7. Run `/kb-compile` to populate the fresh articles from the new version's raw
   sources.

## What this preserves
All raw sources (untouched), all archived articles with full citation history,
wikilinks within archived articles, and an active `wiki/<area>/` reflecting the
new version only.
