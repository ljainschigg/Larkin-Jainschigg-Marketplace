---
name: kb-setup
description: Scaffolds a new Karpathy-loop knowledge base at a specified path, customized for the user's topics and products.
---

Read `${CLAUDE_PLUGIN_ROOT}/skills/kb-setup/kb-guide.md` fully before proceeding. That file is the operating manual for the system you are about to create.

## What this skill does

It creates a complete, ready-to-use Karpathy-loop knowledge base — all directories, index files, templates, and a customized `CLAUDE.md` — at a path the user specifies.

## Step 1 — Gather information

Ask the user:
1. Where to create the KB (full path, e.g. `~/my-project-kb`)
2. What this KB is for — a brief description (e.g. "product knowledge base for Acme's three APIs")
3. What topic areas or products to track (e.g. "auth-service, billing-service, notifications")
4. Their name or team name (for the initial `org-and-people.md` entry)

If the user provided these as arguments, use them directly.

## Step 2 — Scaffold the vault (deterministic)

Run the bundled scaffolder. It emits the exact skeleton the other skills depend on — `raw/` subdirs, `raw/_registry.md` with the correct columns, the index/conflict/source files, every source + article template, a `CLAUDE.md` generated from the operating manual with this KB's name, description, and topic-area map, and a `.gitignore` (a KB is often deliberately versioned, so nothing is ignored by default — but it flags `raw/` and `qa/`, which hold sensitive sources and queries, for the user to decide about before committing):

```
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/create-vault.py" "<path>" \
  --name "<KB name>" \
  --description "<one-line description>" \
  --topics "<area1, area2, area3>" \
  --owner "<user or team name>"
```

- Pass the Step 1 topic areas as a comma-separated `--topics` list; each becomes a `wiki/<slug>/` directory (plus `cross-cutting/`).
- The script refuses to write into a non-empty directory — if it errors, confirm the path with the user.
- **If `python3` is not available**, use the **Fallback** manual scaffold below instead.

## Step 3 — Enrich (optional)

The generated `CLAUDE.md` already carries the full operating manual plus a header with the KB's name, description, and topic-area map. Tailor it only if the conversation surfaced specifics worth capturing — sharpen the purpose paragraph, or note domain conventions. Confirm the owner row in `wiki/cross-cutting/org-and-people.md` and add any other people already known.

## Step 4 — Report

Tell the user where the KB was created, which topic-area directories were set up, and the next commands: add sources with `/kb-add` (one file) or `/kb-ingest` (bulk), then `/kb-compile`.

---

## Fallback (no Python) — manual scaffold

Use this **only if `python3` is unavailable**. The scaffolder in Step 2 produces exactly this structure deterministically; these steps are the manual equivalent.

## Step 2 — Create the directory structure

Create the following directories at the specified path:
```
raw/
raw/transcripts/
raw/slack/
raw/decks/
raw/misc/
wiki/
wiki/cross-cutting/
wiki/[one subdirectory per topic area the user named]/
qa/
```

## Step 3 — Write CLAUDE.md

Write a `CLAUDE.md` at the KB root. Base it on `${CLAUDE_PLUGIN_ROOT}/skills/kb-setup/kb-guide.md` but adapt it:
- Replace the generic introduction with one specific to this KB's purpose
- Replace the directory map to list the user's actual topic area directories
- Keep all processing rules, workflows, and formatting conventions exactly as written in kb-guide.md — do not simplify or omit them

## Step 4 — Write index and registry files

Also write a **`.gitignore`** at the KB root: ignore OS/editor cruft, and add a commented block noting that `raw/` (transcripts, Slack exports, decks) and `qa/` may hold sensitive/personal data, so the user should decide deliberately what to commit (a KB is often deliberately versioned, so don't force-ignore them).

**`raw/_registry.md`**:
```markdown
---
title: "Raw Source Registry"
description: "Index of all raw source documents."
last_updated: ""
---

# Raw Source Registry

| id | path | type | date | topics | compiled | compiled_date |
|----|------|------|------|--------|----------|---------------|
```

**`wiki/_index.md`**:
```markdown
---
title: "Knowledge Base Index"
description: "[KB description]"
last_updated: ""
---

# [KB Name] — Knowledge Base

## Topic areas

[One line per topic area with link to its _index.md]

## Stats

- Sources compiled: 0
- Articles: 0
- Open conflicts: 0
```

**`wiki/_sources.md`**: Empty sources registry (header only).

**`wiki/_conflicts.md`**: Empty conflicts log (header only, `## Open` and `## Resolved` sections).

**`wiki/cross-cutting/_index.md`**: Index for cross-cutting articles.

**`wiki/cross-cutting/org-and-people.md`**: Identity authority file. Pre-populate with the user's name/team from Step 1.

**Per topic area**: Create `wiki/[area]/_index.md` with a header for that area.

**`qa/_index.md`**: Empty Q&A index.

## Step 5 — Write source templates

Write the following template files. They are examples only — the user fills them in for each real source.

**`raw/transcripts/TEMPLATE_transcript.md`**:
```markdown
---
source_id: "YYYY-MM-DD_transcript_[slug]"
type: transcript
date: "YYYY-MM-DD"
meeting_type: "[sync | review | interview | other]"
topics: []
participants:
  - "[Full Name] (@handle)"
compiled: false
compiled_date: ""
context: "[One sentence: what this meeting was about]"
---

[Paste transcript here]
```

**`raw/slack/TEMPLATE_slack.md`**:
```markdown
---
source_id: "YYYY-MM-DD_slack_[channel]-[slug]"
type: slack
channel: "#[channel-name]"
date_range: "YYYY-MM-DD to YYYY-MM-DD"
topics: []
participants:
  - "@handle"
compiled: false
compiled_date: ""
context: "[One sentence: what thread or topic this covers]"
---

[Paste Slack thread here, preserving timestamp and handle structure]
```

**`raw/decks/TEMPLATE_deck.md`**:
```markdown
---
source_id: "YYYY-MM-DD_deck_[slug]"
type: deck
date: "YYYY-MM-DD"
author: "[Full Name]"
audience: "[internal | customer | conference | other]"
event: "[Event or meeting name]"
topics: []
compiled: false
compiled_date: ""
context: "[One sentence: what this deck covered]"
---

--- SLIDE 1 ---
[Slide content]

NOTES:
[Speaker notes if available]

--- SLIDE 2 ---
[Continue...]
```

**`raw/misc/TEMPLATE_misc.md`**:
```markdown
---
source_id: "YYYY-MM-DD_misc_[slug]"
type: misc
doc_type: "[engineering-spec | design-doc | blog-post | email | external-article | other]"
date: "YYYY-MM-DD"
author: "[Full Name or Org]"
topics: []
compiled: false
compiled_date: ""
context: "[One sentence: what this document is]"
---

[Document content here]
```

**`wiki/TEMPLATE_article.md`**:
```markdown
---
title: "[Article Title]"
area: "[topic area]"
tags: []
last_compiled: ""
sources_used: []
---

# [Article Title]

> [!uncited]
> This article has no citations yet. Run a compile pass to populate it from raw sources.

## Summary

_(To be compiled from raw sources.)_

## Related

- [[wiki/cross-cutting/org-and-people|People]]
```

**`qa/TEMPLATE_qa.md`**:
```markdown
---
question: ""
date: "YYYY-MM-DD"
areas_consulted: []
confidence: "High | Medium | Low"
---

# Q&A: [Question]

_Date: YYYY-MM-DD_

## Answer

[Answer with provenance citations]

## Confidence

**[High | Medium | Low]** — [rationale]

## Sources consulted

[List of wiki articles and raw sources referenced]

## Open conflicts relevant to this answer

[Any conflicts from wiki/_conflicts.md that bear on this answer]
```

**`qa/_index.md`**:
```markdown
# Q&A Index

| Date | Question | Confidence | File |
|------|----------|------------|------|
```

## Step 6 — Write README.md

Write a `README.md` at the KB root explaining:
- What this KB is for
- How to add a source (drop file in raw/, run `/kb-add`)
- How to compile (`/kb-compile` from this directory)
- How to query (`/kb-query [question]` from this directory)
- How to lint (`/kb-lint` from this directory)

## Step 7 — Report

Tell the user:
- Where the KB was created
- What topic area directories were set up
- The exact commands to run next: add a source with `/kb-add`, then compile with `/kb-compile`
