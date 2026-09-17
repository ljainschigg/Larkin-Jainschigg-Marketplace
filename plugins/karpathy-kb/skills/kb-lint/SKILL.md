---
name: kb-lint
description: Checks the knowledge base for structural problems — broken links, missing citations, index drift, and resolved conflicts — and fixes them.
---

This skill runs from the knowledge base root directory (where `CLAUDE.md` lives).

Read `./CLAUDE.md` fully before taking any action. It contains all lint rules and formatting conventions for this knowledge base.

## What this skill does

It finds and fixes structural problems in the wiki. It does NOT make substantive edits to article content — only structural and navigational issues.

## Steps

`/kb-lint` performs six structural checks. A bundled Python script does the mechanical ones deterministically with auto-fix; if Python is unavailable, do the same checks by hand.

### Preferred — run the bundled linter

1. Preview issues without changing anything:
   ```
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/lint.py" --dry-run --vault-root .
   ```
   If `python3` is not found, use the **Fallback** below instead.

2. Show the user the summary, then apply fixes:
   ```
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/lint.py" --vault-root .
   ```
   It auto-fixes broken wikilinks, uncited articles, `_index.md` drift, and resolved-conflict moves, and checks supersession integrity. Two checks are report-only — **unknown citation source-ids** and **unmarked supersession** — fix those manually in the affected articles.

### Fallback (no Python) — manual Lint Workflow

Perform these six checks by hand, exactly as described in `./CLAUDE.md`:

1. **Broken wikilinks** — scan all wiki articles for `[[links]]` that point to non-existent files. Replace each with `[[MISSING: original-path]]`. Log them in the lint report.

2. **Citations without source files** — scan all citations in wiki articles for source-ids not present in `raw/_registry.md`. Flag each in `wiki/_conflicts.md` under a `## Structural Issues` section.

3. **Articles without citations** — for every wiki article that has no inline citations and no `> [!uncited]` callout already, add one at the top:
   ```
   > [!uncited]
   > This article has no citations yet. Run /kb-compile to populate it from raw sources.
   ```

4. **Stale cross-references** — check links between topic area wikis for references to deleted or renamed articles. Replace with `[[MISSING: path]]`.

5. **`_index.md` drift** — for each topic area directory, compare articles present on disk against what is listed in the nearest `_index.md`. Add any unlisted articles to the index.

6. **Resolved conflicts** — in `wiki/_conflicts.md`, find any entries whose frontmatter contains `resolved: true`. Move them from `## Open` to `## Resolved`.

## Report

After completing all checks, report:
- Broken links found and replaced (count and paths)
- Citation orphans flagged (count)
- Articles marked uncited (count)
- Index drift corrections (count)
- Conflicts moved to resolved (count)
- Any issues that require human judgment to fix (list specifically)
