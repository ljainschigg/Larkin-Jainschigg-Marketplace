# Anti-Thrashing Rules for Web Retrieval

These rules exist because AI-assisted web retrieval has a failure mode: trying the wrong tool repeatedly, or spinning on inaccessible sources, instead of moving on. Follow these rules throughout all retrieval phases.

---

## Tool selection — classify before fetching

Before touching any URL, classify it:

| URL type | First tool | Escalate to |
|---|---|---|
| Static page (news, Wikipedia, GitHub, docs, official publications) | `WebFetch` | playwright if content thin |
| JavaScript-heavy SPA (React apps, dashboards, `.app` domains) | playwright | — (no further escalation) |
| Known community sites (Reddit, HN, Stack Overflow) | `WebFetch` | playwright if needed |
| Gated landing page (whitepaper, analyst report, vendor research) | `/fetch-pdf` skill | — |
| Direct PDF URL (`.pdf` in path) | `node tools/extract-pdf.js` | browser fetch if download fails |
| Social media (Twitter/X, LinkedIn) | playwright | — |

Never use `WebSearch` when you already have a URL. Never use playwright for a URL that `WebFetch` hasn't failed on first.

---

## The two-attempt rule

Each URL gets **at most two tool attempts total**.

- Attempt 1: the classified first tool
- Attempt 2: the escalation tool (if first attempt returned thin content or failed)
- After two attempts: mark as inaccessible and move on

Never attempt the same tool twice on the same URL. "It might work if I try again" is not a valid hypothesis.

---

## Recognizing failure signals

Do not retry when you see these — escalate or move on:

| Signal | Meaning | Action |
|---|---|---|
| Response body < 800 chars of text | JS-rendered shell | Escalate to playwright |
| Page body contains a contact/registration form or sign-in prompt | Surprise gate | Re-classify as gated PDF; defer to Phase 6 (`/fetch-pdf`) — counts as attempt 1 |
| HTTP 403 / 401 | Auth required | Mark inaccessible |
| HTTP 429 | Rate limited | Mark inaccessible, note for retry later |
| Redirect to homepage | Resource moved or gated | Mark inaccessible |
| "Sign in to continue" | Login wall | Mark inaccessible |
| "Check your email for the report" | Email-gated PDF | Mark inaccessible — no automation path |
| CAPTCHA or bot challenge | Human verification required | Pause and ask the user to complete it. Document: "needs human to complete CAPTCHA" |
| Page snapshot shows no form fields and no download button | No retrievable asset | Mark inaccessible |

---

## PDF-specific rules

- If `WebFetch` or `extract-pdf.js` fails on a PDF URL with a network error, try fetching it via browser (`browser_navigate` + `browser_evaluate fetch()` base64 trick) — once.
- If a PDF downloaded successfully but `extract-pdf.js` extracted < 80 chars/page on average, the tool will automatically fall back to OCR. You do not need to intervene.
- If a PDF URL only appears after form submission, it may be a signed URL with a short expiry. Run `extract-pdf.js` immediately after obtaining it.

---

## Cap and move on

- Commit to a fixed number of sources before retrieval begins (typically 12–15 candidates from Phase 4).
- Do not add new candidates during retrieval to compensate for failures. The candidate list is fixed at the end of Phase 4.
- If more than 30% of candidates are inaccessible, note this in the synthesis summary as a research gap — do not chase replacements.

---

## Declare failure explicitly

When a source is inaccessible, update `candidate-links.md` immediately with:

```markdown
- **Status:** ❌ failed — <reason in one phrase>
- **Attempts:** <tool used> → <signal observed>
```

Do not leave entries in `⏳ pending` state after an attempt. The candidate-links.md file is the source of truth for retrieval state.

---

## CAPTCHA — always stop and ask

Never attempt to bypass a CAPTCHA automatically. If one appears:

1. Take a screenshot (`browser_take_screenshot`)
2. Tell the user: "I've hit a CAPTCHA on [URL]. Can you complete it? I'll wait."
3. After the user confirms, continue from where you left off.
