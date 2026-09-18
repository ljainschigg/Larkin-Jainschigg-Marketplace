# Step 08: Edit Article — Support Assertions

ACTION: Open `{project-dir}/outputs/{project-name}-article.md`.

ACTION: Read the article from beginning to end. For each asserted fact, and particularly for any quantitative assertion or statistic:

  ACTION: Search for support in:
  - `{project-dir}/candidate-links.md` — for the public URL of each resource
  - `{project-dir}/resources/*.txt` — for the text content to verify the claim

  ACTION: Attribute the fact in the article and link to its source:
  - **First appearance of a source**: link with a full attribution sentence naming the publisher and document, e.g.:
    `[Example Analyst Group's 2025 State of Workflow Automation Report](https://...) found that 85% of organizations...`
  - **Subsequent appearances of the same source**: reference without re-linking, e.g.:
    `As Example Analyst Group notes, 99% of respondents...`
  - **Unsupported claims**: insert an inline comment and do not fabricate a source:
    `<!-- UNSUPPORTED ASSERTION: "[exact claim text]" — verify and source before publishing -->`

ACTION: Verify that all links specified in `article_outline.sections[*].links_in_section` have been placed in their designated sections. Insert any that are missing, using the specified anchor text.

ACTION: Save the updated article file.

ACTION: Inform the user that the assertions-support edit is complete and STOP. Await further instructions.
