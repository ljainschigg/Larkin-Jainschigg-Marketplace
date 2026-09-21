---
description: "Submit your finished plugin - runs the security check, then opens the pull request for you."
---

# submit-plugin

Automates the full workflow for submitting a plugin to the plugins marketplace. Runs a security check, clones a fresh copy of the marketplace repository, creates a PR branch, moves files into the correct locations, validates the documentation build, and files a pull request whose description includes the full security review report.

The PR is never merged automatically. Merging is a human decision made by marketplace curators after reviewing the submission.

---

## Install

```
/plugin install submit-plugin@Larkin-Jainschigg-Marketplace
```

## Use

```
/submit-plugin
```

Claude will ask for the path to your plugin folder and which tier it belongs to (`platform`, `local`, or `extended`). Everything else is derived automatically.

---

## What it does

1. **Runs `plugin-security-check`** on your plugin folder. Any BLOCKER finding halts the process — fix the issue and run again. WARNING findings are shown for your review; you must acknowledge each one before submission proceeds.

2. **Prompts for a test attestation.** You describe briefly how you tested the plugin and what the output was. This is included in the PR body.

3. **Clones the marketplace repository** into a temporary directory so your local state is irrelevant to the submission.

4. **Creates a PR branch** named `submit/<plugin-name>`.

5. **Copies your plugin folder** into `plugins/<tier>/<plugin-name>/`.

6. **Promotes your README** — copies `README.md` to `docs/skills/<tier>/<plugin-name>.md` and adds the corresponding entry to `mkdocs.yml`.

7. **Validates the documentation build** by running `mkdocs build --strict` on the cloned repository with your additions included. Build failures halt the process.

8. **Commits, pushes, and files a pull request.** The PR description includes:
    - Plugin name, tier, and description
    - The full `plugin-security-check` report
    - Your test attestation
    - A reviewer checklist covering items that automated review cannot assess

---

## What reviewers receive

Every PR filed by `submit-plugin` contains a structured description so reviewers have everything they need without running anything themselves:

- Plugin summary and tier assignment
- Complete security check findings (BLOCKERs resolved, WARNINGs acknowledged)
- External services and MCP tools declared
- Submitter's test attestation
- Reviewer checklist

---

## Details

| | |
|---|---|
| **Version** | 1.2.5 |
| **Requires** | `plugin-security-check` |
| **Maintained by** | Claude Plugins Marketplace |
