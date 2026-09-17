---
name: fetch-pdf
description: Retrieve a PDF from a URL, including gated landing pages that require form submission. Downloads the PDF and extracts its text. Use when given a URL that leads to a PDF or a whitepaper/report landing page.
---

Retrieve the PDF at the following URL and extract its text:

**Target URL:** $ARGUMENTS

## Output directory

Establish the output directory for this retrieval:

1. If `project-dir` is already set in context (called from `/research` or another plugin), save output to `{project-dir}/resources/`.
2. Otherwise, run `pwd` and save output to `{pwd}/resources/`. Create the directory if it does not exist.

Retain the resolved output directory as `resources-dir`.

## Your credentials for form-filling

If this URL leads to a gated landing page requiring contact information, use these credentials — and only these. Do not invent or substitute values.

!`grep -E "^RESEARCHER_" "${CLAUDE_PLUGIN_DATA}/.env" 2>/dev/null || echo "ERROR: credentials not found at ${CLAUDE_PLUGIN_DATA}/.env — run /setup first."`

---

## Instructions

Follow the PDF retrieval runbook exactly. The full decision tree, form-filling procedure, browser fetch fallback, and recorded outcomes are documented in:

`${CLAUDE_PLUGIN_ROOT}/skills/research/pdf-retrieval-runbook.md`

Read it before proceeding if it is not already in context.

Key rules:
- Each URL gets at most two tool attempts. If both fail, report clearly and stop.
- Never attempt to bypass a CAPTCHA — stop and ask the user to complete it.
- If the page says the PDF will be emailed, report this and stop — there is no automation path.
- If a signed PDF URL is obtained from a thank-you page or network requests, call `extract_pdf` immediately — signed URLs may expire.

## Extracting the PDF

Once you have a direct PDF URL, call the `extract_pdf` MCP tool:

```
extract_pdf(
  source: "<pdf-url>",
  outdir: "<resources-dir>",
  pdf_name: "<descriptive-name>.pdf"   // optional
)
```

## Output

Name files descriptively:
- PDF: `<slug-from-title-or-url>.pdf`
- Text: `<same-slug>.txt`

Prepend a provenance header to the `.txt` file:

```
Source: <canonical landing page URL — the URL originally navigated to, not the signed PDF download URL>
Retrieved: browser (Playwright) + pdf-parse [or tesseract OCR]
Date: <iso date>
```

The `Source:` URL must be the stable, human-navigable landing page — suitable for citation. Signed PDF URLs expire and must not be used here.

Report back:
- Whether the PDF was retrieved successfully
- The local path to the `.pdf` and `.txt` files
- The extraction method used (pdf-parse or tesseract OCR)
- Any obstacles encountered (form fields, redirects, errors)
