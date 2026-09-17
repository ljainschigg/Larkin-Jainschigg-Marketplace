---
name: focus-group
description: Simulate a focus group of diverse LLM-reified personas to test products, messages, concepts, or designs. Use when the user wants to pre-flight an idea against representative audience reactions before real-world testing.
---

## Scientific foundation

This skill is grounded in two bodies of work.

**Persona validity — Maier et al. (2025), "LLMs Reproduce Human Purchase Intent via Semantic Similarity Elicitation of Likert Ratings"** (PyMC Labs / Colgate-Palmolive, arXiv:2510.08338): The most directly relevant paper. Tested across 57 consumer research surveys with 9,300 human responses, it establishes three key findings:

1. *How you elicit matters enormously.* Asking an LLM directly for a number ("rate this 1–5") produces pathologically narrow distributions — the model almost always outputs 3, almost never 1 or 5, yielding only 26% distributional similarity to real human panels (KS similarity = 0.26). This is an artefact of elicitation, not a fundamental LLM limitation. Free-text elicitation followed by semantic mapping to anchor statements (**Semantic Similarity Rating / SSR**) achieves KS = 0.88 and 90% of human test-retest reliability — meaning synthetic panels are almost as reliable as repeating the real survey.

2. *Demographic conditioning is necessary, but uneven.* **Age and income** replicate human response patterns well. **Gender, geographic region, and ethnicity replicate poorly** — models disagree with each other and with human data on these axes. Without any demographic conditioning, models produce realistic-looking distributions but lose nearly all ability to rank concepts against each other (correlation attainment drops to ~50%).

3. *Synthetic panels carry two genuine advantages over real ones.* LLM respondents show **less positivity bias** than human panels — they spread their ratings more widely and are more discriminating between concepts. Their **qualitative responses are richer**: real human free-text answers are typically shallow ("It's good") or repeat the stimulus; LLM synthetic consumers articulate specific reasons, surface concerns, and critique product properties in ways that inform concept development.

**Persona construction — silicon sampling** (Argyle et al., 2023; Park et al., 2024): dense demographic and psychographic profiles condition the LLM to simulate a specific person's response distribution, not a category average. Personas are individuals, not archetypes.

**Session structure** follows Krueger & Casey's five-question arc (opening → introductory → transition → key → closing), with thematic synthesis (Braun & Clarke, 2006) and moderator technique from Kolb (2008): probing, laddering, and silence to elicit depth over agreement.

**Elicitation principle (derived from Maier et al.):** Personas always speak freely in their own voice. Ratings and quantitative signals are *derived* from what they say — never directly requested. This is the mechanism that makes synthetic responses realistic.

---

## Phase 0 — Capture the stimulus and select mode

If `$ARGUMENTS` is non-empty, treat it as the stimulus and skip the intake interview. Otherwise:

Greet the user briefly:

> I'll run a simulated focus group for you. I need to know what you want to test, then I'll assemble a panel of realistic personas and run a structured discussion.

Ask for:
1. **The stimulus** — what are we testing? (product concept, tagline, UI design description, feature idea, marketing message, policy proposal — anything with a describable form)
2. **Format of the stimulus** — is it a text passage, a description of a visual, a spoken pitch? (affects how personas are asked to encounter it)
3. **Target audience** — who do you want reactions from? Give a brief description, or say "general population" or "I don't know yet."
4. **What you most want to learn** — top 1–3 questions the session should answer.

**Mode detection:** Based on the target audience answer, select the session mode before proceeding:

- **B2C mode** (default): audience is general consumers, hobbyists, patients, voters, or any individual making a personal decision. Proceed with Phase 1 below.
- **B2B mode**: audience is organizational buyers — enterprise executives, technical decision-makers, procurement leads, developers evaluating tools for team adoption, or anyone where the purchase decision involves multiple stakeholders and a formal procurement process. Skip to **Phase 1-B2B** below.

If the audience brief is ambiguous, ask: "Will the people evaluating this be making a personal decision, or will they need to get organizational buy-in — budget approval, security review, procurement sign-off?"

Confirm the stimulus, learning goals, and selected mode back to the user before proceeding.

---

## Phase 1 — Persona assembly

### 1a. Determine audience scope

If the user gave a specific audience brief, build personas that cover the plausible range within it. If they said "general population" or gave no brief, build a panel that samples across:
- age cohorts (e.g. 25–34, 45–54, 60+)
- socioeconomic range (working class through professional)
- urban/suburban/rural geography
- varied tech comfort and media consumption
- at least one persona with significant skepticism or friction toward the stimulus category

Aim for **5 personas** (4 is acceptable for narrow audiences; 6 for broad ones). An odd number avoids tie votes.

### 1b. Build each persona

For each persona, write a profile using this structure. Be specific — vague profiles produce vague responses.

```
**[First name], [age], [location]**
Occupation: [specific job title and context]
Household: [who they live with, approximate income bracket]
Education: [level and field]
Media diet: [2–3 specific sources they actually read/watch/listen to]
Relationship to [stimulus category]: [how familiar, how often they encounter it, any prior experience]
Values & worldview: [2–3 sentences — what they care about, their lens on the world]
Likely stance: [initial hypothesis — skeptic / open / enthusiast / indifferent — with brief rationale]
```

**Reliability note on demographic axes (from Maier et al.):** Age and income are the most reliably simulated dimensions — build these out with specificity and weight them heavily in persona differentiation. Gender, geographic region, and ethnicity are lower-confidence axes: the LLM may not reliably replicate real cross-group differences on these dimensions, so avoid constructing a panel where the intended insight depends primarily on a gender or regional split. If the user's brief specifically requires those axes, note the limitation to them during persona presentation.

Display all personas to the user and ask: "Does this panel look right, or should I swap anyone out?" Wait for confirmation or adjustments before proceeding to the session.

---

## Phase 2 — The focus group session

Open with a brief header:

```
─────────────────────────────────────────────
FOCUS GROUP SESSION
Stimulus: [one-line description]
Panel: [first names, ages]
Moderator: Claude
─────────────────────────────────────────────
```

Run five rounds following Krueger & Casey's arc. In each round, pose the question, then write each persona's response **in their voice** — first person, present tense, specific and grounded in their profile. Do not let personas agree blandly; probe for real variation. After each persona speaks, the moderator may briefly probe one or two of them ("Can you say more about that?" / "What would change that for you?") before moving on.

### Round 1 — Opening (warm-up, not about the stimulus)
Ask a question about their relationship to the broader category — not the stimulus itself. Goal: get them talking and establish their baseline frame of reference. Example for a food product: "How do you typically decide what to eat on a weekday evening?"

### Round 2 — Introductory (first encounter)
Present the stimulus. Describe how each persona encounters it in the format the user specified (reads it, hears a pitch, sees a screenshot description). Ask for immediate, unfiltered reactions: "What's your first impression — positive, negative, or neutral? Don't think too hard."

### Round 3 — Transition (understanding and associations)
"What does this remind you of? What kind of person do you imagine this is for?" Surfaces category placement, competitive framing, and who each persona thinks the intended audience is (which may differ from who they are).

### Round 4 — Key questions (core of the session)
Address the user's stated learning goals directly. Typically 2–3 questions from this list (adapt to their goals):
- "Would you consider trying / buying / using / sharing this? What would it take?"
- "What's the one thing you'd change or remove?"
- "Is there anything that feels unclear, untrustworthy, or off-putting?"
- "Who in your life would you tell about this, and what would you say?"
- "What's the price or cost you'd expect — and what would feel too expensive?"

Use laddering on the strongest positive and strongest negative reaction: "Why does that matter to you? And why does *that* matter?" Go 2–3 levels deep.

**Anchor mapping (SSR approximation):** After each persona has spoken freely in this round, the *moderator* — not the persona — derives an intent signal by comparing what the persona said to these five anchor statements and noting the closest match:

| Score | Anchor |
|-------|--------|
| 1 | "I'd definitely not buy / use / adopt this." |
| 2 | "I probably wouldn't buy / use / adopt this." |
| 3 | "I might — I'm genuinely undecided." |
| 4 | "I'd probably buy / use / adopt this." |
| 5 | "I'd definitely buy / use / adopt this." |

Record the score next to each persona's name silently (e.g. `[→ 2]`) — do not break the session flow or ask personas to self-rate. These scores feed the quantitative panel signal in Phase 3. The key principle from Maier et al.: the persona speaks freely; the rating is inferred from the content, not self-reported. Self-reported ratings regress to the middle.

### Round 5 — Closing (priority ranking and departing thought)
"If you could change just one thing to make this work better for you, what would it be?"
Then: "In one word or phrase — what do you think this really is?"

Close the session transcript with a separator line.

---

## Phase 3 — Synthesis

Write a synthesis report after the session transcript. Use this structure:

### Panel intent signal
Show the anchor scores from Round 4 as a simple table:

| Persona | Age | Income | Intent score (1–5) |
|---------|-----|--------|-------------------|
| [Name]  | ... | ...    | [score]           |
| ...     |     |        |                   |
| **Panel mean** | | | **[mean]** |

Interpret the mean: ≤2.0 = strong rejection; 2.1–2.9 = lean negative; 3.0 = genuinely split; 3.1–3.9 = lean positive; ≥4.0 = strong pull. Note: because these scores are derived from free-text (not self-reported), they avoid the regression-to-middle bias that direct numeric elicitation produces (Maier et al., 2025).

### Top-line verdict
One to three sentences. What is the overall signal? Lean toward a clear directional read — avoid the weasel-word hedge of "mixed results." If it *is* mixed, say why and along what fault line.

### What resonated
Bullet list (3–5 items). Claims, features, or framings that drew genuine positive response across ≥3 personas, with representative quotes.

### What created friction
Bullet list (3–5 items). Objections, confusions, or turn-offs, with representative quotes. Note whether friction is concentrated in specific persona segments or is widespread.

### Segment fault lines
If different personas split sharply, describe the fault line explicitly: "Personas with [characteristic X] responded positively; personas with [characteristic Y] did not." This is often the most actionable output.

### Suggested next moves
2–4 concrete recommendations derived from the session:
- What to double down on
- What to change or remove
- What to test next (different framing, different audience, different format)

### Caveats
Based on Maier et al. (2025), be specific:

- **What this method does well:** Free-text-derived synthetic panels achieve ~90% of human test-retest reliability and produce less positivity bias than real panels — they are more discriminating, not less. Qualitative responses are typically richer and more informative than real human free-text answers.
- **Demographics reliability:** Age and income conditioning transfers well. Gender, region, and ethnicity conditioning is unreliable — do not draw firm conclusions from cross-group comparisons along those axes.
- **Domain dependency:** The method works because LLMs have absorbed vast consumer discourse (reviews, forums, social media) for common product and service categories. For genuinely novel concepts, highly technical domains, or categories with thin online discourse, the signal quality degrades. The model cannot conjure informed opinions about things it has never encountered in training.
- **What this cannot replace:** Real purchasing behavior under budget constraints, embodied reactions to physical products, and effects of marketing exposure and shelf context. Treat this as directional signal for early-stage concept screening, not a substitute for quantitative validation studies.
- **Panel size:** This session had N=5. Directional signals are meaningful; do not over-interpret individual persona responses.

---

## Moderator principles (apply throughout, both modes)

- **No bland consensus.** If all five personas are saying roughly the same thing, inject a follow-up that surfaces the dissident view: "Is there anyone who sees this differently?"
- **Stay in character.** Never break persona voice to editorialize inside a persona turn. Save analysis for Phase 3.
- **Quota the floor.** If one persona is dominating, deliberately call on the quieter ones.
- **Name the emotion.** When a persona expresses a strong reaction, the moderator names it: "That sounds like frustration — is that right?" and invites the persona to confirm or correct.
- **Cite the profile.** Persona responses should visibly draw on their specific profile (their job, their media diet, their prior experience with the category) — not generic consumer-speak.

---

---

# B2B MODE
## Phase 1-B2B — Buying committee assembly

### Why a committee, not a panel

Enterprise software decisions are not made by individuals. The average B2B software purchase involves 6–10 stakeholders, each with partial veto power and completely different evaluation criteria. A single CIO persona is a category error — the CIO controls budget but cannot approve a tool the security team will kill, and cannot override the developers who refuse to adopt it. The committee structure models the actual decision dynamics.

**Reliability note (from Maier et al.):** For B2B personas, the most reliably conditioned dimensions are **role/title, company size, industry vertical, and tech stack** — all well-represented in LLM training data (Stack Overflow, Hacker News, Gartner Peer Insights, G2, LinkedIn, conference proceedings, technical blogs). Individual personality quirks and internal org politics are lower-confidence. Build profiles around professional role identity, not personal characteristics.

### 1-B2B-a. Committee composition

Assemble 5–6 stakeholders covering these roles. Adjust for the specific product category — a developer tool skews toward more technical voices; a data platform skews toward security and data governance:

| Role | What they care about | Veto axis |
|------|---------------------|-----------|
| **Economic Buyer** (CIO, VP Eng, or equivalent) | Strategic fit, ROI, board-level risk | Budget and strategic alignment |
| **Technical Evaluator** (Lead Architect, Principal Engineer, or Tech Lead) | Integration complexity, technical debt, DX, scalability | "This will cause us pain for years" |
| **Security/Compliance Gatekeeper** (CISO, Security Architect, or Compliance Lead) | Data residency, attack surface, certifications (SOC 2, ISO 27001, GDPR) | Hard block if not met |
| **Procurement/Commercial** (Procurement Manager or Legal) | Contract terms, vendor risk, pricing model, lock-in | Process and liability |
| **End-User Champion** (a developer, analyst, or power user who found the product and is advocating for it) | Productivity, workflow fit, community, docs | No veto power — drives the process |
| **Finance Proxy** (optional, for high-ticket items) | TCO, budget cycle timing, multi-year commit risk | Cost justification |

If the stimulus is developer tooling specifically, replace the End-User Champion with a second technical voice (e.g. a skeptical senior developer who didn't initiate the evaluation and has seen too many tools fail).

### 1-B2B-b. Build each committee member

```
**[First name], [title], [company size / industry vertical]**
Stack & environment: [what they're currently running — key tools, cloud provider, languages]
Current pain: [the specific problem this evaluation is meant to solve, from their perspective]
What they're measured on: [their internal KPIs — uptime, security incidents, delivery velocity, cost reduction]
Prior relevant experience: [tools they've evaluated or adopted before in this category; scars they carry]
Vendor relationships / lock-in: [existing contracts that complicate a switch]
Likely posture: [champion / skeptic / gatekeeper / indifferent — with rationale]
Kill-shot risk: [the single concern most likely to make them block the deal]
```

Display the committee to the user and ask: "Does this buying committee look right for your target customer? Anyone to swap, add, or adjust?" Wait for confirmation before proceeding.

---

## Phase 2-B2B — The evaluation session

This is not a focus group. It is a moderated **internal evaluation meeting** — the kind that happens 3–4 weeks after a vendor demo, when the committee reconvenes to decide whether to proceed to a POC, expand a pilot, or kill the evaluation. The product has already been seen; now stakeholders are voicing their real assessments.

Open with a header:

```
─────────────────────────────────────────────
BUYING COMMITTEE EVALUATION
Product: [one-line description]
Committee: [titles and first names]
Stage: Post-demo internal review
Moderator: Claude (as meeting facilitator)
─────────────────────────────────────────────
```

### Round 1 — Context setting (current state and motivation)
Before anyone reacts to the product, establish where each stakeholder is coming from. Facilitator asks: "Before we get into the evaluation, can everyone quickly say — what problem were we hoping this would solve, and how painful is that problem right now?"

Each stakeholder answers in their voice, from their role perspective. This surfaces whether the committee even agrees on what problem they're solving — often they don't, and that tension is important signal.

### Round 2 — First impressions post-demo
"Having seen the pitch/demo/concept — what's your initial read? Positive, negative, or open questions?"

Each stakeholder reacts in character. The End-User Champion should be enthusiastic but specific; the Security Gatekeeper should immediately flag data questions; the Technical Evaluator should probe integration; the Economic Buyer should be reserved until they hear from the others.

### Round 3 — Deep evaluation by role
Each stakeholder gets a targeted question matched to their evaluation axis:

- **Economic Buyer:** "Does this move a metric you care about, and can you explain the ROI case to the CFO?"
- **Technical Evaluator:** "Walk us through the integration story — what would it actually take to deploy this in our environment?"
- **Security Gatekeeper:** "What's the security posture? What questions would you need answered before you could sign off?"
- **Procurement:** "What's the commercial model — and what are the contract risks we should know about?"
- **End-User Champion:** "You brought this to us — what's the strongest case for moving forward, and what are you glossing over?"
- **Finance Proxy (if present):** "What does the three-year TCO look like when you include implementation, training, and migration?"

After each stakeholder speaks, the facilitator may prompt one other member to respond: "Does anyone have a reaction to what [name] just said?"

### Round 4 — Key questions and anchor mapping

Pose 2–3 of these based on the user's stated learning goals:
- "What would you need to see in a POC to move forward with confidence?"
- "What's the one thing about this that's genuinely differentiated — that we can't get from [incumbent / cheaper alternative]?"
- "What happens to this evaluation if [key concern] isn't resolved in 30 days?"
- "Who in this room would have to go to bat for this at the executive level — and are they willing to?"
- "If this deal dies, what kills it — price, security, integration, internal politics, or something else?"
- "What's the competitive alternative you'd go with if this doesn't work out?"

**B2B anchor mapping:** After each stakeholder has spoken in this round, the moderator silently derives their advocacy signal by comparing what they said to these anchors:

| Score | Anchor |
|-------|--------|
| 1 | "I'd recommend against this — it won't clear our review process." |
| 2 | "I have blocking concerns. I can't support moving forward until they're resolved." |
| 3 | "I'm open but not convinced. I'd want a POC or more answers before committing." |
| 4 | "I'm inclined to move forward — I'd support a pilot or next-stage conversation." |
| 5 | "I'd actively champion this internally and put my credibility behind it." |

Record silently as `[→ 3]` next to each stakeholder's name. Do not ask them to self-rate.

### Round 5 — The kill-shot and the path forward
Two closing questions, answered by each committee member:

1. "What's the one thing that could still kill this deal — even if everything else checks out?"
2. "If we decided to move forward tomorrow, what would the next concrete step be?"

The gap between these two answers (what kills it vs. what the next step would be) is often the most actionable output of the entire session.

Close with a separator line.

---

## Phase 3-B2B — Synthesis

### Committee advocacy signal

| Stakeholder | Role | Advocacy score (1–5) | Veto power? |
|-------------|------|----------------------|-------------|
| [Name] | [Title] | [score] | [Yes / No] |
| ... | | | |
| **Mean (non-veto)** | | **[mean]** | |
| **Veto holders** | | **[their scores]** | Yes |

**Veto logic:** A mean score of 4.2 is irrelevant if the CISO scores 1. Note explicitly if any veto-power stakeholder scored ≤2 — that is the deal outcome regardless of the panel mean.

Score interpretation: ≤2.0 = likely dead; 2.1–2.9 = high-friction path forward; 3.0–3.4 = conditional on POC/answers; 3.5–4.0 = positive momentum; ≥4.0 = strong buy signal.

### Champion and blocker map
Who would actively push this forward internally, and who would slow or kill it? Be specific about which concerns are blockers (will stop the deal) vs. friction (will slow it but can be overcome).

### Most likely deal-killer
The single concern most likely to terminate this evaluation, based on the session. Name it precisely — "data residency for EU customers not confirmed," not "security concerns."

### What would need to be true
3–5 specific conditions that, if met, would move this committee from their current position to a close. These are the vendor's actual to-do list:
- What questions need written answers (security questionnaire, compliance certs)
- What needs to be demonstrated in a POC
- What commercial terms need adjusting
- What internal politics the champion needs to navigate

### Segment fault lines
Where the committee diverged sharply — e.g. "technical evaluators see this as a 10x improvement; security will block on SOC 2 gap." This is often where the vendor needs to focus.

### Suggested next moves
2–4 concrete recommendations for the user:
- What to fix in the product or pitch to address the blocking concern
- What proof points (certifications, case studies, integrations) are missing
- Which stakeholder role to target more directly in the next conversation
- Whether to proceed, pivot, or abandon this segment

### Caveats (B2B-specific)
- **What simulates well:** Role-based concerns, standard evaluation criteria, common objection patterns for this product category — all well-represented in LLM training data via enterprise tech discourse.
- **What simulates poorly:** Internal org politics specific to a company, existing vendor relationships and lock-in dynamics, individual personalities, budget cycle timing, and the specific history between a vendor and a prospect.
- **The committee is stylized:** Real buying committees have more dysfunction, more silence, and more decisions made in side conversations outside the meeting. This session surfaces the concerns; it doesn't model the political process for resolving them.
- **Domain coverage:** Developer tooling, cloud infrastructure, data platforms, and enterprise SaaS have excellent LLM training coverage. Highly specialized verticals (defense, nuclear, rare industrial equipment) have thinner coverage — treat those results with more caution.
