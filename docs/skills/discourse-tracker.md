---
description: "Track what the AI industry is talking about right now, and keep a summary on hand so your writing and research stay current."
---

# discourse-tracker

Maintains a shared AI discourse context file at `~/.claude/shared-context/current-discourse.md` by doing a fast, shallow scan of frontier labs, practitioners, community signal, infrastructure news, regulatory updates, and new product introductions. Run it weekly — it takes a few minutes and costs a fraction of a deep-research pass.

Any other skill can read from `~/.claude/shared-context/current-discourse.md` to stay current on what's happening in the AI space without doing its own research.

---

## Install

If you haven't added the marketplace yet:

```
/plugin marketplace add ljainschigg/Larkin-Jainschigg-Marketplace
```

Then install the plugin:

```
/plugin install discourse-tracker@Larkin-Jainschigg-Marketplace
```

---

## Use

```
/update-discourse
```

That's it. The skill scans the source list, extracts signal, prepends a dated section to the shared context file, and reports what it found.

To customize what gets scanned, edit `sources.md` in the skill directory:

```
~/.claude/plugins/discourse-tracker-Larkin-Jainschigg-Marketplace/skills/update-discourse/sources.md
```

Add or remove sources, adjust what to look for in each category, or add new categories entirely.

---

## Scheduling

Run it weekly via the schedule skill:

```
/schedule weekly /update-discourse
```

---

## How other skills use it

Any skill can read the shared context file at runtime:

```
Read ~/.claude/shared-context/current-discourse.md for current AI discourse before proceeding.
```

Skills that benefit most: content ideation, competitive analysis, market positioning, anything where "what's happening right now" matters. The [karpathy-kb](karpathy-kb.md) plugin can compile its output into a provenance-tracked wiki.

---

## How it works

For each category in `sources.md`, the skill fetches 1–2 sources, extracts 3–5 signal points (new releases, pricing changes, hot debates, notable quotes, trending tools), and moves on. No adversarial verification — the goal is currency, not certainty. Sections older than 90 days are pruned automatically to keep the file lean.

---

## Details

| | |
|---|---|
| **Version** | 1.0.5 |
| **Maintained by** | Claude Plugins Marketplace |
| **Shared context** | `~/.claude/shared-context/current-discourse.md` |
