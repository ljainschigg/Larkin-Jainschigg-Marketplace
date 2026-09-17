---
name: exec-content-mine
description: Extract article ideas and quotable clip moments from an executive or SME conversation transcript, tuned to your organization's context
---

**Person/org-neutral engine.** Everything organization-specific lives in instance config gathered at setup, never in this skill.

First, read your organization's context from **`org-context.md`** in the current directory. It defines your strategy, positioning, products/technology, tone, target audiences, competitive framing, and proof points — and it shapes everything you extract. If `org-context.md` is absent, copy `templates/org-context.md` and interview the user to fill it (territory/market, products & technology, target audiences, tone/voice, competitive framing, proof points, current strategic context) before proceeding.

Then, if `~/.claude/shared-context/current-discourse.md` exists, read it — a snapshot of current industry discourse that keeps ideas timely and debates live rather than stale. Optional.

If the instance provides product/technical **reference documentation** (an org-configured location such as `./reference/`), consult it *on demand* to verify specific product capabilities, features, or integrations rather than guessing — read individual facts when needed, never the whole corpus upfront. If no reference is configured, rely on the transcript plus `org-context.md`.

## Keep the user's material out of git

This plugin works with the user's own material in the current directory — `org-context.md`, transcripts under `input/`, any `reference/` docs, and extracted ideas under `output/` — a folder that may be a git repo. Ensure a `./.gitignore` covers `input/`, `output/`, `reference/`, and `org-context.md` (create it or append the missing lines); never `git add`/commit them. This is the user's transcripts and your organization's proprietary context — not material to publish.

## Input

The user should have provided a transcript filename as an argument. Look for it at `./input/<filename>` relative to the current directory; else try `<filename>` as a path; else ask. Read the transcript in full before extracting anything.

## Title quality

Every idea needs a specific, publishable working title — bold and specific, the kind a smart, skeptical reader stops at. The provocation must come from genuine insight, not bait. Best test: does the article deliver on the title's promise, and does the answer surprise in a way that matters? The surprise should live in the *answer*, not just the question. Never use "Everyone thinks X, actually Y" as a title — that's the argument's shape, not the article. If you cannot write a good title for an idea, the idea is not ready.

## Ranking

Within each section, rank ideas before writing them out. Most provocative, novel, and central-to-your-organization's-vision first. Ask: which of these, if published, would most change how a target reader thinks about the market — and most advance the narrative that your organization's approach is the right answer? Those go to the top. Cut weak or conventional ideas rather than list them.

## Section 1: Boffo

Goal: take a stand on an issue important to your organization and its vision. These ideas are indirectly derived from the transcript — synthesized from its themes, implications, and live community debates; they go beyond what was explicitly said. Target ~800 words when written.

Generate 3–5 ideas by running these lenses over the transcript (grounded in `org-context.md`):

- **Contrarian reframe.** What does conventional wisdom say, and what does your organization's actual production experience contradict or complicate? The uncomfortable version of a settled idea is usually the interesting one.
- **Stakes escalation.** Push each first-pass idea one level further — to the implication that's non-obvious or that makes someone's current strategy look wrong.
- **The unasked question.** What did the interviewer not ask that, answered honestly, would be the most surprising or uncomfortable thing your organization could say publicly?
- **Privileged knowledge.** What has your organization learned from real deployments that competitors can't match? Experience, not opinion.
- **Live debates.** Where does the transcript, or your organization's position, speak to currently-contested questions in your field?

For each idea:

```
### <Title>

* **Summary:** One sentence capturing the core argument.
* **Why we should write this:** One sentence on strategic rationale.
* **Description:** One paragraph briefing a writer to execute the piece — specific about products, data points, and the argument's shape.
```

## Section 2: Authoritative

Goal: identify a customer challenge, state the characteristics of a technical solution, and show how one of your organization's products or mission pillars meets those requirements optimally. Ideas may be direct or indirect from the transcript. A Vision Article is ~800 words; an Educational spin can be longer.

Generate 5–8 ideas directly from the transcript. Apply `org-context.md`: favor ideas that advance positioning, resonate with target audiences, and reflect the tone and content goals it describes. Same per-idea format as Section 1.

## Section 3: Out-Takes

Goal: identify segments where someone from your organization says something pithy about customer needs, solution characteristics, unsolved industry problems, or how to solve a problem with your products. Include timestamps (start–end) when the transcript has them; if it only marks speaker-turn boundaries, use this turn's start to the next turn's start. Omit timestamps only if there are none at all.

Include 5–15 clip moments; prefer passages that stand alone.

For each clip:

```
### <Short label for the moment>

* **Summary:** One sentence.
* **Why we should excerpt this:** One sentence.

#### Transcript

> Verbatim quote. Lightly clean obvious filler ("um", "you know") but otherwise preserve exact wording.
> Timestamp: <start–end> | Speaker: <name>

#### Intro options

Three social-media copy options. Each: a headline (sentence case — capitalise only the first word and proper nouns, never title case) and a 1–2 sentence hook. Where a clip connects to a Boffo or Authoritative idea, note it (e.g. _Connects to: Boffo #1_) and use that frame in at least one option.

**A.** **<Headline>**
<Hook>

**B.** **<Headline>**
<Hook>

**C.** **<Headline>**
<Hook>
```

## Output

Derive a short identifier from the transcript filename (e.g. `acme-podcast-ai-ops` from `Acme_Podcast_AI_Ops.md`): strip extension, lowercase, hyphens. Write one file to `./output/`:

**`ideas-from-<identifier>.md`**

```
# Content ideas from: <original filename>

_Extracted <date>_

## Boffo
### 1. <Title>
...

## Authoritative
### N. <Title>
...

## Out-Takes
### <Label>
...
```

The output is for executive review and must be pristine: no meta-commentary, no quality assessments, no notes about the extraction process, no hedges. Do not use horizontal rules. Every sentence should be usable as-is.

After writing the file, report back to the user (not in the file): the path; counts of Boffo ideas, Authoritative ideas, and clip moments; and any items needing fact-checking or sensitivity review before the file goes further — named specifically.
