# Step 03: Brand Perspective

NOTE: If `brand-profile-path` is set, read it now. If `references-dir` is set, read any files there relevant to the article topic before asking the user — the context will improve the quality of the discussion.

ACTION: Establish the **brand perspective** on this topic: the organization's positioning, key differentiators, and how its products or services relate to the article subject matter.
- If the brand profile and reference materials already make this clear, draft a proposed perspective from them and ask the user to confirm or adjust.
- Otherwise, ask the user for it directly.

ACTION: Summarize the brand perspective into a concise summary and key points. Add or update the `brand_perspective` field in `{project-dir}/article-data.json` with:
- `summary` (string): a concise paragraph summarizing the organization's position on this topic
- `key_points` (array of strings): 4–6 bullet points capturing the main differentiators

ACTION: Inform the user that the brand perspective step is complete and STOP. Please await further instructions.
