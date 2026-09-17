---
name: research
description: Run a web research project. Discovers, fetches, and extracts sources — including gated PDFs — based on a topic. Use when the user asks to research a topic, gather sources, or start a research project.
---

## Resources
- Tool-use strategy and anti-thrashing rules: [anti-thrashing.md](anti-thrashing.md)
- Source selection criteria by mode: [resource-selection-rules.md](resource-selection-rules.md)
- Gated PDF retrieval workflow: [pdf-retrieval-runbook.md](pdf-retrieval-runbook.md)

---

## Project directory

Before anything else, establish `project-dir`:

1. If `project-dir` is already set in context (passed by a calling plugin such as seo-claude-plugin), use it as-is and skip to Phase 0.
2. If `$ARGUMENTS` is a valid absolute path to an existing directory, use it as `project-dir`.
3. Otherwise, run `pwd` and use the result as `project-dir`.

Ensure `{project-dir}/resources/` exists. Create it if not.

---

## Phase 0 — Profile detection

Check for an existing research brief or profile in the project directory.

IF `{project-dir}/topic-direction-goal.md` exists:
  Read it. Use its topic, direction, and goal as a **directed** research profile. Skip Phase 1 entirely and proceed to Phase 2.

ELIF `{project-dir}/research-profile.md` exists:
  Read it. Skip Phase 1 and proceed to Phase 2.

ELSE:
  Proceed to Phase 1.

---

## Phase 1 — Mode selection (interactive)

Greet the user and explain the three research modes. Ask them to choose, or offer to help them decide:

---

Before we start, I need to understand what kind of research this is — the answer determines which sources we look for, how we evaluate them, and what a good result looks like.

There are three modes:

**Exploratory** — You want to understand a topic broadly. No particular angle or conclusion to support. We cast a wide net across diverse source types: overviews, long-form explainers, reference material, varied perspectives.

**Directed** — You need research to support a specific piece of writing or argument. You have a topic, a focus angle (direction), and a conclusion to substantiate (goal). We favor authoritative, recent, quantitative sources — analyst reports, official publications, credible media.

**Perspective** — You want to know what practitioners, bloggers, and community members actually think — not what institutions say. We specifically target informal sources: Reddit, Hacker News, dev.to, personal blogs, Stack Overflow, forums.

Which fits your need? If you're not sure, tell me what you're trying to accomplish and I'll suggest a mode.

---

Once the user picks a mode, ask only the questions that mode requires:

**Exploratory:** Ask for the topic only. Confirm there is no specific angle.

**Directed:** Ask for:
1. Topic — what subject area are we researching?
2. Direction — what angle, focus, or constraint should shape the research?
3. Goal — what conclusion should the research support?

**Perspective:** Ask for:
1. Topic — what subject are people's opinions about?
2. Any recency constraint?
3. Any specific communities to prioritize or avoid?

Confirm the profile back to the user before saving it.

Save the profile to `{project-dir}/research-profile.md`.

---

## Phase 2 — Project setup

Confirm `{project-dir}/resources/` exists (create if needed). If it already contains prior work, read `{project-dir}/candidate-links.md` (if present) and inform the user of prior progress before proceeding.

**Keep the gathered data out of version control.** This project writes the user's research corpus — `resources/`, `candidate-links.md`, `search-phrases.md`, `research-summary.md` — into `{project-dir}`, which may be a git repository. Ensure a `{project-dir}/.gitignore` exists and lists these paths (create it or append the missing lines); never `git add`/commit the research data. It's the user's personal data, not something to publish.

---

## Phase 3 — Search phrase generation

Read [resource-selection-rules.md](resource-selection-rules.md) for the source criteria that apply to the current mode.

Generate 5–8 search phrases tailored to the mode and profile:

- **Exploratory:** Broad phrases covering the topic from multiple angles.
- **Directed:** Targeted phrases designed to surface authoritative, quantitative sources on the specific angle. Include phrases likely to surface analyst reports, official publications, and statistics.
- **Perspective:** Community-targeted phrases. Include site-specific operators where useful (e.g., `site:reddit.com`, `site:news.ycombinator.com`).

Save phrases to `{project-dir}/search-phrases.md`.

---

## Phase 4 — Discovery

Run WebSearch for each search phrase. Accumulate candidate URLs.

Target 12–15 candidates. Evaluate each against the source criteria in [resource-selection-rules.md](resource-selection-rules.md) for the current mode. Discard weak candidates.

For each candidate, record:
- URL
- Source type and authority
- Publication date (if determinable from snippet)
- One-line relevance note
- Whether it likely yields a PDF (look for report/whitepaper landing pages, `.pdf` links in snippets)

Save all candidates to `{project-dir}/candidate-links.md` using this format for each entry:

```markdown
### <N>. <Title>
- **URL:** <url>
- **Authority:** <source type>
- **Date:** <date or "unknown">
- **Relevance:** <one sentence>
- **Type:** <web page | PDF | gated PDF>
- **Status:** ⏳ pending
- **File:** —
```

Pause and show the candidate list to the user. Ask if they want to add, remove, or reprioritize any sources before fetching begins. Wait for confirmation or adjustments.

---

## Phase 5 — Retrieval (Pass 1: web pages)

Read [anti-thrashing.md](anti-thrashing.md) before starting. Follow its rules throughout retrieval.

For each candidate marked as a web page (not a PDF):

1. Attempt `WebFetch` first.
2. Evaluate the response:
   - If fewer than ~800 characters of actual text: JS-rendered shell — escalate to Playwright (step 4).
   - If the body contains a contact/registration form or sign-in prompt: surprise gate — re-classify as `gated PDF`, update `candidate-links.md`, and defer to Phase 6 (`/fetch-pdf`). Count the WebFetch as attempt 1.
   - Otherwise: content is good — proceed to step 3.
3. Save to `{project-dir}/resources/item<NN>-<slug>.txt` with a provenance header.
4. If escalating to Playwright: use `browser_navigate` + `browser_snapshot` to read the page.
   - If the snapshot reveals a contact/registration form or sign-in wall: re-classify as `gated PDF`, update `candidate-links.md`, and defer to Phase 6 (`/fetch-pdf`). Count both attempts toward the two-attempt limit.
   - Otherwise: use `browser_evaluate` to extract content. Save result.
5. Update `candidate-links.md` with status and file path.

Provenance header format for web pages:
```
Source: <url>
Retrieved: <method> (WebFetch | browser)
Date: <iso timestamp>

<content>
```

---

## Phase 6 — Retrieval (Pass 2: PDFs)

For each candidate marked as a PDF or gated PDF, invoke `/fetch-pdf <url>`.

The fetch-pdf skill handles the full gated landing page workflow — form filling, thank-you page navigation, PDF URL extraction, download, and text conversion. It will save output to `{project-dir}/resources/` because `project-dir` is already set in context.

After each invocation, update `candidate-links.md` with the outcome and file paths.

---

## Phase 7 — Synthesis

All fetching is complete. Do not make further web requests in this phase.

Write `{project-dir}/research-summary.md` covering:

1. **Sources retrieved** — how many candidates, how many successfully fetched, how many failed or were inaccessible
2. **Key findings** — the most important information found, organized thematically (not by source)
3. **Quantitative highlights** — any notable statistics or data points (directed mode only)
4. **Gaps** — topics or angles the research couldn't cover due to inaccessible sources

For directed mode, frame findings in relation to the stated goal.
For exploratory mode, organize by theme or subtopic.
For perspective mode, summarize the range of opinions found, noting any consensus or divergence.

Report to the user that research is complete and show the summary.
