---
name: kb-add
description: Registers a new raw source file in the knowledge base registry and validates its frontmatter.
---

This skill runs from the knowledge base root directory (where `CLAUDE.md` lives).

Read `./CLAUDE.md` fully before taking any action. It contains all processing rules for this knowledge base.

## What this skill does

It validates and registers a new raw source file that has been dropped into one of the `raw/` subdirectories. It does not compile the source — that is `/kb-compile`.

For registering **many** files at once, use `/kb-ingest` instead — it bulk-scans and registers every unregistered file in one pass.

## Input

The user should provide the path to the new file (e.g. `raw/transcripts/2024-11-15_transcript_roadmap-sync.md`). If no path was provided, list all files in `raw/` subdirectories that are not yet in `raw/_registry.md` and ask the user which one to register.

## Steps

1. Read the file's frontmatter and extract: `source_id`, `type`, `date`, `topics`, and any participant/author fields.

2. Validate the frontmatter:
   - `source_id` must follow the pattern `YYYY-MM-DD_[type]_[slug]`
   - `type` must be one of: `transcript`, `slack`, `deck`, `misc`
   - `topics` must be a non-empty list
   - `compiled` must be `false`
   - Report any missing or malformed fields and stop if validation fails

3. Add a row to `raw/_registry.md`:
   ```
   | [source_id] | [path] | [type] | [date] | [topics joined with comma] | false | |
   ```

4. Check `wiki/cross-cutting/org-and-people.md` for any participants or authors listed in the source. Add any unknown names or handles with `[role unknown]` and `[team unknown]` placeholders, noting the source id.

5. Confirm successful registration and remind the user to run `/kb-compile` when ready to ingest this source.
