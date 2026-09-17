---
name: update-discourse
description: Shallow-scans curated AI discourse sources and updates ~/.claude/shared-context/current-discourse.md with what's current.
---

Read the source list from `${CLAUDE_PLUGIN_ROOT}/skills/update-discourse/sources.md` before doing anything else. That file defines what to scan and what to look for in each category.

## What this skill does

It does a shallow, fast scan — not a deep research pass. For each category in the source list, fetch or search 1–2 sources, extract 3–5 signal points, and move on. No adversarial verification. No deep dives. The goal is currency, not certainty.

A signal point is: a new model or product release, a notable pricing change, a hot debate in the community, a significant quote from a key figure, a trending paper or tool, a regulatory development, or anything that would change how a practitioner thinks about the space right now.

## Scan instructions

Work through each category in sources.md in order. For each:

1. Fetch the listed URLs or run the listed searches — pick whichever 1–2 look most likely to have fresh signal
2. Extract signal points: what is new, notable, or changing? Concrete and specific beats vague and general
3. Note the source URL and approximate date for each point
4. Move to the next category — do not go deep on any single source

If a source is unreachable or returns nothing useful, skip it and note it briefly.

## Output format

Write a new dated section to `~/.claude/shared-context/current-discourse.md`. Prepend it — newest at top.

Format for the new section:

```
## Updated <YYYY-MM-DD>

### Frontier labs
- <signal point> [<source>]
- ...

### Practitioners and developer discourse
- <signal point> [<source>]
- ...

### Community signal
- <signal point> [<source>]
- ...

### Infrastructure and hardware
- <signal point> [<source>]
- ...

### Neoclouds and AI infrastructure operators
- <signal point> [<source>]
- ...

### New product introductions
- <signal point> [<source>]
- ...

### Business and enterprise AI
- <signal point> [<source>]
- ...

### Political, regulatory, and policy
- <signal point> [<source>]
- ...

### Market and investment
- <signal point> [<source>]
- ...

### Open-weight and local models
- <signal point> [<source>]
- ...
```

Omit any category where you found nothing notable — don't pad with generic statements.

## File management

- Create `~/.claude/shared-context/` if it does not exist
- If `current-discourse.md` already exists, read it first, then prepend the new section
- Remove any sections older than 90 days to keep the file manageable
- Keep the permanent context at the bottom (anything below a `---` separator and `## Permanent context` heading) — never prune or modify that section

## After writing

Tell the user:
- How many signal points were found across all categories
- Which categories had the most activity
- Anything that seems particularly significant for your organization's content positioning — especially new products, infrastructure economics shifts, or live debates that touch the areas your source list focuses on

Do not write these observations into the file — they go in the conversation only.
