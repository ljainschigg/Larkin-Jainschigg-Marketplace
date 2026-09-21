---
hide:
  - navigation
---

# Larkin J.'s Marketplace

Twenty-four Claude Code plugins — executive intelligence, research, content, and the
tools to build your own. Add the marketplace once, then install what you need.

```
/plugin marketplace add ljainschigg/Larkin-Jainschigg-Marketplace
```

[Browse the plugins](#the-plugins){ .md-button .md-button--primary }
[Build your own](contributing/build-and-submit.md){ .md-button }

---

## The plugins

### :material-target: Executive intelligence

<div class="grid cards" markdown>

-   :material-radar:{ .lg .middle } **discourse-tracker**

    ---

    Tracks what the AI industry is talking about right now and keeps a
    summary on hand, so your writing and research stay current.

    [:material-arrow-right: Read more](skills/discourse-tracker.md)

-   :material-slack:{ .lg .middle } **talk-to-slack**

    ---

    Reads a Slack channel and writes up what your team is working on — or
    briefs you on one colleague before a meeting with them.

    [:material-arrow-right: Read more](skills/talk-to-slack.md)

-   :material-lightbulb-on:{ .lg .middle } **exec-content-mine**

    ---

    Reads an interview transcript and pulls out article ideas and quotable
    moments, shaped around how your organization talks about itself.

    [:material-arrow-right: Read more](skills/exec-content-mine.md)

</div>

### :material-scale-balance: Investor relations & research

<div class="grid cards" markdown>

-   :material-scale-balance:{ .lg .middle } **ir-copy-check**

    ---

    Checks marketing copy against your investor-relations guidance and latest
    financial filing, flagging anything that claims more than you have
    publicly disclosed.

    [:material-arrow-right: Read more](skills/ir-copy-check.md)

-   :material-account-group:{ .lg .middle } **focus-group**

    ---

    Runs a focus group with simulated participants built from published
    audience research, so you can test a product or message early.

    [:material-arrow-right: Read more](skills/focus-group.md)

</div>

### :material-file-document-edit: Content & documents

<div class="grid cards" markdown>

-   :material-file-document-edit:{ .lg .middle } **seo-claude-plugin**

    ---

    Writes a search-optimized article from your brief, researching sources
    and citing them as it drafts and edits.

    [:material-arrow-right: Read more](skills/seo-claude-plugin.md)

-   :material-closed-caption:{ .lg .middle } **subtitle-studio**

    ---

    Turns video and audio into subtitles and transcripts on your own machine.
    Nothing is uploaded, and no API key is required.

    [:material-arrow-right: Read more](skills/subtitle-studio.md)

-   :material-broom:{ .lg .middle } **markdown-doc-cleaner**

    ---

    Turns rough notes into a clean, well-organized document, tidying the
    structure and formatting without adding anything you did not write.

    [:material-arrow-right: Read more](skills/markdown-doc-cleaner.md)

-   :material-link-variant:{ .lg .middle } **linkcheck**

    ---

    Checks a documentation site for broken links and gives you a report of
    what needs fixing.

    [:material-arrow-right: Read more](skills/linkcheck.md)

</div>

### :material-book-search: Knowledge & research

<div class="grid cards" markdown>

-   :material-book-search:{ .lg .middle } **researcher**

    ---

    Finds, reads, and summarizes real sources on a topic — and knows when to
    move on from a paywalled or dead page instead of retrying it.

    [:material-arrow-right: Read more](skills/researcher.md)

-   :material-file-tree:{ .lg .middle } **karpathy-kb**

    ---

    Turns transcripts, documents, and notes into a searchable knowledge base
    where every fact records who said it, where, and when.

    [:material-arrow-right: Read more](skills/karpathy-kb.md)

-   :material-file-pdf-box:{ .lg .middle } **get-pdfs**

    ---

    Downloads reports and whitepapers from sites that put them behind a
    sign-up form, filling in the form for you.

    [:material-arrow-right: Read more](skills/get-pdfs.md)

</div>

### :material-heart-pulse: Personal

<div class="grid cards" markdown>

-   :material-heart-pulse:{ .lg .middle } **diet**

    ---

    Tracks what you eat and your health readings against targets you set.
    Describe meals in plain language — no weighing or calorie lookups.

    [:material-arrow-right: Read more](skills/diet.md)

-   :material-checkbox-marked-outline:{ .lg .middle } **smart-todo**

    ---

    A to-do list you talk to. Paste in messy notes to capture tasks, then ask
    what you should work on next.

    [:material-arrow-right: Read more](skills/smart-todo.md)

-   :material-key-variant:{ .lg .middle } **secret-resolver**

    ---

    Keeps API keys and passwords for your other plugins in your system
    keychain, so no plugin ever holds your credentials itself.

    [:material-arrow-right: Read more](skills/secret-resolver.md)

</div>

---

## Build a plugin

Fully-validated tools that encode the standards a curator applies, so you can
catch problems before you open a pull request.

<div class="grid cards" markdown>

-   :material-hammer-wrench:{ .lg .middle } **plugin-scaffold**

    ---

    Describe the plugin you want, and it generates a correctly structured
    starting point for you to build on.

    [:material-arrow-right: Read more](skills/plugin-dev-tools/plugin-scaffold.md)

-   :material-shield-check:{ .lg .middle } **plugin-security-check**

    ---

    Inspects a plugin for security problems, risky permissions, and
    documentation gaps before you publish it.

    [:material-arrow-right: Read more](skills/plugin-dev-tools/plugin-security-check.md)

-   :material-spellcheck:{ .lg .middle } **plugin-docs-lint**

    ---

    Checks that a plugin's README meets this marketplace's documentation
    standards, and tells you what is missing.

    [:material-arrow-right: Read more](skills/plugin-dev-tools/plugin-docs-lint.md)

-   :material-file-compare:{ .lg .middle } **plugin-diff**

    ---

    Explains in plain language what changed between two versions of a
    plugin, so you know what you are upgrading to.

    [:material-arrow-right: Read more](skills/plugin-dev-tools/plugin-diff.md)

-   :material-source-pull:{ .lg .middle } **submit-plugin**

    ---

    Submits your finished plugin: runs the security check, then opens the
    pull request for you.

    [:material-arrow-right: Read more](skills/plugin-dev-tools/submit-plugin.md)

-   :material-clipboard-check:{ .lg .middle } **validate-marketplace**

    ---

    Checks every plugin in a marketplace at once and reports which ones fall
    short of the standards.

    [:material-arrow-right: Read more](skills/plugin-dev-tools/validate-marketplace.md)

</div>

Starting points you can copy: [example-skill](skills/example-skill.md) (the
minimum viable plugin), [example-mcp-python-skill](skills/example-mcp-python-skill.md),
and [example-mcp-node-skill](skills/example-mcp-node-skill.md) (skills backed by
an MCP server).

---

## Getting started

**Plugin** — the installable package. It is what you install with `/plugin install`,
and it can contain one or more skills, an MCP server, configuration, and docs.

**Skill** — an individual `/command` inside a plugin. Typing `/example-skill`
invokes a skill. Many plugins contain exactly one skill with the same name as
the plugin; more capable ones bundle several.

You need **Claude Code** installed and running. Then:

```
/plugin marketplace add ljainschigg/Larkin-Jainschigg-Marketplace
/plugin install <plugin-name>@Larkin-Jainschigg-Marketplace
```

You only need to add the marketplace once. To see what is available, run
`/plugin list`; to pick up new and updated plugins later, run
`/plugin marketplace update Larkin-Jainschigg-Marketplace` and reinstall the ones you want.

### Do you need to authenticate?

Adding the marketplace and installing plugins both `git clone` the
`ljainschigg/Larkin-Jainschigg-Marketplace` repository. Whether you need to set
up authentication depends on whether that repository is **public** or **private**.

=== "Public repository"

    If the marketplace repository is public, there is **nothing to set up**.
    `/plugin marketplace add` and `/plugin install` work with no authentication.

=== "Private repository"

    If the marketplace repository is private (for example, an internal fork),
    you need two things:

    1. **Read access** to `ljainschigg/Larkin-Jainschigg-Marketplace`
       (ask a maintainer to add you).
    2. **Git configured to authenticate to GitHub.** Claude Code runs git
       non-interactively, so without configured credentials the clone fails with
       `could not read Username`.

    Set up authentication **once**, using whichever method matches how you already
    use GitHub:

    === "HTTPS (recommended for most people)"

        The simplest path. Install the [GitHub CLI](https://cli.github.com), then
        run these in a terminal (**not** inside Claude Code):

        ```
        gh auth login       # choose: GitHub.com → HTTPS → log in via browser
        gh auth setup-git   # teaches git to authenticate as you
        ```

        That's it — no SSH keys to generate.

    === "SSH (if you already use SSH keys with GitHub)"

        If you already clone GitHub repos over SSH, add one line so git routes the
        marketplace's HTTPS clone URLs over your existing SSH key:

        ```
        git config --global url."git@github.com:".insteadOf "https://github.com/"
        ```

        This requires an SSH key already registered with GitHub and loaded in your
        `ssh-agent`.

!!! tip "Keeping it working"

    Read access is enough for everything on this page — you never need write
    access to install or use plugins. If a background auto-update of the
    marketplace ever fails on a private repo, just run
    `/plugin marketplace update Larkin-Jainschigg-Marketplace` manually, or set
    `CLAUDE_CODE_PLUGIN_KEEP_MARKETPLACE_ON_FAILURE=1` in your environment.

---

## Contribute a plugin

Built something useful? The more we share, the less we each have to reinvent.
The **[Build & submit a plugin guide](contributing/build-and-submit.md)** walks
the whole path — scaffold, build, verify, security-check, and open a PR with
`/submit-plugin`.
