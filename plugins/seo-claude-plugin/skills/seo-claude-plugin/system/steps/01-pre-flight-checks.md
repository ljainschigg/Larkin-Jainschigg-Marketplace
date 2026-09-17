# Step 01: Pre-flight Checks

## Verify prerequisites

ACTION: This workflow invokes the `researcher` plugin and may clone documentation repositories the user asks for. Before anything else, verify the runtime prerequisites and stop with clear guidance if any is missing:

- Run `git --version`. If `git` is not found, stop and tell the user to install Git (https://git-scm.com) before continuing — the optional repo-cloning step below depends on it.
- Confirm the `researcher` plugin is installed (this workflow calls `/research`). If it is not available, tell the user to install it with `/plugin install researcher@claude-plugins` and run its `/setup`.

Do not proceed past a missing prerequisite.

## Establish project directory

ACTION: Run `pwd` and retain the result as `project-dir`. This directory is the project root — all article data, research output, and the finished article will be written here.

ACTION: Create the following subdirectories inside `project-dir` if they do not already exist:
- `{project-dir}/resources/` — research resources written by the researcher plugin
- `{project-dir}/outputs/` — finished article and other deliverables

ACTION: `project-dir` may be a git repository. Ensure a `{project-dir}/.gitignore` exists and lists the working/data paths this workflow writes — `resources/`, `outputs/`, and `references/` (the last holds **the user's reference material and any cloned documentation repos**, which must never be committed into the user's project). Create the `.gitignore` or append any missing lines. Never `git add`/commit these — they are the user's gathered material and third-party repos, not deliverables to publish.

## Reference materials (optional, user-supplied)

NOTE: Brand facts, product knowledge, positioning, and reference documentation are **the user's own instance data** — nothing is bundled with the plugin. A reusable template for capturing this is at `${CLAUDE_PLUGIN_ROOT}/skills/seo-claude-plugin/system/brand-profile-template.md`.

ACTION: Ask the user whether they have a **brand profile** (a filled copy of the template above, or equivalent notes on their organization, products, positioning, competitors, and preferred sources). If yes, retain its path as `brand-profile-path` and read it now. If no, mention the template exists and that they can fill it later for better results; proceed without it.

ACTION: Ask the user whether they have a local **reference-materials directory** — a folder of canonical reference documents such as whitepapers, deep dives, product overviews, or clones of documentation repositories. If yes, retain its path as `references-dir`. If no, and they want one, create a `references/` directory inside `project-dir` and retain its path as `references-dir`.

ACTION: Ask the user which products, offerings, or subjects you will be writing about.

ACTION: IF `brand-profile-path` lists documentation repositories to clone AND `references-dir` is set: tell the user which repos are listed, and request permission to use their authentication to clone the relevant ones into `references-dir`. Depending on their answer, clone the repos using their authentication, reporting and resolving any difficulties before proceeding. The contents of these repos (often under each repo's `/docs` tree) provide detailed product information for writing. Skip this action entirely if no repos are listed or the user declines.

## Product knowledge check (do not skip)

ACTION: Assess what product knowledge is actually available for the subjects the user named. It is sufficient if EITHER:
- `brand-profile-path` is set and its "Products / offerings" section covers those subjects, OR
- `references-dir` is set and contains relevant product documentation (docs, whitepapers, deep dives, or cloned repos).

IF neither is true:
  ACTION: Warn the user plainly, before proceeding: with no brand profile and no reference documents, you know their products only from this conversation, from general knowledge, and from web research. Any product-specific claim (capabilities, differentiators, naming, positioning) may therefore be inaccurate or invented, and the article's factual assertions about their products will be unreliable. This is the single biggest quality risk for the piece.
  ACTION: Offer the user a choice and act on their answer:
    a. **Point you at instance data now (preferred)** — a brand profile (`brand-profile-template.md` shows the shape) or a directory of product reference docs. If they provide one, set `brand-profile-path` and/or `references-dir` accordingly and read it.
    b. **Give you a few key product facts inline** — names, a one-line description each, and the differentiators that matter. If `references-dir` is not set, create `{project-dir}/references/` and retain it as `references-dir`. Write the facts to `{references-dir}/product-facts.md`, one product per section (name, description, differentiators). Later steps read `references-dir`, so these facts will inform the outline and drafting.
    c. **Proceed anyway** — accepting that product-specific claims will need careful human verification before publishing. If they choose this, carry the limitation forward: in step 08, treat product-specific claims with the same scrutiny as unsupported statistics and flag each with an `<!-- UNSUPPORTED ASSERTION -->` comment for the user to verify.

  Do not silently proceed without product knowledge — make the choice explicit.

## Credentials note

NOTE: Credentials used for filling gated PDF forms during research are stored by the researcher plugin at `${CLAUDE_PLUGIN_DATA}/config/` or `~/.claude/plugins/data/researcher-claude-plugins/.env`. The researcher plugin manages these — run `/setup` within the researcher plugin if credentials have not been configured.

ACTION: Inform the user that pre-flight checks are complete and STOP. Please await further instructions.
