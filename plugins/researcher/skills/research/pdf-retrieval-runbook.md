# PDF Retrieval Runbook

This runbook is used by the `/fetch-pdf` skill and referenced by `/research` during Pass 2. It documents the complete decision tree for retrieving PDFs from any URL — direct or gated — using MCP Playwright tools.

---

## The retrieval loop

For each PDF candidate, execute this sequence. The loop may repeat if the first page is a landing page that leads to another page with the PDF.

### Step 1 — Navigate and wait

```
browser_navigate(url)
browser_wait_for(time: 2)
```

### Step 2 — Dismiss cookie/consent banners

```
browser_snapshot()
```

Look for cookie consent banners. Click "Accept All", "Accept", "I agree", or similar. If a close button (×) is visible, click it. If none visible, press Escape and continue.

### Step 3 — Read the page

```
browser_snapshot()
```

Understand what kind of page this is. Identify:
- Is there a direct link or button to download/view the PDF?
- Is there a form to fill (same-page or in an iframe)?
- Is there any indication the PDF will be emailed rather than shown?

---

## Decision tree

### Branch A — Direct PDF link or button with href pointing to .pdf

Extract the URL from the `href` attribute. Call the `extract_pdf` MCP tool:

```
extract_pdf(
  source: "<pdf-url>",
  outdir: "<project-resources-dir>",
  pdf_name: "<name>.pdf"   // optional
)
```

Write a provenance header to the top of the extracted `.txt` file:

```
Source: <canonical landing page URL — the URL the user or researcher navigated to, not the signed PDF URL>
Retrieved: browser (Playwright) + pdf-parse [or tesseract OCR]
Date: <iso date>
```

Use the **original landing page URL** as `Source:`, not the signed or dynamic PDF download URL — signed URLs expire and are not suitable for citation. The local `.pdf` file is the artifact; the landing page is the stable, citable reference.

Done. Update candidate-links.md.

### Branch B — Download button with no href (JavaScript-triggered download)

Click the button:
```
browser_click(ref)
```

Immediately check network requests:
```
browser_network_requests(includeStatic: false)
```

Look for a request with `.pdf` in the URL or `Content-Type: application/pdf`. Extract the URL and call `extract_pdf` as in Branch A.

If no PDF URL appears in network requests, the download may be a blob URL. Use the browser fetch fallback (see below).

### Branch C — Form gate (landing page with contact form)

Fill and submit the form using credentials from `${CLAUDE_PLUGIN_DATA}/.env`. Then return to Step 1 of the loop on the resulting page (thank-you page or redirect).

See **Form-filling procedure** below.

### Branch D — "Check your email" or email verification required

No automation path exists. Mark as inaccessible:

```
Status: ❌ failed — email-gated; PDF sent to inbox, not shown on page
```

Move to the next candidate.

### Branch E — No PDF, no form, no download button

The page does not appear to yield a PDF. Mark as inaccessible:

```
Status: ❌ failed — no PDF or download CTA found on page
```

---

## Form-filling procedure

Read credentials from `${CLAUDE_PLUGIN_DATA}/.env` at invocation. Use only these values — do not invent or substitute.

### Reading form structure

```
browser_snapshot()
```

Identify all form fields. Note whether the form is inline on the page or inside an iframe — iframe fields use different element refs (prefixed `f1`, `f2`, etc.).

### Filling fields

Map credential values to form fields by label:

| Field label (common variants) | Credential |
|---|---|
| Name / Full name / First + Last name | RESEARCHER_NAME (split if separate fields) |
| Email / Work email / Business email | RESEARCHER_EMAIL |
| Company / Organization / Employer | RESEARCHER_COMPANY |
| Job title / Title / Role | RESEARCHER_TITLE |
| Phone / Mobile / Business phone | RESEARCHER_PHONE |
| Country | RESEARCHER_COUNTRY |
| State / Province / Region | RESEARCHER_STATE |

For text inputs: `browser_type(ref, value)`
For dropdowns/comboboxes: `browser_select_option(ref, label)` — use the visible text label exactly as it appears in the option list
For multiple fields at once: `browser_fill_form(fields_object)`

**Country and state fields require extra care** — forms vary in what they accept:
- For **dropdowns**: take a snapshot to inspect the available options, then select the option that best matches (e.g., "United States", "USA", "US", or "United States of America" — pick whichever is present).
- For **text inputs**: enter the full name first (e.g., "United States", "New York"). If validation fails, retry with the common abbreviation ("USA", "NY").

### Submitting

Click the submit button:
```
browser_click(submit_ref)
browser_wait_for(time: 3)
```

Then return to Step 1 of the retrieval loop. The resulting page is typically a thank-you page with a PDF download link.

### If form validation fails

Take a snapshot, identify the invalid or missing field, correct it, resubmit. One correction attempt only — if it fails again, mark as inaccessible.

---

## Browser fetch fallback (for network-blocked or blob URLs)

Use this when:
- `extract_pdf` fails with a DNS or connection error on a known valid URL
- A download button produces a blob URL not visible in network requests

```
browser_navigate(pdf_url)
browser_evaluate("""
  fetch(location.href)
    .then(r => r.blob())
    .then(b => new Promise((res) => {
      const reader = new FileReader();
      reader.onload = () => res(reader.result);
      reader.readAsDataURL(b);
    }))
""")
```

This returns a base64 DataURL string. Decode it, trim everything before `%PDF`, and write the bytes to a `.pdf` file. Then call `extract_pdf` with `extract_only: true` on the saved file.

---

## Recorded outcomes — known site behaviors

| Site / Pattern | Behavior | Strategy |
|---|---|---|
| CNCF, NIST (direct) | Direct PDF link on landing or TOC | Branch A |
| HubSpot-hosted forms | Form in iframe — use iframe refs | Branch C |
| Marketo / Pardot forms | Same-page form; thank-you page has PDF link | Branch C |
| JFrog, Portworx, Port | Thank-you page has "View the Report" or "Download" link | Branch C → Branch A |
| VAST Data and similar | "Download PDF" button, no href, JS-triggered | Branch B |
| EU Commission / EDPB | Python requests sometimes fail DNS; browser fetch works | Browser fetch fallback |
| EUR-Lex | URL ends in .pdf but serves HTML | Extract text directly from page, save as .txt |
| Short links (t.co, bit.ly) | May redirect to vendor homepage instead of resource | Navigate and check final URL; if homepage, mark inaccessible |
| Any gate with reCAPTCHA | Bot detection triggered on form submit | Stop, take screenshot, ask user to complete CAPTCHA |
| "Check your email" thank-you | No PDF on page | Branch D — mark inaccessible |
