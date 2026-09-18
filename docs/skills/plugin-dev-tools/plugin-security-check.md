# plugin-security-check

Deep inspection of a plugin folder that evaluates format compliance, security risks, blast radius, and documentation quality. Produces a structured report with rated findings. Called automatically by [submit-plugin](submit-plugin.md), and useful to run at any point during development.

---

## Install

```
/plugin install plugin-security-check@lj-marketplace
```

## Use

```
/plugin-security-check
```

Claude will ask for the path to the plugin folder if you do not provide one.

---

## What it checks

### Format compliance

- `plugin.json` is valid JSON with all required fields (`name`, `description`, `version`)
- Plugin name matches its directory name
- `skills/<name>/SKILL.md` exists
- If MCP servers are declared, they reference a `.mcp.json` file rather than inline configuration
- `.mcp.json` is valid JSON and references files that exist in the plugin
- `README.md` is present and non-empty

### Credential and secret exposure

- Hardcoded API keys, tokens, and bearer strings
- AWS, GCP, and Azure credential patterns
- PEM blocks and private key material
- Password or secret assignments in code or config files
- `.env` files accidentally included in the plugin folder

### Dangerous behaviors

- Destructive operations (file deletion, database drops, `git reset`) invoked without explicit user confirmation
- Outbound network calls from MCP server code, and what endpoints are contacted
- Writes to files outside the expected working directory scope
- Interaction with credentials stores, cloud IAM, or SSH keys
- Ability to send messages, emails, notifications, or post to external services
- Prompt injection risk: if the plugin reads external content (files, URLs, APIs) and passes it to Claude, injected instructions in that content could alter Claude's behavior

### Blast radius

- Does the plugin touch files outside the current working directory?
- Does it push code or modify git history?
- Does it modify infrastructure, permissions, or cloud resources?
- Could it trigger runaway execution or excessive API consumption?

### Dependency and supply chain

- For MCP plugins: are dependencies pulled from external registries, and are versions pinned or floating?
- Known vulnerabilities via `npm audit` or `pip-audit`
- License compatibility for internal use

### Documentation quality

- Does the README accurately describe what the plugin does? (assessed against the actual code and SKILL.md)
- Are dangerous operations documented with warnings?
- Are MCP tools and external dependencies listed?
- Are prerequisites stated?
- Does the SKILL.md description match the plugin's actual behavior?

---

## Report format

Findings are rated at three levels:

| Level | Meaning |
|---|---|
| **BLOCKER** | Must be fixed before the plugin can be submitted |
| **WARNING** | Should be reviewed; submission requires explicit acknowledgment |
| **INFO** | Informational; no action required |

The report closes with an overall verdict: **PASS**, **PASS WITH WARNINGS**, or **FAIL**.

---

## Details

| | |
|---|---|
| **Version** | 1.2.6 |
| **Maintained by** | Claude Plugins Marketplace |
