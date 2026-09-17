# Step 02: Gather the Brief

ACTION: Read and understand the working schema at:
`${CLAUDE_PLUGIN_ROOT}/skills/seo-claude-plugin/system/base-article-data.json`

Each field's `_intent` (where present) explains what it holds. You will copy this file and populate it from the user's brief.

ACTION: Ask the user for a short project name to use for naming output files — retain as `project-name`.

ACTION: Ask the user to provide their **article brief**. Accept either form:
- a path to a filled brief file (the template is at `${CLAUDE_PLUGIN_ROOT}/skills/seo-claude-plugin/system/brief-template.md`) — read it, or
- the brief pasted directly into the conversation, or gathered interactively.

At minimum, collect: **title**, **description**, **target terms to include**, **links to include**, and a **proposed outline** (the H2 sections, with any per-section instructions). Everything else is optional and can be derived.

IF the user cannot supply at least a title, a description, and a proposed outline (H2 sections):
  STOP and explain what is still needed, pointing them at the brief template.
ELSE:
  ACTION: Create `{project-dir}/article-data.json` as a copy of base-article-data.json, then populate it from the brief:
  - `title`, `description` — as given.
  - `target_terms` — the terms/phrases to target (preserve multi-word phrases).
  - `links_to_include` — each as `{ anchor_text, url, note }`; carry any of these into the relevant section's `links_in_section` where the user indicated placement.
  - `reference_links` — any benchmark/competitor URLs to learn from.
  - `article_outline.h1_title` — the H1 (default to `title` if not separately given).
  - `article_outline.introduction` — any intro instructions / pre-written final sentence.
  - `article_outline.sections[]` — one per H2, with `h2_heading`, `instructions`, and any `h3_headings`, `pre_written_content`, `format_requirements`.
  - `recommended_word_count`, `key_highlights`, `notes` — if provided.
  - Leave the SEO fields (`meta_title`, `meta_description`, `url_slug`) blank if not supplied; note that you will help derive them.

ACTION: If `meta_title`, `meta_description`, or `url_slug` are blank, propose values derived from the title, description, and target terms, and ask the user to confirm or edit. Write the confirmed values into `article-data.json`.

ACTION: Inform the user that the brief is captured and STOP. Please await further instructions.
