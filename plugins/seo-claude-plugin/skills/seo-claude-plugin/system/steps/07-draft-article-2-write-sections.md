# Step 07: Draft Article — Write Sections

NOTE: Write as a trustworthy, highly-technical business leader educating peers: credible, non-writerly, non-marketing-y, well-structured, and supported by online resources.

ACTION: Read `${CLAUDE_PLUGIN_ROOT}/skills/seo-claude-plugin/system/WRITING-RULES.md` and keep these rules active throughout drafting.

ACTION: Note the total word count required from `recommended_word_count` in `{project-dir}/article-data.json`.

ACTION: Create `{project-dir}/outputs/{project-name}-article.md` and write:
1. The article title as a `#` (H1) heading, drawn from `article_outline.h1_title`
2. On the next line, a bare `##` as a placeholder for the dek (subheadline), to be composed later

ACTION: For each H2 section in `article_outline.sections`:
  ACTION: Read all notes and instructions for this section from `article-data.json` (including `instructions`, `h3_headings`, `pre_written_content`, `format_requirements`, and any narrative arc notes from step 06).
  ACTION: Consider which target keywords are likely to appear naturally in this section.
  ACTION: Read the `.txt` resource file allocated to this section in step 06. Use its facts and statistics to substantiate the argument.
  NOTE: If `references-dir` is set and relevant product context applies to this section, draw on it here to strengthen positioning.
  ACTION: Insert the H2 heading with `##` on a new line.
  ACTION: Write the section text following the section instructions. Link supporting resources naturally in body copy. Follow WRITING-RULES.md throughout — no em-dashes, no boldface for emphasis, rule-of-three avoidance, proper bullet formatting.
  ACTION: If `pre_written_content` is specified for this section, include it exactly as given.

ACTION: Inform the user that the draft is complete and STOP. Await further instructions.
