# seo-claude-plugin

Produces a complete, SEO-optimized article from a structured brief you supply. The workflow guides Claude through nine sequential steps: capturing the brief, establishing the brand perspective, defining a research brief, handing off to the researcher plugin, annotating the outline with stats, drafting, and two editing passes for sourced assertions and uniform voice.

You bring the brief and (optionally) a brand profile; the plugin brings the workflow.

---

## Prerequisites

- **`/researcher`** must be installed — it handles the web research phase (step 5)
- **Git** on the PATH (used only if you ask the workflow to clone documentation repos)
- A **structured brief** for the article: title, description, target terms to include, links to include, and a proposed outline. A fill-in template ships at `skills/seo-claude-plugin/system/brief-template.md`.
- Optionally, a **brand profile** — your own reusable instance data (organization, products, positioning, competitors to exclude, sources to prefer, reference docs). A template ships at `skills/seo-claude-plugin/system/brand-profile-template.md`. Nothing about any specific organization is baked into the plugin.

## Install

If you haven't added the marketplace yet:

```
/plugin marketplace add ljainschigg/Larkin-Jainschigg-Marketplace
```

Then install the plugin:

```
/plugin install seo-claude-plugin@lj-marketplace
```

## Use

Run the workflow from the directory where you want the project output written (it uses the current directory as the project root):

```
/seo-claude-plugin
```

Claude guides you through the workflow interactively. Each of the nine steps ends with a STOP — review the output, then instruct Claude to continue.

At step 5, the workflow pauses and hands off to `/researcher` with the assembled research brief. Once research is complete and resources are saved, the workflow resumes from step 6.

**Project output** is written under the current directory:
- `article-data.json` — structured brief, brand perspective, and research allocations
- `outputs/{project-name}-article.md` — the finished article draft
- `topic-direction-goal.md` — research brief
- `candidate-links.md` — index of retrieved resources (written by the researcher plugin)
- `resources/*.txt` — full text of retrieved resources (written by the researcher plugin)

`resources/`, `outputs/`, and `references/` are `.gitignore`d by the workflow — they hold your gathered material and third-party repos, not deliverables.

## How it works

The plugin encodes an SEO article workflow as a nine-step prompt sequence. Each step reads a bundled instruction file from the plugin root, performs its work, writes outputs to the project directory, and stops for review before advancing.

Steps 1–4 capture the brief, establish the brand perspective, and define the research brief. Step 5 hands control to `/researcher`, which retrieves authoritative web resources and saves them as text files. Steps 6–9 resume with the researched material: annotating the outline with narrative-arc notes and stats allocations, drafting the full article, sourcing every factual assertion with a linked citation, and applying a final voice-and-style pass governed by `WRITING-RULES.md`.

## Bundled reference material

`skills/seo-claude-plugin/system/` holds the workflow's bundled, organization-neutral files:

- `WRITING-RULES.md` — house style rules (no em-dashes, sourced assertions, rule-of-three avoidance, bullet formatting)
- `base-article-data.json` — the working schema for one article project
- `brief-template.md` — fill-in template for a per-article brief
- `brand-profile-template.md` — fill-in template for your reusable brand instance data

Your brand facts, product knowledge, competitor lists, and reference documentation are **your own instance data** — you keep them outside the plugin and point the workflow at them.

## Details

| | |
|---|---|
| **Version** | 1.2.4 |
| **Type** | skill |
| **Depends on** | `researcher` |
| **Project data** | the current working directory |
