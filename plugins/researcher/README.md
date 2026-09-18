# researcher

A Claude Code plugin for web research. Discovers and retrieves sources on any topic — including PDFs behind marketing lead-gen gates — and synthesizes findings into clean, readable output.

- Helps you choose the right research mode (broad exploration, directed evidence-gathering, or community opinion)
- Generates search phrases and discovers 12–15 candidate sources
- Fetches web pages using both direct HTTP and browser automation (for JavaScript-heavy sites)
- Retrieves PDFs from gated landing pages by filling contact forms using your credentials
- Extracts text from PDFs, including OCR for image-only documents
- Saves everything locally and writes a synthesis summary

## Prerequisites

- **Node.js 20 or higher** (current LTS) and **npm** — [nodejs.org](https://nodejs.org). The Playwright MCP server requires Node ≥20; Node 18 is end-of-life.
- **A 20+ Node must be first on your `$PATH`.** The MCP servers launch via bare `npx`, which resolves `node` through `$PATH`. If you have Node 20+ installed elsewhere (nvm, `~/.local/`, Homebrew) but `node --version` still shows an older one, put the newer one ahead on your `$PATH` — otherwise Playwright fails its version check and the connection closes.
- That's it. Playwright and PDF dependencies are installed automatically by `/setup`.

## Install

If you haven't added the marketplace yet:

```
/plugin marketplace add ljainschigg/Larkin-Jainschigg-Marketplace
```

Then install the plugin:

```
/plugin install researcher@claude-plugins
```

After installing, run setup:

```
/setup
```

This installs the Chromium browser binary, creates a credentials file at `$CLAUDE_PLUGIN_DATA/.env`, and verifies both MCP servers are running. Fill in the credentials file with your work contact details — they are used to fill forms on gated research landing pages.

## Use

Start a research project:

```
/research
```

Claude will ask what kind of research you need and guide you through the rest. Or pass a topic directly:

```
/research quantum computing fundamentals
```

Fetch a single PDF (direct link or gated landing page):

```
/fetch-pdf https://example.com/whitepaper-landing-page
```

Research output is saved to your **project directory** — the path you pass to `/research`, or the current directory if you don't pass one (a calling plugin such as `seo-claude-plugin` sets it automatically). Retrieved sources land in `<project-dir>/resources/`, alongside `candidate-links.md`, `search-phrases.md`, and the final `research-summary.md` at the project root.

## How it works

`/research` runs a seven-phase pipeline: mode selection, search phrase generation, source discovery (via WebSearch), web page retrieval (WebFetch with Playwright fallback for JS-heavy sites), PDF retrieval (Playwright browser automation to fill forms on gated landing pages), and synthesis. Two MCP servers power the heavy lifting: `playwright` handles all browser automation, and `extract-pdf` downloads PDFs and extracts their text using pdf-parse with a tesseract.js OCR fallback for image-only documents.

## Details

| | |
|---|---|
| **Version** | 1.1.9 |
| **Runtime** | Node.js via `npm` |
| **MCP servers** | `playwright` (npx), `extract-pdf` (bundled Node.js server) |
| **Maintained by** | Claude Plugins Marketplace |
