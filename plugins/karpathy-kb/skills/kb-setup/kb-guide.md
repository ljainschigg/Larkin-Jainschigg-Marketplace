# Karpathy-loop knowledge base — operating manual

This file is the authoritative guide for all Claude operations in this knowledge base.
Read it fully before taking any action. It is written into every new KB by `kb-setup`
and adapted with the KB's specific product areas and topics.

---

## How the loop works

1. Raw source documents land in `raw/` — they are **never modified**.
2. Claude compiles those sources into wiki articles under `wiki/`.
3. Claude maintains index files and a source registry for navigation.
4. Q&A queries run against the wiki; outputs are filed in `qa/`.
5. Periodic lint passes clean up stale links, missing citations, and inconsistencies.

**Core invariant:** every factual claim in the wiki must carry a citation to the raw
source that asserts it, including the name of the person who asserted it and the
date/context. The wiki records what people believe, not settled truth. Do not resolve
conflicts — surface them.

---

## Directory map

| Path | Purpose |
|------|---------|
| `raw/` | Immutable source documents — never edit |
| `raw/_registry.md` | Index of all raw sources |
| `wiki/` | Compiled knowledge articles |
| `wiki/_index.md` | Master navigation index |
| `wiki/_sources.md` | Aggregated source inventory |
| `wiki/_conflicts.md` | Log of contradictory claims |
| `wiki/cross-cutting/` | Topics spanning multiple areas |
| `qa/` | Q&A session outputs |

---

## Provenance rules

Every factual statement in a wiki article must follow this pattern:

> [Claim text] `[PERSON, SOURCE-ID, DATE]`

- **PERSON** — the individual who stated or wrote this. If no individual author, use the org or team name.
- **SOURCE-ID** — the filename stem of the raw source (e.g., `2024-11-15_transcript_roadmap-sync`).
- **DATE** — the date from the raw source frontmatter.

Example:
> The inference layer will support multi-modal inputs by Q2 2025.
> `[First Speaker, 2024-11-15_transcript_roadmap-sync, 2024-11-15]`

For claims stated by multiple people in agreement:
> `[First Speaker + Second Speaker, 2024-11-15_transcript_roadmap-sync, 2024-11-15]`

**Never strip citations. Never paraphrase away the attribution.**

---

## Conflict handling

When two sources make contradictory claims about the same subject:

1. Present both claims in the wiki article, each with its own citation.
2. Mark the section with the `> [!conflict]` callout.
3. Add an entry to `wiki/_conflicts.md` — do not silently pick a winner.
4. Do not editorialize about which claim is correct.

```
> [!conflict]
> **Conflicting claims about [topic]:**
> - [Claim A] `[Person A, source-id-A, date-A]`
> - [Claim B] `[Person B, source-id-B, date-B]`
> See [[wiki/_conflicts#conflict-slug]] for triage status.
```

---

## Supersession handling

Supersession is **not** a conflict. A conflict is two sources disagreeing; a
supersession is a newer source deliberately replacing an older claim (a plan
changed, a spec was revised, a name was retired).

A raw source declares what it replaces via a `supersedes:` list in its
frontmatter (source-ids of the claims/sources it overrides). When compiling a
source with a non-empty `supersedes:`, **before** extracting its new claims:

1. Find the affected claim(s) in the wiki.
2. Mark each old claim with the `> [!superseded]` callout — keep it for history,
   do not delete it. Note what supersedes it and when.
3. Add the new claim immediately below, with its own citation.
4. Add the superseding source-id to the article's `superseded_sources`
   frontmatter list.

```
> [!superseded]
> ~~[Old claim] `[Person, old-source-id, old-date]`~~
> Superseded by [New claim] `[Person, new-source-id, new-date]`.
```

`/kb-lint` checks supersession integrity: a superseded claim whose replacement
isn't marked is reported for manual follow-up.

---

## Processing source types

### Transcripts (`raw/transcripts/`)

Frontmatter fields: `date`, `participants`, `meeting_type`, `topics`.

1. Identify every distinct claim or decision made.
2. Attribute each to the speaker by name from the participant list.
3. Note whether it is a statement of fact, an opinion, a decision, or an action item. Only facts and decisions flow into wiki articles.
4. Treat "we will" / "the plan is" statements as **intent claims**, not settled facts. Flag with `(stated intent)` in the citation.
5. Cross-reference against existing wiki articles.

### Slack exports (`raw/slack/`)

Frontmatter fields: `channel`, `date_range`, `participants`, `topics`.

1. Reconstruct threaded conversations where possible.
2. Treat each substantive message as a separate claimable unit.
3. Attribute by Slack handle; map to real names via `wiki/cross-cutting/org-and-people.md`. If no mapping exists, use `[@handle — real name unknown]`.
4. Slack messages are informal and often speculative — prefer "suggested" or "asked" over asserted facts unless context is clear.

### Presentation decks (`raw/decks/`)

Frontmatter fields: `date`, `author`, `audience`, `event`, `topics`.

1. Decks are extracted to text; slide boundaries are marked `--- SLIDE N ---`.
2. Slide content is the author's official prepared position at time of presentation.
3. Claims from decks carry higher weight than casual Slack messages.
4. Speaker notes (following a `NOTES:` marker) may modify the on-slide claim — always check them.

### Miscellaneous (`raw/misc/`)

Frontmatter fields: `date`, `author`, `doc_type`, `topics`.

Weight by `doc_type`:
- `engineering-spec` or `design-doc` — treat as authoritative for the date
- `blog-post` — treat as marketing position
- `email` — treat like Slack (informal, attributed)
- `external-article` or `external-blog` — treat as external signal, note the source org
- `other` — note in citation

---

## Compile workflow

### Step 1 — Discover new sources
Read `raw/_registry.md`. Identify all entries where `compiled: false`. If none, report and stop.

### Step 2 — Read and parse each new source
For each uncompiled source:
- Read frontmatter: type, date, participants/author, topics.
- Extract all factual claims, decisions, and intent statements per source-type rules.
- Build a working list: `[claim, person, source-id, date, topic-tags]`.

### Step 3 — Update wiki articles incrementally
Do NOT rewrite articles from scratch.
- Open the relevant article(s) for each claim.
- If the claim is new, add it with citation.
- If the claim updates an existing claim from the same person/source, update in place and note the newer source.
- If the claim contradicts an existing claim, invoke the conflict protocol.
- Create new articles or sections as needed, following the article template.

### Step 4 — Update index files
After editing wiki articles:
- Update the relevant topic `wiki/[area]/_index.md`.
- Update `wiki/_index.md` if new articles were created.
- Update `wiki/_sources.md`.

### Step 5 — Mark sources as compiled
Update `raw/_registry.md`: set `compiled: true` and `compiled_date: [today]`.

### Step 6 — Report
Sources processed, articles created vs. updated, conflicts flagged.

---

## Query workflow

1. Read `wiki/_index.md` to identify relevant articles.
2. Read only the relevant articles.
3. Synthesize an answer that:
   - Preserves provenance (`[Person, source-id, date]` for every claim).
   - Flags open conflicts from `wiki/_conflicts.md` that bear on the answer.
   - Rates confidence: High (multiple independent sources, at least one formal) / Medium (one formal source, or multiple informal agreeing) / Low (single informal source).
4. Save to `qa/[YYYY-MM-DD]_[short-slug].md` using the Q&A template.
5. Add the new file to `qa/_index.md`.
6. Do NOT modify wiki articles during a query run.

---

## Lint workflow

Check for and fix:
1. **Broken wikilinks** — replace with `[[MISSING: path]]` and log.
2. **Citations without source files** — source-id not in `raw/_registry.md`; flag in `wiki/_conflicts.md`.
3. **Articles without citations** — mark with `> [!uncited]` if not already present.
4. **Stale cross-references** — links to deleted or renamed articles.
5. **`_index.md` drift** — articles on disk not listed in the nearest `_index.md`; add them.
6. **Resolved conflicts** — if a `_conflicts.md` entry has `resolved:` in frontmatter, move it to `## Resolved`.

Do NOT make substantive edits to article content during a lint pass.

---

## Formatting conventions

**Wikilinks**: `[[path/to/article]]` or `[[path/to/article|Display Text]]`. Paths relative to vault root.

**Headings**: `#` title only, `##` major sections, `###` subsections. Never skip levels.

**Citation inline format**: `` `[Person Name, source-id, YYYY-MM-DD]` `` — at end of sentence, in backtick code span.

**Callout blocks**:
```
> [!conflict]    — conflicting claims
> [!uncited]     — needs citation
> [!intent]      — stated intent, not confirmed fact
> [!stale]       — source older than 6 months, may be outdated
> [!superseded]  — claim replaced by a newer source (kept for history)
```

**Article frontmatter**:
```yaml
---
title: "Article Title"
area: [topic area]
tags: []
version: ""
last_compiled: YYYY-MM-DD
sources_used: []
superseded_sources: []
---
```

---

## People and identity

`wiki/cross-cutting/org-and-people.md` is the identity authority. It maps full names to handles, affiliations, and roles.

When you encounter a new name or handle in any source, check if they are listed. If not, add them with whatever information is available. Use `[role unknown]` and `[team unknown]` as placeholders. All citations must use the canonical full name from this file.

---

## What you must never do

- Never edit files in `raw/`.
- Never remove a citation from a wiki article.
- Never silently resolve a conflict.
- Never assert a claim as settled fact if it came from a single informal source.
- Never create a wiki article without frontmatter.
- Never run a query that modifies wiki content.
