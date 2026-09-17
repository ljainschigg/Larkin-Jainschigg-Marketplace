---
name: setup
description: One-time setup for ir-copy-check. Verifies the resource documents each critique skill needs are present in the working directory, keeps them out of git, checks python3, and (if a 10-K filing is supplied) extracts a sectioned copy of it. Run this after installing the plugin.
---

Set up `ir-copy-check` in the user's working directory. This plugin ships **no company data** — every fact it uses comes from resource documents the user supplies. Setup's job is to confirm those resources are present, protected, and (for the filing) processed. Work through the steps in order; report clearly on what is found, what is missing, and what to do about it.

## What this plugin needs

The plugin has two critique skills, each with its own resource set. Set up whichever you plan to use (or both). Fill-in templates ship at `${CLAUDE_PLUGIN_ROOT}/templates/` — `templates/messaging/` and `templates/filing/`.

**`/critique-messaging`** reads messaging and IR resources from `./resources/` (a `./resources/messaging/` subdirectory is also fine):

| File (role) | Purpose |
|---|---|
| `ir-guidance.md` | Most authoritative direct guidance from the IR function |
| `investor-narrative.md` | The parent/investor narrative, framework, metrics, constraints |
| `product-messaging.md` | The brand's product and positioning messaging |
| `messaging-tensions.md` | Fault lines and absolute no-gos |
| `approved-boilerplate.md` | Approved messaging frameworks |
| `authentic-voice.md` | The brand's desired voice (ground truth, not critiqued) |
| `strategic-context.md` | Optional — strategic-intent theories |
| `transition-notes.md` | Optional — open questions during an org change |

**`/critique-vs-10k`** reads a distilled 10-K corpus from `./resources/`:

| File | Purpose |
|---|---|
| `00-filing-map.md` | Which filing is authority; fiscal-year convention; how to cite |
| `01-official-self-description.md` | The company's filed self-description |
| `02-defined-terms.md` | The filed glossary; non-GAAP rules; units |
| `03-citable-metrics.md` | Every citable figure with its period; the contracts |
| `04-risk-factor-constraints.md` | Risk disclosures and the claims they cap |
| `05-disclosure-rules.md` | Safe harbor, Reg FD, superseded material, scope boundary |
| `corpus-meta.conf` | Freshness guard: `FISCAL_YEAR_END`, `DROP_DEAD`, optional `SNAPSHOT_NOTE` |
| `writing-rules.md` | House tone and formatting rules (governs rewrites) |

## Step 1 — Keep resources out of git

This plugin's resources are the user's own confidential material (messaging strategy, IR guidance, distilled filings). The working directory may be a git repo. Ensure a `./.gitignore` covers `resources/` and `extract/` (create it or append the lines). This material must **never** be committed or pushed. This is a hard requirement, not a convenience.

## Step 2 — Check what resources are present

Report a table of what exists, using the Bash tool to confirm and show modification dates:

```bash
ls -lh ./resources/ ./resources/messaging/ 2>&1
```

For each skill the user wants, list which of its files are present and which are missing. If `./resources/` is empty or missing:
- Explain that the plugin ships **templates, not data**, at `${CLAUDE_PLUGIN_ROOT}/templates/`.
- Offer to copy the relevant template set as a starting scaffold, for example:
  ```bash
  mkdir -p ./resources
  cp -n "${CLAUDE_PLUGIN_ROOT}/templates/messaging/." ./resources/   # for critique-messaging
  cp -n "${CLAUDE_PLUGIN_ROOT}/templates/filing/." ./resources/       # for critique-vs-10k
  ```
- Make clear the templates are empty scaffolds the user must fill with their own material before any critique will be meaningful.

`cp -n` never overwrites a file the user has already edited.

## Step 3 — Filing-corpus freshness (if using `/critique-vs-10k`)

If the filing corpus is present, run the freshness guard:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/critique-vs-10k/scripts/corpus_status.sh"
```

- **EXPIRED**: show the output verbatim; tell the user `/critique-vs-10k` will refuse to produce a critique until the corpus is refreshed (this is deliberate). Setup may still complete.
- **UNKNOWN**: no `corpus-meta.conf` is configured. Tell the user to create it (the script explains the keys) so staleness can be detected.
- **CURRENT**: note the days remaining and any `SNAPSHOT_NOTE`.

## Step 4 — Check python3 (only if you will extract a filing)

```bash
python3 --version 2>&1
```

The extractor is a stdlib-only Python script — python3 (3.8+) and nothing else, no pip, no network. If it is missing and the user wants to process a filing, tell them to install Python 3 and re-run.

## Step 5 — Locate and extract the filing (optional)

The plugin does not ship any filing — a 10-K is a large document and is instance data. If the user has supplied one under `./resources/`, extract a sectioned copy:

```bash
ls -lh ./resources/*.rtf ./resources/*.docx ./resources/*.htm ./resources/*.html ./resources/*.txt 2>/dev/null
python3 "${CLAUDE_PLUGIN_ROOT}/skills/critique-vs-10k/scripts/extract_10k.py" ./resources/<filing> -o ./extract
```

The script detects the format by content, not extension (a `.docx` misnamed `.rtf` is handled). It splits the 10-K body from the appended exhibits, sections the body on `ITEM n.` headings into `extract/body/`, and writes an index at `extract/00-INDEX.md`. Show the user the section map; confirm every `ITEM` from 1 through 15 is listed. If it reports no `ITEM n.` headings, the file is probably not a 10-K — have the user check the download, and try `--list` to inspect without writing.

This is a **warning, not a blocker** — `/critique-vs-10k` works from the corpus alone; the filing lets it quote exact language.

## Step 6 — Confirm

Report a table of what is in place:

| Check | Status |
|---|---|
| Resources gitignored | ✅ / ❌ |
| Messaging resources | ✅ N present / ⚠️ not set up |
| Filing corpus | ✅ present / ⚠️ not set up |
| Corpus freshness | ✅ Current / 🚫 EXPIRED / ❔ Unknown / — n/a |
| python3 | ✅ 3.x.x / — not needed |
| Sectioned extract | ✅ N sections / ⚠️ Skipped |

Then tell the user how to use it:

```
/critique-messaging <URL, file path, or pasted content>
/critique-vs-10k    <URL, file path, or pasted content>
```

Each returns a structured critique. For `/critique-vs-10k`, every finding is cited to an Item of the filing. Ask either skill to rewrite and it returns the corrected asset as well.

## Freshness — say this out loud at the end

If the user set up the filing corpus, remind them plainly:

1. **A 10-K is annual — the corpus is a snapshot** of one fiscal year.
2. **It carries a hard drop-dead date** (in `corpus-meta.conf`). Past it, `/critique-vs-10k` refuses to produce a critique unless explicitly overridden — the corpus goes stale silently, and its figures stay confidently quotable long after they stop being current.
3. **Refreshing it** means downloading the newer filing, re-running the extractor, revising `./resources/0*.md`, and updating `DROP_DEAD`/`FISCAL_YEAR_END` in `corpus-meta.conf`.

And, for both skills: resource documents should be refreshed whenever the IR function issues new guidance or the company's disclosures change.
