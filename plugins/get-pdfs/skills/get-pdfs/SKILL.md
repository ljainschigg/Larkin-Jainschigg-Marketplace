---
name: get-pdfs
description: Download PDFs from a list of gated lead-gen landing pages. Fills out access forms using stored credentials, retrieves each PDF to ./resources/, and returns a status table. Called directly by users or by other skills (e.g. researcher).
---

# get-pdfs

Download PDFs from gated landing pages. Works sequentially through the list, fills forms, follows redirects and CDN hops, and saves PDFs to `./resources/`.

---

## Input

`args` is a whitespace- or newline-separated list of landing page URLs.

---

## Setup

### 1. Load Playwright tool schemas

Before any browser work, load these via ToolSearch:

```
select:mcp__playwright__browser_navigate,mcp__playwright__browser_snapshot,mcp__playwright__browser_fill_form,mcp__playwright__browser_click,mcp__playwright__browser_select_option,mcp__playwright__browser_type,mcp__playwright__browser_wait_for,mcp__playwright__browser_evaluate,mcp__playwright__browser_network_requests,mcp__playwright__browser_network_request,mcp__playwright__browser_take_screenshot
```

### 2. Read credentials

Check for credentials in this order:

1. `${CLAUDE_PLUGIN_DATA}/.env` — standard installed-plugin location
2. `./.env` in the current working directory — for testing / project-local use

Parse whichever file is found first as KEY=VALUE (ignore blank lines and `#` comments).

Supported key formats — accept either convention:

| Canonical key | Researcher-compat alias | Meaning |
|---|---|---|
| `FIRST_NAME` | — | Given name |
| `LAST_NAME` | — | Family name |
| `FIRST_NAME` + `LAST_NAME` | `RESEARCHER_NAME` (split on first space) | Full name |
| `EMAIL` | `RESEARCHER_EMAIL` | Work email |
| `COMPANY` | `RESEARCHER_COMPANY` | Employer |
| `JOB_TITLE` | `RESEARCHER_TITLE` | Job title |
| `PHONE` | `RESEARCHER_PHONE` | Phone |
| `CITY` | — | City |
| `STATE` | `RESEARCHER_STATE` | State / province |
| `COUNTRY` | `RESEARCHER_COUNTRY` | Country |
| `INDUSTRY` | — | Industry / vertical |
| `LANGUAGE` | — | Preferred language |

If neither file is found, or any of `EMAIL`, `COMPANY`, `JOB_TITLE` are blank, prompt the user interactively for the missing values before proceeding.

### 3. Ensure output directory

```bash
mkdir -p ./resources
```

The downloaded PDFs are the user's own material and land in `./resources/` — a working folder that may be a git repo. Ensure a `.gitignore` here ignores `resources/` (create it or append the line); never `git add`/commit the fetched files.

### 4. Initialize results list

One entry per URL: `{ url, status, local_path, notes }`. Populate as you go.

---

## Per-URL process

Work through URLs **sequentially**. For each URL, follow the retrieval loop below. The loop may execute more than once for a single URL (e.g. form submission leads to a thank-you page with a download button).

---

### Stage 1 — Navigate and settle

```
browser_navigate(url)
browser_wait_for(time: 2)
browser_snapshot()
```

---

### Stage 2 — Dismiss cookie / consent banners

If a cookie consent banner is visible:
- Click **"Reject"**, **"Decline"**, **"Necessary only"**, **"Reject all"**, or the close (×) button.
- Do **not** click "Accept all", "Accept", or "I agree to cookies" — these expand data sharing.
- If no reject option exists and the banner blocks the page, click the least-permissive available option, then continue.

After dismissing, `browser_snapshot()` again.

---

### Stage 3 — Classify the page

Read the snapshot and determine which branch applies:

| What you see | Branch |
|---|---|
| URL ends `.pdf`, or page is a PDF viewer with no surrounding page chrome | **A — Direct PDF** |
| A download / "Get the report" button with a direct `.pdf` href | **A — Direct PDF** |
| A download button with no href (JavaScript-triggered) | **B — JS download** |
| A contact form (inline or in an iframe) | **C — Form gate** |
| "Check your email" / "We've sent you a link" | **D — Email gate** |
| Login wall, account required | **E — Login wall** |
| Blank, error page, or no PDF-related content | **F — Dead end** |

---

### Branch A — Direct PDF link

Extract the `href` from the link or button. Proceed directly to **§ Download**.

---

### Branch B — JavaScript-triggered download

Click the download button:

```
browser_click(ref)
browser_wait_for(time: 2)
browser_network_requests(static: false)
```

Scan network requests for any URL containing `.pdf` or with `Content-Type: application/pdf`. If found, use that URL for **§ Download**.

If no PDF URL appears in network requests, the download may be a blob URL. Use the **browser fetch fallback** in **§ Download**.

---

### Branch C — Form gate

#### C1. Read the form structure

```
browser_snapshot()
```

Identify every field: label, type (text / email / phone / checkbox / radio / select / textarea), whether required, current state. Note whether the form is:
- **Inline on the page** — element refs are plain (`ref=123`)
- **Inside an iframe** — element refs are prefixed (`f1ref=45`, `f2ref=67`). Iframe forms are common on HubSpot, Marketo, and Pardot pages. Snapshot the iframe contents specifically if the main snapshot doesn't show fields.

Scroll down and re-snapshot if the form appears truncated or if progressive disclosure is likely.

#### C2. Fill fields

Map credential values to form fields by label. Use `browser_fill_form` for a batch of text/email fields; use `browser_select_option` for dropdowns; use `browser_click` for radio buttons and standalone checkboxes.

| Label patterns | Value |
|---|---|
| first name, given name, fname | `FIRST_NAME` |
| last name, surname, family name, lname | `LAST_NAME` |
| full name, name (single field) | `FIRST_NAME` + ` ` + `LAST_NAME` |
| email, e-mail, work email, business email | `EMAIL` |
| phone, telephone, mobile, business phone | `PHONE` — leave blank if marked optional |
| company, organization, employer, firm | `COMPANY` |
| title, job title, role, position, function | `JOB_TITLE` |
| city, town | `CITY` |
| state, province, region | `STATE` |
| country | `COUNTRY` |
| zip, postal code | `95008` |
| industry, vertical, sector | `INDUSTRY` — pick closest match from dropdown |
| language, preferred language | `LANGUAGE` |
| company size, employees, headcount | Pick `501–1000` or the closest available bracket |
| annual revenue | Pick `$100M–$500M` or the closest available bracket |
| how did you hear, referral source | `Web search` or `Industry publication` |
| biggest challenge, interest, use case | One sentence appropriate for a Director of Content at a cloud-infrastructure company — e.g. "Managing technical documentation at scale across Kubernetes and cloud-native product lines." |
| comments, questions, message | Leave blank unless required; if required: "Requesting access to the resource." |

**Country and state fields need care:**
- For dropdowns: snapshot to inspect available options, then select the option that matches (e.g. "United States", "USA", "US", "United States of America" — whichever appears). Never type into a dropdown.
- For text inputs: enter the full name first ("United States", "California"). If validation fails on submit, retry with abbreviation ("USA", "CA").

**Required fields not covered above:** make a sensible, innocuous choice consistent with the profile. Do not leave required fields blank.

#### C3. Opt out of marketing

After filling content fields, before submitting, actively find every consent-related checkbox or radio group:

- **Uncheck** any checkbox whose label contains: newsletter, updates, marketing, promotional, communications, news, offers, partner, third.party, contact me, keep me informed, send me, I agree to receive, I would like to receive, keep in touch
- **Check** any checkbox whose label contains: do not contact, opt out, unsubscribe, no thanks, I do not want
- **Check** required legal-consent boxes (terms of service, privacy policy, legal agreement) — these are necessary, not marketing

When a checkbox state is ambiguous, snapshot it, reason about the label, and default to the opt-out-of-marketing choice.

#### C4. Submit

```
browser_click(submit_ref)
browser_wait_for(time: 3)
browser_snapshot()
```

**If form validation fails** (error messages, highlighted fields): snapshot, identify the problem field, correct it, resubmit once. If validation fails again, log as hard case and stop.

**If the form is multi-step:** complete each step in sequence, re-entering the loop at C1 for each step.

**After successful submission:** re-enter the retrieval loop at Stage 3 to classify the result page (typically a thank-you page).

---

### Branch D — Email gate

The page says the PDF will be sent to the user's inbox. No automation path.

```
status: email-gate
notes: "Page says to check email for the download link."
```

Log and move to next URL.

---

### Branch E — Login wall

The page requires an account login (not a lead-gen form).

```
status: hard-case
notes: "Login wall — account required."
```

Log and move to next URL.

---

### Branch F — Dead end

The page is blank, an error, or contains no PDF-related content.

```
status: hard-case
notes: "<error text or description of what was found>"
```

Log and move to next URL.

---

## § Download

You have a PDF URL. Download it to `./resources/`.

### Pre-step — Post-submission session check

**If you arrived here from a form submission (Branch C → thank-you page → Branch A or B):** the download server may require the session cookies from that form submission to authenticate the download. Curl opens a fresh cookieless connection and will fail silently (returning an HTML redirect instead of a PDF).

In this case: **skip Steps 1–2 and go directly to the Browser fetch fallback** below, running it inside the current browser session before navigating anywhere else. Only fall back to curl if the browser fetch returns non-PDF content.

### Step 1 — Determine filename

Priority order:

1. Run `curl -sI "<url>" | grep -i content-disposition` and parse the `filename=` value.
2. Take the last path segment of the URL, strip query params, decode percent-encoding.
3. Use a sanitized version of the landing page `<title>` tag + `.pdf`.
4. Fallback: `download-<sanitized-domain>-<index>.pdf`

Sanitize: lowercase, replace spaces and special characters with `-`, trim to 120 chars, ensure `.pdf` suffix.

### Step 2 — Download with curl

```bash
curl -L --max-redirs 10 -A "Mozilla/5.0 (compatible)" \
  -o "./resources/<filename>" "<pdf-url>"
```

`-L` follows CDN hops and short-link chains.

### Step 3 — Validate

```bash
head -c 4 "./resources/<filename>" | cat
```

A valid PDF begins with `%PDF`. If the file starts with `<html` or `<!DOCTYPE`, the server returned an HTML error page instead of the PDF. Retry once with a browser-like `Referer` header:

```bash
curl -L --max-redirs 10 -A "Mozilla/5.0 (compatible)" \
  -H "Referer: <original-landing-page-url>" \
  -o "./resources/<filename>" "<pdf-url>"
```

If the second attempt still returns HTML, try the **browser fetch fallback** below. If that also fails, delete the partial file, log as hard case, and move on.

### Browser fetch fallback (blob URLs and JS-protected downloads)

Use when: curl returns HTML despite a valid URL, or the download was triggered by JavaScript with no accessible `href`.

```
browser_navigate(<pdf-url>)
browser_evaluate(function: "() => fetch(location.href).then(r => r.blob()).then(b => new Promise(res => { const fr = new FileReader(); fr.onload = () => res(fr.result); fr.readAsDataURL(b); }))")
```

This returns a base64 DataURL string (`data:application/pdf;base64,<data>`). Strip the prefix and decode to disk:

```bash
echo "<base64_data>" | sed 's/data:application\/pdf;base64,//' | base64 -d > "./resources/<filename>"
```

Validate with the `%PDF` check above.

---

## Known site behaviors

| Site / pattern | Behavior | Strategy |
|---|---|---|
| HubSpot-hosted forms | Form in iframe — use iframe element refs (f1/f2 prefix) | Branch C, iframe mode |
| Marketo / Pardot forms | Same-page form; thank-you page has PDF link | Branch C → re-loop → Branch A |
| JFrog, Portworx, Port | Thank-you page has "View the Report" or "Download" button | Branch C → re-loop → Branch A or B |
| VAST Data and similar | "Download PDF" button, no href, JS-triggered | Branch B |
| CNCF, NIST (direct) | Direct PDF link on landing or TOC | Branch A |
| EU Commission / EDPB | curl sometimes fails DNS; browser fetch works | Browser fetch fallback |
| Short links (t.co, bit.ly) | May redirect to vendor homepage instead of resource | Re-classify final URL; if homepage, Branch F |
| reCAPTCHA / hCaptcha | Bot detection on form submit | Take screenshot, log as hard case, ask user |
| "Check your email" | No PDF on page | Branch D |
| resources.nvidia.com short-links | Signed JWT in thank-you page URL; link redirects to nvidia.com homepage if browser has navigated away or if fetched without session cookies | Use browser fetch fallback immediately from within the thank-you page session — do not curl, do not navigate away first |

---

## Hard cases — end-of-run review

After all URLs have been processed, if any entries are `hard-case` or `email-gate`, present them:

```
The following URLs need attention:

1. https://example.com/whitepaper  — CAPTCHA detected [screenshot saved to ./resources/captcha-1.png]
2. https://vendor.io/report        — Form validation failed: "Invalid email domain"
3. https://docs.co/guide           — Email gate

Would you like to retry any of these, or provide guidance?
```

Wait for the user's response and act on any instructions. If there is no response, note the outstanding items in the final results and conclude.

---

## Results

Return a markdown table when all processing is complete:

```
## get-pdfs results

| # | URL | Status | Local path | Notes |
|---|-----|--------|------------|-------|
| 1 | https://... | ✓ saved | ./resources/cloud-report-2025.pdf | |
| 2 | https://... | ✓ saved | ./resources/kubernetes-guide.pdf | |
| 3 | https://... | email-gate | — | Check inbox |
| 4 | https://... | hard-case | — | CAPTCHA — screenshot at ./resources/captcha-4.png |

Downloaded: 2  /  Email-gated: 1  /  Hard cases: 1
```

---

## Standing rules

- Never click "Accept all cookies" — always reject or choose necessary-only.
- If a modal or overlay appears over the landing page, work with it — do not dismiss it.
- Treat `PHONE` as optional — leave blank if the form marks it optional.
- Signed PDF URLs (containing tokens, expiry params) expire — download immediately upon discovery using the **browser fetch fallback** (not curl), so session cookies are preserved.
- If a page redirects to a generic homepage after form submission, classify as Branch F.
- Do not open PDFs in the browser — download to disk only.
- CAPTCHAs: take a screenshot, log as hard case, never attempt to solve programmatically.
