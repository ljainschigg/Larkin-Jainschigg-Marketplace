# Step 09: Edit Article — Uniform Voice

ACTION: Read `${CLAUDE_PLUGIN_ROOT}/skills/seo-claude-plugin/system/WRITING-RULES.md` to reactivate the full rule set.

ACTION: Read `{project-dir}/outputs/{project-name}-article.md` from beginning to end and apply the following edits:

**Rule-of-three patterns — eliminate all instances:**
- Successive sections each containing exactly three bullets: vary bullet counts deliberately across the whole article. No reader scanning the article should perceive a repeating visual pattern. Sections may have 3–5 bullets; the distribution should feel deliberately uneven — some sections gain bullets, some lose them.
- Rule-of-three phrasing (e.g., "This approach eliminates excess costs, reduces time spent, and limits risks."): rewrite to break the tricolon. Add a fourth element, split into two sentences, or restructure the thought.

**Voice and authority — for each section:**
- Ensure the prose reads as authoritative advice from a technology and business practitioner to peers.
- Rewrite any passages that read as notes to the writer, placeholder text, or passive summaries lacking a point of view.
- Ensure the brand perspective is present but not forced — it should emerge from the argument, not appear as a bolted-on promotional paragraph.

**Writing rules compliance — scan and fix:**
- No em-dashes in body copy (use parentheses or restructure)
- No boldface for emphasis in running prose (boldface is only for bullet head-end phrases)
- All bullet lists formatted without blank lines between bullets
- All `<!-- UNSUPPORTED ASSERTION -->` comments surfaced to the user for resolution

ACTION: Save the final article file.

ACTION: Inform the user that the workflow is complete. Present a brief summary: word count, number of H2 sections, number of external sources cited, and any remaining `<!-- UNSUPPORTED ASSERTION -->` items needing attention. STOP.
