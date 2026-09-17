---
name: kb-ingest
description: Bulk-register every new raw source file dropped into the knowledge base at once, then offer to compile. The batch equivalent of kb-add.
---

This skill runs from the knowledge base root directory (where `CLAUDE.md` lives).

Read `./CLAUDE.md` fully before taking any action.

## What this skill does

It scans all `raw/` subdirectories for source files not yet in
`raw/_registry.md`, validates their frontmatter, and registers them in one
pass — the batch equivalent of `/kb-add` (which handles a single file). Use it
after dropping several files into `raw/` at once.

## Steps

1. **Preview** what would be registered, without changing anything:
   ```
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/sync-registry.py" --dry-run --vault-root .
   ```
   - If `python3` is not found, fall back to `/kb-add` for each file
     individually (it does the same validation by prompt).
   - The script exits `0` (nothing new), `1` (new sources found), or `2`
     (some files have frontmatter errors and were skipped).

2. **Show the user** the list of new sources found and — if the script
   reported any — the frontmatter errors, with the specific fix for each
   (each source needs a valid `source_id` matching `YYYY-MM-DD_type_slug`, a
   `type` of transcript/slack/deck/misc, a `YYYY-MM-DD` `date`, and a
   **non-empty `topics:` list**).

3. **Confirm, then register.** On the user's go-ahead, run without `--dry-run`:
   ```
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/sync-registry.py" --vault-root .
   ```
   Valid files are appended to `raw/_registry.md` with `compiled: false`; any
   file with frontmatter errors is left unregistered for the user to fix and
   re-run.

4. **Report** how many sources were registered and list any that were skipped
   with errors.

5. **Offer to compile.** Ask whether to run `/kb-compile` now to ingest the
   newly registered sources into the wiki. (People/handle mapping into
   `wiki/cross-cutting/org-and-people.md` happens during compile, per the
   Compile Workflow in `./CLAUDE.md`.)

## Notes

- The registry stays the single source of truth for what has been ingested;
  this skill only adds rows — it never marks anything `compiled`.
- For a single file, or when you want the per-file people-mapping done at
  registration time, use `/kb-add` instead.
