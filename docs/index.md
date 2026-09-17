# Claude Plugins Marketplace

This marketplace shares Claude Code plugins — packaged capabilities that extend what Claude Code can do.

---

## Plugins and skills

Two terms you will see throughout this site:

**Plugin** — the installable package. A plugin is what this marketplace distributes, what you install with `/plugin install`, and what lives in a repository as a structured directory. A plugin can contain one or more skills, an MCP server, configuration, and documentation.

**Skill** — an individual `/command` within a plugin. When you type `/example-skill`, you are invoking a skill. Skills are defined by a prompt file (`SKILL.md`) inside the plugin and can optionally call tools exposed by an MCP server.

In practice, many plugins contain exactly one skill with the same name as the plugin itself. More capable plugins may bundle several related skills together.

---

## Prerequisites

You need **Claude Code** installed and running. If you haven't set it up yet, it only takes about five minutes.

---

## One-time setup

Add the plugins marketplace to your Claude Code installation. Open a terminal, start Claude Code, and run:

```
/plugin marketplace add ljainschigg/generic-marketplace-2
```

You only need to do this once. Claude Code will remember it.

### Do you need to authenticate?

Adding the marketplace and installing plugins both `git clone` the
`ljainschigg/generic-marketplace-2` repository. Whether you need
to set up authentication depends on whether that repository is **public** or
**private**.

=== "Public repository"

    If the marketplace repository is public, there is **nothing to set up**.
    `/plugin marketplace add` and `/plugin install` work with no authentication.
    Skip straight to [Browse available plugins](#browse-available-plugins).

=== "Private repository"

    If the marketplace repository is private (for example, an internal fork),
    you need two things:

    1. **Read access** to `ljainschigg/generic-marketplace-2`
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

## Browse available plugins

To see what's available:

```
/plugin list
```

---

## Install a plugin

```
/plugin install <plugin-name>@claude-plugins
```

Replace `<plugin-name>` with the name of the plugin you want. For example:

```
/plugin install example-skill@claude-plugins
```

---

## Use a skill

Once a plugin is installed, invoke its skill by typing `/` followed by the skill name:

```
/example-skill
```

Claude Code will run the skill in the context of whatever you're working on.

---

## Keep plugins up to date

When new plugins are added or existing ones are updated, refresh your local list:

```
/plugin marketplace update claude-plugins
```

Then reinstall any plugins you want to update.

---

## Plugin Dev Tools

If you are building a plugin, use the Plugin Dev Tools. These are fully-validated platform plugins that encode the standards and review criteria used by marketplace curators — so you can catch and fix problems before filing a PR, and submit with confidence.

| Tool | What it does |
|---|---|
| `/plugin-scaffold` | Generate a correct plugin structure from a description |
| `/plugin-docs-lint` | Check your README against documentation standards |
| `/plugin-security-check` | Deep inspection: compliance, security, blast radius, documentation quality |
| `/submit-plugin` | Full PR submission: runs the security check, clones the repo, files the PR |

Install any of them with:

```
/plugin install <tool-name>@claude-plugins
```

We encourage everyone building plugins to use these tools. The security check runs automatically as part of submission, and its report is included in every PR for reviewers.

---

## Contribute a plugin

Built something useful? The more we share, the less we each have to reinvent. The **[Build & submit a plugin guide](contributing/build-and-submit.md)** walks the whole path — scaffold, build, verify, security-check, and open a PR with `/submit-plugin`.
