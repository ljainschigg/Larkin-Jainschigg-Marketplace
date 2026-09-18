# exec-content-mine

Turn an executive or SME conversation transcript into publishable content ideas: provocative article concepts and quotable social-media clip moments — tuned to *your* organization's strategy, products, and voice. Person/org-neutral engine; your specifics live in instance config, never in the plugin.

## Prerequisites

- A transcript to mine (e.g. under `./input/`).
- An **`org-context.md`** in your working directory describing your organization (mission, products, audiences, tone, competitive framing, proof points). If it's missing, the skill copies `templates/org-context.md` and interviews you to fill it at first run.
- *Optional:* product/technical reference docs under `./reference/` (or a configured location) for fact-checking — read on demand, never shipped.

## Install

```
/plugin marketplace add ljainschigg/Larkin-Jainschigg-Marketplace
/plugin install exec-content-mine@Larkin-Jainschigg-Marketplace
```

## Use

```
/exec-content-mine <transcript-filename>
```

Produces three ranked sections — **Boffo** (bold, synthesized thesis pieces), **Authoritative** (solution-oriented vision/education pieces), and **Out-Takes** (verbatim clip moments with social copy) — written to `./output/` as a pristine, review-ready file.

## How it works

The extraction logic is prompt-only and organization-neutral. It reads `org-context.md` (and optional reference docs) at runtime, so the *same* engine produces ideas tailored to one organization for one instance and entirely different ideas for another — the difference is the context file, not the code.

## Details

| | |
|---|---|
| **Version** | 1.0.7 |
| **Type** | skill |
| **Maintained by** | Claude Plugins Marketplace |
