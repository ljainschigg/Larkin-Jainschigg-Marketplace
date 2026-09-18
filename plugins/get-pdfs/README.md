# get-pdfs

Downloads PDFs from gated lead-gen landing pages. Fills out access forms using your stored credentials, follows redirects and CDN hops, and saves files to `./resources/`.

Also used internally by the `researcher` plugin for PDF retrieval.

---

## Install

```
/plugin install get-pdfs@claude-plugins
```

## Setup

Run once after installing:

```
/setup
```

This installs the Playwright browser and creates your credentials file at `$CLAUDE_PLUGIN_DATA/.env`.

## Use

```
/get-pdfs https://vendor.com/whitepaper https://analyst.io/report2025
```

Pass one or more landing page URLs. The skill works sequentially, fills each form, downloads the PDF to `./resources/`, and returns a status table.

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

Stored at `$CLAUDE_PLUGIN_DATA/.env` after `/setup`. Fields:

| Key | Description |
|-----|-------------|
| `FIRST_NAME` | Given name |
| `LAST_NAME` | Family name |
| `JOB_TITLE` | Job title |
| `COMPANY` | Employer |
| `CITY` | City |
| `STATE` | State / province |
| `COUNTRY` | Country |
| `PHONE` | Phone (used only on required fields) |
| `EMAIL` | Work email |
| `INDUSTRY` | Industry / vertical |
| `LANGUAGE` | Preferred language |

For project-local testing, a `.env` file in the current working directory is also recognized.

Fields not in your credentials (company size, revenue, referral source, etc.) are filled with plausible defaults derived from your profile.

---

## Details

| | |
|---|---|
| **Version** | 1.0.6 |
| **Maintained by** | Claude Plugins Marketplace |
| **Requires** | Playwright MCP (configured automatically via `.mcp.json`) |
