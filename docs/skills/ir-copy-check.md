# ir-copy-check

Investor-relations copy check. When a brand is part of a public company's group, its outward-facing marketing content is attributable to that company, and content that misstates a figure or undermines the investor narrative creates real financial and reputational risk. This plugin reviews and rewrites that content against **resource documents you supply** — messaging and IR guidance, and a filed Form 10-K — and cites your resources for every finding.

The plugin is organization-neutral: it ships the **method and the tooling, not the data**. You bring the messaging briefs, the IR guidance, and the filing; the plugin brings the workflow. Your material stays in your working directory and is kept out of git.

## Two skills, two kinds of evidence

They are kept deliberately separate so every finding rests on one identifiable kind of evidence and you always know which kind you are looking at.

- **`/critique-messaging`** — works from your messaging strategy and IR guidance. Covers the tactical, strategic questions: which framings undermine the investor story, which topics are no-gos, how the brand's authentic voice and the parent's narrative can both be served. The specific rules it enforces come from your resources (chiefly a "messaging tensions" document and the latest IR guidance).
- **`/critique-vs-10k`** — works only from a company's filed Form 10-K, distilled into a corpus you supply. Answers one question definitively: is this content consistent with what the company told the SEC? Every finding quotes filed language and cites its Item. Where the filing is silent, it says so rather than guessing.

Running both gives you overlapping but non-identical coverage.

## Prerequisites

- **Your resource documents** under `./resources/` in a working directory (see **Setup**). Fill-in templates ship at `templates/messaging/` and `templates/filing/`.
- **python3** (3.8+), only if you want the extractor to section a filing. Standard library only — no pip, no network.
- **Optional: a 10-K filing** in `./resources/`, for `/critique-vs-10k` to quote exact language. Not shipped — a filing is a large document and is instance data. Download it from the issuer's investor-relations page or SEC EDGAR.
- Web browsing, for critiquing content by URL.

## Install

```
/plugin marketplace add ljainschigg/generic-marketplace-2
/plugin install ir-copy-check@claude-plugins
```

## Setup

Run once after install, from the working directory where your resources live:

```
/setup
```

It confirms your resources are present, ensures `resources/` and `extract/` are gitignored, checks python3, runs the corpus freshness guard, and (if you have supplied a filing) extracts a sectioned copy under `./extract/`. It reports what is in place and stops with specific guidance at the first thing missing. The plugin ships **templates, not data** — setup will offer to copy a template scaffold you then fill with your own material.

## Use

```
/critique-messaging <URL, file path, or pasted content>
/critique-vs-10k    <URL, file path, or pasted content>
```

Each returns:

1. A summary of what the asset is and who it addresses
2. What holds up, with the support that backs it
3. Findings rated **CRITICAL** or **ADVISORY**, each with replacement wording (for `/critique-vs-10k`, each quotes the filing and cites its Item)
4. Anything outside the skill's scope, stated as such
5. A verdict

Ask for a rewrite and the skill returns the corrected asset in full after the findings, with a changelog. Rewrites follow the house tone and formatting rules in your `writing-rules.md`.

For `/critique-vs-10k` the severity split is mechanical: **CRITICAL** means the filing contradicts the content and there is filed language quoted to prove it; **ADVISORY** means the filing does not support the content, a qualifier has been dropped, the vocabulary is superseded, or the framing sits awkwardly against the filed structure. Absence of support is never inflated into contradiction.

## You supply the resources

Nothing about any specific company is baked into the plugin. You keep your resources in your own working directory (and out of git). The templates under `templates/` describe the shape of each resource file; fill them with your own messaging strategy, IR guidance, and distilled filing.

**Messaging resources** (`/critique-messaging`): `ir-guidance.md`, `investor-narrative.md`, `product-messaging.md`, `messaging-tensions.md`, `approved-boilerplate.md`, `authentic-voice.md`, and optionally `strategic-context.md` and `transition-notes.md`.

**Filing corpus** (`/critique-vs-10k`): `00-filing-map.md`, `01-official-self-description.md`, `02-defined-terms.md`, `03-citable-metrics.md`, `04-risk-factor-constraints.md`, `05-disclosure-rules.md`, `writing-rules.md`, and `corpus-meta.conf` (the freshness guard).

## How the filing extractor works

A filed 10-K is not readable in one pass. A large filer's annual report can run to tens of megabytes as a Word document, and often a majority of that is appended exhibit documents — purchase agreements, escrow and credit agreements, SOX certifications — that follow the signature page and are not 10-K disclosure at all.

So `skills/critique-vs-10k/scripts/extract_10k.py` handles the mechanical problem: it extracts text from the filing (detecting Word/OOXML, HTML, or plain text by content, not extension), splits the body from the exhibits at the signature page, sections the body on its `ITEM n.` headings, and writes one file per section with an index. That output is the audit trail — it lets a critique quote the filing exactly, and it makes the plugin re-runnable against next year's filing.

## Keeping the corpus current — the drop-dead date

A 10-K is annual, so a corpus derived from it is a snapshot of one fiscal year. A superseded figure cited as current is this plugin's worst failure mode, and it fails silently — the output looks authoritative precisely because every finding carries a citation.

So the corpus carries a **hard drop-dead date** in `corpus-meta.conf`, enforced by `skills/critique-vs-10k/scripts/corpus_status.sh`, which runs before any critique. Past that date `/critique-vs-10k` refuses to produce a critique unless you explicitly override for a deliberate historical check, and any overridden output is stamped as based on an expired corpus and unfit for clearing content. Choose the drop-dead date deliberately: the earliest date by which a material later filing (the next 10-Q or 10-K) or a stated corporate milestone supersedes the corpus.

To refresh: download the newer filing into `./resources/`, re-run the extractor, revise `./resources/0*.md`, and update the dates in `corpus-meta.conf`.

## Details

| | |
|---|---|
| **Version** | 1.0.0 |
| **Type** | skill |
| **Skills** | `setup`, `critique-messaging`, `critique-vs-10k` |
| **Data** | you supply it, in your working directory (kept out of git) |
