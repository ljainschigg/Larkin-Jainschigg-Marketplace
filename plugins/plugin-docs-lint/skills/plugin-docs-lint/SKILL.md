---
name: plugin-docs-lint
description: Checks a plugin's README.md against the marketplace's documentation standards
---

Check a plugin's `README.md` against the marketplace's documentation standards. Look for `README.md` in the current directory, or ask the user for a path if one is not found there.

Also read `skills/*/SKILL.md` and `.claude-plugin/plugin.json` if present — you need them to verify that the README is accurate, not just well-formed.

Evaluate the README against the following and produce an advisory list of findings:

---

## Structure

- Is there a single `#` H1 heading at the top?
- Are the required sections present: a description, install instructions, usage, and a details table?
- Does the details table include at least `Version` and `Maintained by` fields?
- Are any sections empty or containing placeholder text (e.g., "TODO", "coming soon", lorem ipsum)?

## Content accuracy

- Does the description match what the plugin actually does based on `SKILL.md` and any server code? Flag discrepancies.
- If the plugin uses MCP tools or contacts external services, are they listed?
- If the plugin has prerequisites (tools to install, accounts needed, permissions required), are they stated?
- Are dangerous operations or elevated blast radius documented with appropriate warnings?
- Does the install command reference the correct plugin name?
- Does the invocation example match the plugin name?
- **[Conventions]** Does the README's framing match the plugin's declared `type` in `plugin.json`? A `tool` should document its external service and required credentials/setup; a `skill` should not imply external access it does not have.

## Style

- Do headings use sentence case (`## How it works`, not `## How It Works`)?
- Is there any obviously broken markdown: unclosed code fences, malformed tables, broken links?
- Is the writing direct and specific rather than vague or generic?

---

Produce a list of findings with brief suggested fixes for each. All findings are advisory — this tool does not block anything.

If no issues are found, tell the user the README looks good and is ready for submission.
