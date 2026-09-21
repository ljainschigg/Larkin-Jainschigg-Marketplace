---
description: "Check a documentation site for broken links and get a report of what needs fixing."
---

# linkcheck

Scans a versioned MkDocs documentation site for broken links and saves a full report. Discovers all published versions via `versions.json`, enumerates pages from the navigation sidebar, checks every content link once (cached across versions), and reports broken links grouped by version with anchor text and the pages that reference them.

---

## Prerequisites

- [`uv`](https://docs.astral.sh/uv/) on your PATH. The skill runs a bundled Python script via `uv run`, which installs the script's dependencies automatically (declared inline, PEP 723). `/linkcheck` checks for `uv` before it starts.

---

## Install

If you haven't added the marketplace yet:

```
/plugin marketplace add ljainschigg/Larkin-Jainschigg-Marketplace
```

Then install the plugin:

```
/plugin install linkcheck@Larkin-Jainschigg-Marketplace
```

---

## Use

```
/linkcheck
```

Claude walks you through the scan interactively:

1. **Which site** — a site URL, or an entry from an optional saved list
2. **Ignore prefixes** — private GitHub repos, staging hosts, and the like (localhost is always ignored)
3. **Versions** — all published versions, or specific version strings
4. **Output filename** — defaults to `<site-slug>-YYYY-MM-DD.txt`

It then runs the scan with live progress, saves the full report to your chosen file, and summarises broken links by version with suggested next steps. A full multi-version scan of a large site typically takes 5–15 minutes.

---

## Details

| | |
|---|---|
| **Version** | 1.0.6 |
| **Type** | skill |
| **Maintained by** | Claude Plugins Marketplace |
| **Runtime** | Python via `uv` (dependencies declared inline in `linkcheck.py`) |
