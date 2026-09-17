---
name: kb-compile
description: Runs an incremental compile pass — reads uncompiled raw sources and updates wiki articles with full provenance citations.
---

This skill runs from the knowledge base root directory (where `CLAUDE.md` lives).

Read `./CLAUDE.md` fully before taking any action. It contains all processing rules, source-type handling, conflict protocols, and formatting conventions for this knowledge base.

## What this skill does

It finds all uncompiled raw sources, extracts claims with full provenance, and updates the wiki incrementally. It does not rewrite articles from scratch — it adds to them.

## Steps

Follow the **Compile Workflow** in `./CLAUDE.md` exactly:

1. Read `raw/_registry.md` and identify all entries where `compiled: false`. If there are none, report that and stop.

2. For each uncompiled source:
   - Read the file's frontmatter to understand type, date, participants/author, and topics
   - **Check for supersession first**: if the frontmatter has a non-empty `supersedes:` list, apply the supersession protocol in `CLAUDE.md` BEFORE extracting new claims — mark affected wiki claims `[!superseded]`, add the new claim below, and update the article's `superseded_sources`. Supersession is not a conflict.
   - Extract all claims per the source-type rules in `CLAUDE.md`
   - Update relevant wiki articles incrementally — add new claims, update refined claims, invoke conflict protocol for contradictions
   - Create new articles or sections as needed using the article template format

3. After processing all sources, update:
   - `wiki/_index.md` (stats block and any new articles)
   - The relevant topic `wiki/[area]/_index.md` files
   - `wiki/_sources.md`

4. Mark each processed source in `raw/_registry.md` with `compiled: true` and `compiled_date: [today's date]`.

5. Print a compile report:
   - Sources processed (count and IDs)
   - Wiki articles created (paths)
   - Wiki articles updated (paths)
   - Conflicts logged (count and slugs)

6. Run the linter to catch structural issues the compile may have introduced, and resolve what it reports:
   ```
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/lint.py" --vault-root .
   ```
   If `python3` is unavailable, run `/kb-lint` instead (manual fallback). Fix any unknown source-ids or unmarked supersession it flags.

Work methodically. When a source is ambiguous, prefer to add a citation with a `> [!intent]` or `> [!uncited]` note rather than omit the claim.
