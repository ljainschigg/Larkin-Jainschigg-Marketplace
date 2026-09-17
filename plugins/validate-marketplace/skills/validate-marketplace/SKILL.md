---
name: validate-marketplace
description: Walks all plugins in a marketplace repository and reports format compliance issues
---

Validate all plugins in a Claude Code marketplace repository. Look for a `plugins/` directory in the current working directory. If not found, ask the user for the repository path.

For each subdirectory found directly under `plugins/` (and one level deeper if tier subdirectories are present), check:

1. `.claude-plugin/plugin.json` exists and is valid JSON with `name`, `description`, and `version` fields
2. Plugin name in `plugin.json` matches the directory name
3. `skills/<name>/SKILL.md` exists, where `<name>` matches the plugin name
4. If `.mcp.json` is present: it is valid JSON and all referenced files exist within the plugin directory
5. `README.md` exists and is non-empty
6. A docs page exists somewhere under `docs/skills/` for this plugin (search by filename `<name>.md`)
7. The plugin appears in `mkdocs.yml` navigation
8. **[Conventions]** `plugin.json` declares a valid `type` (`skill` | `tool` | `app`). Report a missing/invalid `type` as a failing (🚫) compliance item. See `CONVENTIONS.md`. (There is no `source_of_truth` field — this repo is canonical; plugins are edited in place.)
9. **[Conventions]** External runtime dependencies are self-checked (`CONVENTIONS.md` §5). If the plugin has `.mcp.json`, or its `SKILL.md`/README shells out to a system binary beyond what its own runtime auto-installs (`git`, `gh`, `ffmpeg`, `pass`, a browser, etc.), it must have either a `skills/setup/SKILL.md` or a clearly documented inline Step 0 preflight in its main `SKILL.md` that checks the same things listed in the README's `## Prerequisites` section. Report a missing check as a 🚫 failing item — no rollout warning period for this one.
10. **[Conventions]** Credential standard (`CONVENTIONS.md` §3). If the plugin uses credentials (declares `requires_credentials`, or reads API keys / OAuth secrets / tokens), it must: declare the keys in `requires_credentials`; read them **server-side** in the order env `<SERVICE>_<FIELD>` → `secret-resolver` → fail loud (never surfacing a raw secret to the model); and run a credential negotiation in its `setup` (detect `secret-resolver`, ask resolver-or-bring-your-own, instruct storing each key, confirm the read path). Report a missing piece as a 🚫 failing item.
11. **[Conventions]** Personal data (PII) (`CONVENTIONS.md` §3). If the plugin writes the user's own data (research, transcripts, logs, drafts, downloads, cloned repos) into a project/working folder, its skill must ensure that data is `.gitignore`d (create/append `.gitignore`) and never commit it; PII lives in a user-owned location, never via `secret-resolver`. Report a missing `.gitignore` step as a 🚫 failing item.

---

Produce a report listing each plugin found and its status:

✅ **<plugin-name>** — all checks passed
⚠️ **<plugin-name>** — non-blocking issues: (list)
🚫 **<plugin-name>** — failing: (list missing or invalid items)

End with a one-line summary:
> Checked N plugins: X healthy, Y with warnings, Z failing.

This tool is read-only. It does not modify any files.
