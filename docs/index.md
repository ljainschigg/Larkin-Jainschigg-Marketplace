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

    Keeps a running snapshot of current AI discourse on disk, so other skills
    draw on what is happening now rather than stale training data.

    [:material-arrow-right: Read more](skills/discourse-tracker.md)

-   :material-slack:{ .lg .middle } **talk-to-slack**

    ---

    Turns a channel's activity into a collaboration report, or reconstructs a
    per-person briefing before you walk into a meeting.

    [:material-arrow-right: Read more](skills/talk-to-slack.md)

-   :material-lightbulb-on:{ .lg .middle } **exec-content-mine**

    ---

    Mines an executive or SME interview transcript for article ideas and
    quotable clip moments, tuned to your organization's positioning.

    [:material-arrow-right: Read more](skills/exec-content-mine.md)

</div>

### :material-scale-balance: Investor relations & research

<div class="grid cards" markdown>

-   :material-scale-balance:{ .lg .middle } **ir-copy-check**

    ---

    Critiques or rewrites outward-facing copy against your IR guidance and
    your latest filing, so marketing language stays inside what you disclosed.

    [:material-arrow-right: Read more](skills/ir-copy-check.md)

-   :material-account-group:{ .lg .middle } **focus-group**

    ---

    Runs a simulated focus group of researched personas to pressure-test
    products, messaging, and positioning before you commit.

    [:material-arrow-right: Read more](skills/focus-group.md)

</div>

### :material-file-document-edit: Content & documents

<div class="grid cards" markdown>

-   :material-file-document-edit:{ .lg .middle } **seo-claude-plugin**

    ---

    Takes a structured brief through research, drafting, and editing to a
    complete, source-backed article.

    [:material-arrow-right: Read more](skills/seo-claude-plugin.md)

-   :material-closed-caption:{ .lg .middle } **subtitle-studio**

    ---

    Transcribes video and audio to subtitles entirely on your machine with
    Whisper — no upload, no API key.

    [:material-arrow-right: Read more](skills/subtitle-studio.md)

-   :material-broom:{ .lg .middle } **markdown-doc-cleaner**

    ---

    Turns rough notes into a clean, well-structured Markdown document without
    inventing content that was not there.

    [:material-arrow-right: Read more](skills/markdown-doc-cleaner.md)

-   :material-link-variant:{ .lg .middle } **linkcheck**

    ---

    Scans a versioned MkDocs site for broken links and writes a report you can
    act on.

    [:material-arrow-right: Read more](skills/linkcheck.md)

</div>

### :material-book-search: Knowledge & research

<div class="grid cards" markdown>

-   :material-book-search:{ .lg .middle } **researcher**

    ---

    Discovers, fetches, and synthesizes real sources — with retrieval rules
    that stop it thrashing on gated or dead pages.

    [:material-arrow-right: Read more](skills/researcher.md)

-   :material-file-tree:{ .lg .middle } **karpathy-kb**

    ---

    Builds a citation-tracked knowledge base where every claim carries full
    provenance: who said it, in what document, on what date.

    [:material-arrow-right: Read more](skills/karpathy-kb.md)

-   :material-file-pdf-box:{ .lg .middle } **get-pdfs**

    ---

    Retrieves PDFs from gated lead-gen landing pages, handling the access
    forms that normally stop automation.

    [:material-arrow-right: Read more](skills/get-pdfs.md)

</div>

### :material-heart-pulse: Personal

<div class="grid cards" markdown>

-   :material-heart-pulse:{ .lg .middle } **diet**

    ---

    Tracks food and biometrics against your own targets, with loose logging
    and optional device sync. Ships no one's numbers but yours.

    [:material-arrow-right: Read more](skills/diet.md)

-   :material-checkbox-marked-outline:{ .lg .middle } **smart-todo**

    ---

    Conversational to-do list: paste freeform text to capture tasks, then ask
    what to do next.

    [:material-arrow-right: Read more](skills/smart-todo.md)

-   :material-key-variant:{ .lg .middle } **secret-resolver**

    ---

    Provider-agnostic secret broker so plugins never hold your credentials —
    keyring, `pass`, or file, your choice.

    [:material-arrow-right: Read more](skills/secret-resolver.md)

</div>

---

## Build a plugin

Fully-validated tools that encode the standards a curator applies, so you can
catch problems before you open a pull request.

<div class="grid cards" markdown>

-   :material-hammer-wrench:{ .lg .middle } **plugin-scaffold**

    ---

    Generates a correctly structured plugin directory from a description.

    [:material-arrow-right: Read more](skills/plugin-dev-tools/plugin-scaffold.md)

-   :material-shield-check:{ .lg .middle } **plugin-security-check**

    ---

    Deep inspection: compliance, security, blast radius, documentation quality.

    [:material-arrow-right: Read more](skills/plugin-dev-tools/plugin-security-check.md)

-   :material-spellcheck:{ .lg .middle } **plugin-docs-lint**

    ---

    Checks a README against the marketplace's documentation standards.

    [:material-arrow-right: Read more](skills/plugin-dev-tools/plugin-docs-lint.md)

-   :material-file-compare:{ .lg .middle } **plugin-diff**

    ---

    Plain-language summary of what changed between two plugin versions.

    [:material-arrow-right: Read more](skills/plugin-dev-tools/plugin-diff.md)

-   :material-source-pull:{ .lg .middle } **submit-plugin**

    ---

    Full submission: runs the security check, clones the repo, files the PR.

    [:material-arrow-right: Read more](skills/plugin-dev-tools/submit-plugin.md)

-   :material-clipboard-check:{ .lg .middle } **validate-marketplace**

    ---

    Curator tool: walks every plugin in a repository and reports what fails.

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
/plugin install <plugin-name>@claude-plugins
```

You only need to add the marketplace once. To see what is available, run
`/plugin list`; to pick up new and updated plugins later, run
`/plugin marketplace update claude-plugins` and reinstall the ones you want.

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
    `/plugin marketplace update claude-plugins` manually, or set
    `CLAUDE_CODE_PLUGIN_KEEP_MARKETPLACE_ON_FAILURE=1` in your environment.

---

## Contribute a plugin

Built something useful? The more we share, the less we each have to reinvent.
The **[Build & submit a plugin guide](contributing/build-and-submit.md)** walks
the whole path — scaffold, build, verify, security-check, and open a PR with
`/submit-plugin`.
