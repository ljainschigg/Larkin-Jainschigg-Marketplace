---
description: "The tools for building, checking and submitting a plugin to this marketplace."
---

# Plugin Dev Tools

Plugin Dev Tools are fully-validated platform skills for building, reviewing, and submitting plugins to this marketplace. They are maintained by the Claude Plugins Marketplace and are the recommended way to develop and contribute plugins.

If you are building a plugin — whether for yourself, your department, or for contribution to this marketplace — start here. These tools encode the standards and review criteria that human curators apply when evaluating submissions, so you can catch and fix problems before filing a PR.

---

## Available tools

| Tool | What it does |
|---|---|
| [plugin-security-check](plugin-security-check.md) | Deep inspection of a plugin folder: format compliance, security, blast radius, documentation quality |
| [submit-plugin](submit-plugin.md) | Full PR submission workflow: runs security check, clones repo, creates branch, files PR with review report |
| [plugin-scaffold](plugin-scaffold.md) | Generates a correct plugin directory structure from a description |
| [plugin-docs-lint](plugin-docs-lint.md) | Fast check that a plugin's README meets documentation standards |
| [plugin-diff](plugin-diff.md) | Plain-language summary of what changed between two versions of a plugin |
| [validate-marketplace](validate-marketplace.md) | Curator tool: walks all plugins in the repo and reports format or compliance issues |

---

## Recommended workflow

1. **Scaffold** a new plugin with `/plugin-scaffold`
2. Build your skill
3. **Lint** the docs with `/plugin-docs-lint` as you write
4. Run **`/plugin-security-check`** when you think it's ready
5. Fix any BLOCKERs; review and acknowledge any WARNINGs
6. **Submit** with `/submit-plugin` — the security check runs again as part of the PR
