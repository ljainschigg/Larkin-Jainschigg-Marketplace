# karpathy-kb

Sets up and maintains a citation-tracked local knowledge base using the Karpathy-loop workflow. Compile raw sources — transcripts, Slack exports, presentation decks, design docs — into a structured wiki where every factual claim carries full provenance: who said it, in what document, on what date. Query it with full attribution, review conflicts, elicit missing tacit knowledge, and keep it structurally clean.

The core invariant: the wiki records what people believe, not settled truth. Conflicts between sources are surfaced, not resolved.

Works as an Obsidian vault out of the box.

## Prerequisites

- **Python 3.8+** — used by the deterministic vault scaffolder (`/kb-setup`), the mechanical linter (`/kb-lint`), and bulk source registration (`/kb-ingest`). Run `/setup` once after installing to verify it. Everything else is prompt-driven; if Python is absent, each falls back to a manual equivalent.

## Install

```
/plugin install karpathy-kb@lj-marketplace
```

Then verify the runtime once:

```
/setup
```

## Quickstart

**Set up a new knowledge base:**
```
/kb-setup ~/my-project-kb
```

The skill asks what topics to track, then runs a **deterministic scaffolder** that emits the full directory structure, `CLAUDE.md`, index files, and templates — the exact skeleton the other skills depend on. (Falls back to prompt-driven scaffolding if Python isn't available.)

**Add a source and compile it:**
```
# Drop a file into raw/transcripts/, raw/slack/, raw/decks/, or raw/misc/
# Fill in the frontmatter (use the TEMPLATE file as a guide)
# Then from the KB root directory:
/kb-add raw/transcripts/my-source.md      # one file
# or, after dropping several files in at once:
/kb-ingest                                # bulk-register everything new
/kb-compile
```

**Query the wiki:**
```
/kb-query What is the current plan for the inference layer?
```

**Check coverage before a big question, or review conflicts:**
```
/kb-coverage-check      # is there enough compiled, cited coverage to answer well?
/kb-conflict-review     # read-only triage of open conflicts
```

**Capture tacit knowledge that isn't written down anywhere:**
```
/kb-elicit
```

**Lint for structural problems; archive a topic area on a major version change:**
```
/kb-lint
/kb-archive
```

All skills run from the KB root directory — the one containing `CLAUDE.md`.

## How it works

Raw source documents live in `raw/` and are never modified. `/kb-compile` reads uncompiled sources, extracts factual claims with full provenance (`[Person, source-id, date]`), and writes them incrementally into wiki articles. Conflicts between sources are flagged with `> [!conflict]` callouts and logged in `wiki/_conflicts.md` for human review. When a newer source declares `supersedes:`, the compile marks the old claim `> [!superseded]` (kept for history) and adds the new one — supersession is handled distinctly from conflict.

`/kb-query` answers questions using only compiled wiki content — no speculation. Every claim carries its citation, and the answer is rated High / Medium / Low confidence. `/kb-coverage-check` assesses, before answering, whether the KB has enough to answer well.

`/kb-lint` runs structural checks (broken links, missing citations, index drift, orphaned source references, supersession integrity) via a bundled Python script with deterministic auto-fix, falling back to a manual pass if Python isn't present.

## Keeping it current

- **`/kb-elicit`** — when coverage is thin and the missing knowledge is tacit, run a structured interview that captures it as a cited raw source and compiles it in.
- **`discourse-tracker`** (separate plugin) — maintains `~/.claude/shared-context/current-discourse.md` with a weekly shallow scan of frontier labs, practitioners, and community signal. Add relevant entries to `raw/misc/` as `external-article` sources to compile them with proper attribution.

## Details

| | |
|---|---|
| **Version** | 1.3.5 |
| **Type** | skill |
| **Maintained by** | Claude Plugins Marketplace |
| **Prerequisite** | Python 3.8+ (for `/kb-setup`, `/kb-lint`, `/kb-ingest`; run `/setup` to verify) |
| **Format** | Obsidian-compatible Markdown vault |
