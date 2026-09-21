---
description: "Run a focus group with simulated participants built from published audience research, so you can test a product or message early."
---

# focus-group

Run a simulated focus group or enterprise buying-committee evaluation to pre-flight products, messages, concepts, UI designs, or any stimulus before committing to real fieldwork.

The skill operates in two modes selected automatically from your audience brief:

- **B2C mode** — a panel of 5 diverse consumer personas runs a structured five-round focus group discussion. Outputs a qualitative synthesis with resonance/friction breakdowns, segment fault lines, and an SSR-derived quantitative intent signal.
- **B2B mode** — a buying committee of 5–6 stakeholders (Economic Buyer, Technical Evaluator, Security Gatekeeper, Procurement, End-User Champion) runs a post-demo internal evaluation meeting. Outputs champion/blocker maps, veto-aware advocacy scores, a most-likely deal-killer, and a concrete vendor to-do list.

## Scientific grounding

The skill is built on **Maier et al. (2025), "LLMs Reproduce Human Purchase Intent via Semantic Similarity Elicitation of Likert Ratings"** (PyMC Labs / Colgate-Palmolive, arXiv:2510.08338), validated across 57 consumer surveys with 9,300 human responses.

The key finding: asking an LLM directly for a numeric rating produces pathologically narrow distributions (KS similarity = 0.26 vs. real humans). Free-text elicitation followed by mapping to anchor statements — **Semantic Similarity Rating (SSR)** — achieves KS = 0.88 and 90% of human test-retest reliability. The skill applies this principle throughout: personas always speak freely; scores are inferred from content, never self-reported.

Two genuine advantages of synthetic panels over real ones, per the paper: less positivity bias (synthetic respondents are more discriminating), and richer qualitative responses (real human free-text answers are typically shallow; LLM synthetic consumers articulate specific reasons and surface concerns).

Persona construction additionally draws on the **silicon sampling** method (Argyle et al., 2023; Park et al., 2024). Session structure follows Krueger & Casey's five-question arc with moderator technique from Kolb (2008). Synthesis applies Braun & Clarke thematic analysis.

## Install

If you haven't added the marketplace yet:

```
/plugin marketplace add ljainschigg/Larkin-Jainschigg-Marketplace
```

Then install the plugin:

```
/plugin install focus-group@Larkin-Jainschigg-Marketplace
```

## Use

```
/focus-group
```

Claude asks for your stimulus, audience, and top learning goals, then selects B2C or B2B mode automatically. For B2C it assembles a diverse consumer panel; for B2B it assembles a buying committee matched to your target customer profile.

Pass the stimulus inline to skip intake:

```
/focus-group "New tagline: 'The bank that actually explains itself'"
```

## How it works

### B2C mode

Builds 5 consumer personas from dense profiles (age, income, occupation, media diet, prior category experience, values) and runs a five-round moderated session: warm-up → first encounter → associations → key questions → closing. After Round 4, the moderator silently derives an intent score (1–5) for each persona by comparing their free-text response to five purchase-intent anchor statements — the SSR approximation. The synthesis opens with a panel intent table, then covers what resonated, what created friction, segment fault lines, and next moves.

**Demographic reliability note (from Maier et al.):** Age and income condition well. Gender, region, and ethnicity replicate poorly — the skill avoids building panels whose key insight depends on those axes, and flags it when the user's brief requires them.

### B2B mode

Builds a buying committee of 5–6 stakeholders with role-specific profiles (stack, current pain, internal KPIs, existing vendor lock-in, individual kill-shot risk). Runs a post-demo internal evaluation meeting across five rounds: current-state context → first impressions → role-targeted deep evaluation → key questions → kill-shot and path forward. Each stakeholder receives an advocacy score (1–5) derived from their free-text responses against B2B-specific anchors ranging from "I'd recommend against this" to "I'd actively champion this internally."

The synthesis includes a veto-aware committee signal table (a mean of 4.2 is irrelevant if the CISO scores 1), champion/blocker map, most likely deal-killer, and a "What would need to be true" section that translates session findings into the vendor's concrete next steps.

**B2B reliability note:** Role, title, company size, industry vertical, and tech stack condition well — all heavily represented in LLM training data. Internal org politics and company-specific vendor history do not simulate reliably.

## Known limitations

- Domain coverage: works best for product and service categories with abundant online discourse (reviews, forums, analyst content). Thin-coverage domains (rare industrial, highly classified verticals) degrade.
- Cannot model real purchasing constraints: budget cycles, shelf context, marketing exposure, embodied reactions to physical products.
- B2B sessions model the concerns, not the political process for resolving them.
- Panel/committee size is N=5. Directional signals are meaningful; individual responses are not statistically significant.

## Details

| | |
|---|---|
| **Version** | 1.0.5 |
| **Tier** | platform |
| **Maintained by** | Claude Plugins Marketplace |
