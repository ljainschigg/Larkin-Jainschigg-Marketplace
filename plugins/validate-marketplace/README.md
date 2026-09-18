# validate-marketplace

Curator tool that walks every plugin in a marketplace repository and reports format compliance issues, missing required files, and documentation gaps. Run this before cutting a release, after accepting a batch of PRs, or any time you want a health check on the full catalog.

---

## Install

```
/plugin install validate-marketplace@Larkin-Jainschigg-Marketplace
```

## Use

```
/validate-marketplace
```

Claude will look for a `plugins/` directory in the current working directory, or ask for the path to a marketplace repository.

---

## What it checks

For each plugin found in the repository:

- `plugin.json` is present, valid JSON, and contains all required fields
- Plugin name matches its directory name
- `skills/<name>/SKILL.md` exists
- MCP server configuration (if declared) references files that exist
- `README.md` is present and non-empty
- The plugin appears in `mkdocs.yml` navigation
- The plugin has a corresponding docs page in `docs/skills/`
- If it has external runtime dependencies (MCP server, or shells out to a system binary), it has a `setup` skill or an equivalent inline preflight (`CONVENTIONS.md` §5)

---

## Output

A report listing each plugin and its status. Plugins with issues are flagged with the specific problems found. A summary at the end gives counts of healthy, warning, and failing plugins.

Intended for curators, not end users. Does not modify any files.

---

## Details

| | |
|---|---|
| **Version** | 1.2.6 |
| **Maintained by** | Claude Plugins Marketplace |
