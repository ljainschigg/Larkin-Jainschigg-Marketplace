# karpathy-kb

Sets up and maintains a citation-tracked local knowledge base using the Karpathy-loop workflow. Compile raw sources — transcripts, Slack exports, presentation decks, design docs — into a structured wiki where every factual claim carries full provenance: who said it, in what document, on what date. Query it with full attribution, review conflicts, elicit missing tacit knowledge, and keep it structurally clean.

The core invariant: the wiki records what people *believe*, not settled truth. Conflicts between sources are surfaced, not resolved. Works as an Obsidian vault out of the box.

---

## Prerequisites

- **Python 3.8+** — used by the deterministic vault scaffolder (`/kb-setup`), the mechanical linter (`/kb-lint`), and bulk source registration (`/kb-ingest`). Run `/setup` once after installing to verify. Everything else is prompt-driven; if Python is absent, each falls back to a manual equivalent.

---

## Install

If you haven't added the marketplace yet:

```
/plugin marketplace add ljainschigg/Larkin-Jainschigg-Marketplace
```

Then install the plugin and verify the runtime:

```
/plugin install karpathy-kb@claude-plugins
/setup
```

---

## Quickstart

```
/kb-setup ~/my-project-kb          # scaffold a new vault (structure, CLAUDE.md, indexes, templates)
# drop sources into raw/…, fill frontmatter, then from the KB root:
/kb-add raw/transcripts/my-source.md
/kb-compile
/kb-query What is the current plan for the inference layer?
```

All skills run from the KB root directory — the one containing `CLAUDE.md`.

---

## Skills

| Skill | Purpose |
|---|---|
| `/setup` | One-time preflight — verify Python 3.8+ is available |
| `/kb-setup` | Scaffold a new KB vault deterministically (structure, `CLAUDE.md`, indexes, templates) |
| `/kb-add` | Register a single raw source file so it will be compiled |
| `/kb-ingest` | Bulk-register every new raw file at once (batch `/kb-add`) |
| `/kb-compile` | Extract claims with provenance into wiki articles; handle supersession |
| `/kb-query` | Answer a question from compiled content, with citations + confidence rating |
| `/kb-coverage-check` | Assess whether the KB can answer a question well *before* answering |
| `/kb-conflict-review` | Read-only triage of open conflicts, with suggested human actions |
| `/kb-elicit` | Structured interview to capture tacit knowledge as a cited source |
| `/kb-lint` | Structural checks + auto-fix (broken links, citations, index drift, supersession) |
| `/kb-archive` | Archive a topic area's articles on a major version transition |

---

## How it works

Raw sources in `raw/` are never modified. `/kb-compile` extracts claims with full provenance (`[Person, source-id, date]`) into wiki articles. Conflicts are flagged with `> [!conflict]` callouts and logged in `wiki/_conflicts.md`. When a newer source declares `supersedes:`, the compile marks the old claim `> [!superseded]` (kept for history) and adds the new one — supersession is handled distinctly from conflict.

`/kb-query` answers using only compiled content, every claim cited and the answer rated High / Medium / Low confidence; `/kb-coverage-check` assesses sufficiency first. `/kb-lint` runs its checks via a bundled Python script with deterministic auto-fix, falling back to a manual pass when Python isn't present.

---

## Keeping it current

- **`/kb-elicit`** captures tacit knowledge that isn't written down anywhere, as a cited raw source, and compiles it in.
- The [discourse-tracker](discourse-tracker.md) plugin can feed external signal into `raw/misc/` as `external-article` sources for provenance-tracked compilation.

---

## Details

| | |
|---|---|
| **Version** | 1.3.4 |
| **Type** | skill |
| **Maintained by** | Claude Plugins Marketplace |
| **Prerequisite** | Python 3.8+ (for `/kb-setup`, `/kb-lint`, `/kb-ingest`; run `/setup` to verify) |
| **Format** | Obsidian-compatible Markdown vault |
