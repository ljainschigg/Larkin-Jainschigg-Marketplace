# Step 06: Draft Article — Outline and Stats

ACTION: If your context is lengthy, summarize it now.

ACTION: Confirm that `project-dir` and `project-name` are in context. If either is missing, ask the user.

ACTION: Confirm that `{project-dir}/resources/` contains retrieved text files. If the folder is empty, STOP and ask the user to confirm research is complete.

ACTION: Read `{project-dir}/article-data.json`, including the brand perspective stored in `brand_perspective`.

ACTION: Read `{project-dir}/topic-direction-goal.md`.

NOTE: If `references-dir` is set, read any relevant files there now to supplement the researched material with your reference product knowledge.

ACTION: Read all `.txt` files in `{project-dir}/resources/` to absorb the researched information.

ACTION: Annotate the outline in `article-data.json` section by section (H2 by H2) with notes describing a good plan for the narrative arc. Consider: how the brand perspective threads through the piece; where the strongest statistics land; where internal links should appear; how the article builds toward its conclusion.

ACTION: Working from `{project-dir}/candidate-links.md` and `article-data.json` in parallel:
  For each link in candidate-links.md:
    ACTION: Read the associated `.txt` file in `{project-dir}/resources/`, scanning for main assertions and quantitative statistics.
    ACTION: Determine which H2 section this resource is most relevant to, based on how well its facts support the argument planned for that section.
    ACTION: Note the most relevant facts or stats in `article-data.json` within the data structure for that section.
    NOTE:
      - Match each resource to the section where it best supports the argument.
      - Do not allocate a resource to more than one section unless there is a compelling reason.
      - Allocate resources to the most important sections first.

ACTION: When all resources are allocated and `article-data.json` is updated with narrative arc notes and resource allocations, inform the user and STOP. Await further instructions.
