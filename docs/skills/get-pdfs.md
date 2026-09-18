# get-pdfs

Downloads PDFs from gated lead-gen landing pages. Fills out access forms using your stored credentials, follows redirects and CDN hops, and saves files to `./resources/`. Also used internally by the `researcher` plugin for PDF retrieval.

---

## Prerequisites

- [Node.js and npm](https://nodejs.org/) (**20 or higher**, current LTS) — required by the Playwright MCP server (Node 18 is end-of-life). A 20+ Node must be first on your `$PATH`, since the server launches via bare `npx`.
- Run `/setup` after installing to download the Chromium browser and store your form-filling credentials

---

## Install

If you haven't added the marketplace yet:

```
/plugin marketplace add ljainschigg/Larkin-Jainschigg-Marketplace
```

Then install the plugin:

```
/plugin install get-pdfs@lj-marketplace
```

Run one-time setup:

```
/setup
```

---

## Skills

### `/get-pdfs`

Pass one or more landing page URLs. The skill works sequentially, fills each form, downloads the PDF to `./resources/`, and returns a status table.

```
/get-pdfs https://vendor.com/whitepaper https://analyst.io/report2025
```

### `/setup`

One-time setup: installs the Playwright Chromium browser and creates your credentials file at `$CLAUDE_PLUGIN_DATA/.env`.

```
/setup
```

---

## What it handles

| Scenario | Handling |
|---|---|
| Lead-gen contact form (inline) | Fills and submits |
| Lead-gen form in iframe (HubSpot, Marketo, Pardot) | Fills using iframe element refs |
| Multi-step forms | Completes each step in sequence |
| JS-triggered download (no href) | Intercepts via network requests |
| CDN-hosted PDF with redirect chain | `curl -L` follows up to 10 hops |
| Blob URL / JS-protected download | Browser fetch → base64 → disk |
| Cookie consent banners | Clicks Reject / Necessary only |
| Marketing opt-in checkboxes | Unchecks automatically |
| Email-gated downloads | Detected and flagged for manual follow-up |
| CAPTCHAs | Flagged — never bypassed |
| Login walls | Flagged |

---

## Credentials

Stored at `$CLAUDE_PLUGIN_DATA/.env` after `/setup`, covering the common lead-gen form fields (name, job title, company, location, work email, industry, and so on). Fields not in your credentials are filled with plausible defaults derived from your profile. For project-local testing, a `.env` file in the current working directory is also recognized.

---

## Details

| | |
|---|---|
| **Version** | 1.0.7 |
| **Maintained by** | Claude Plugins Marketplace |
| **Runtime** | Node.js via `npx` (Playwright) |
| **MCP servers** | Playwright (configured automatically via `.mcp.json`) |
| **Credentials** | `${CLAUDE_PLUGIN_DATA}/.env` |
