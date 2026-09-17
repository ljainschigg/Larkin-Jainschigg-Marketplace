# Step 04: Topic, Direction, and Goal for Research

ACTION: Reread `{project-dir}/article-data.json` to refresh context on the article topic, structure, and the brand perspective.

ACTION: Derive the three research parameters automatically from the article data:

1. **Topic** — derive from `meta_title`, `article_outline.h1_title`, and `target_terms`. Should be broad enough to find authoritative resources, specific enough to stay on-topic.

2. **Direction** — derive from the H2 headings (which aspects need research support) and `brand_perspective.key_points` (which angles to substantiate). Apply standard source constraints:
   - Recency: Before researching, acknowledge today's date and use it to define the search window.
      For fast-moving topic areas (e.g., AI), prioritize sources published within the last 6 months of today's date—especially for quantitative statistics, market size, spending projections, adoption rates, investment, forecasts, and competitive data.
      If no suitable sources exist, expand to the last 12 months and explicitly note the exception. Prefer the most recent authoritative evidence available.
   - Authority: major media, analyst firms (Gartner, Forrester, IDC), official standards bodies, government sources.
   - Competitive exclusions and preferences: apply the lists from the user's brand profile (`brand-profile-path`), if set:
     - **Exclude** sources from the competitors and categories the brand profile lists under "Competitors to exclude from research" — unless the research's purpose is to investigate one of those companies specifically at the user's request.
     - **Prefer** sources from the partners/organizations the brand profile lists under "Partners / sources to prefer."
     - If no brand profile is set, ask the user whether there are any sources they want excluded or preferred, and apply their answer.

3. **Goal** — derive from `brand_perspective.summary` and `brand_perspective.key_points`. Frame as what the research should indirectly demonstrate in support of the brand's position.

ACTION: Present the derived topic, direction, and goal to the user in a concise summary. Ask: "Does this research brief look right? Correct anything before I proceed." Apply any corrections the user provides.

ACTION: Write `{project-dir}/topic-direction-goal.md` recording the final topic, direction, and goal.

ACTION: Continue immediately to step 05 — do not STOP.
