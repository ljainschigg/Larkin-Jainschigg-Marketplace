# Plugin Conventions (enforceable)

*The rules every plugin obeys. This is the terse checklist the tooling enforces; the complete narrative — every concern a plugin addresses, required or optional — is the on-site [Plugin anatomy](https://ljainschigg.github.io/Larkin-Jainschigg-Marketplace/contributing/plugin-anatomy/) reference (keep the two in agreement). Designed to **extend the skills you already have** rather than add new machinery.*

---

## 1. Manifest (`.claude-plugin/plugin.json`)

Required: `name`, `description`, `version` (semver), `name` == folder name, and `type` — one of `skill` | `tool` | `app` (skill = behavior only; tool = reaches an external service, needs credentials; app = a person's instance composing skills/tools). All are enforced (FAIL) by `publish-check`.

**This repo is canonical.** A plugin's source of truth is its directory here plus git history — plugins are developed and edited **in place**, not copied in from an external "real" source. There is no `source_of_truth` field; it was retired once the develop-elsewhere-then-copy model was dropped (the external `code/<x>` folders are just history).

**Optional, declarative (tools):**
- `requires_credentials` — list of resolver keys the tool needs, e.g. `["personal/withings/client_secret", "personal/withings/refresh_token"]`. Declares need; never holds values.
- `consumes` / `provides` — other tools composed, or capabilities offered (for reuse/dedupe visibility).

## 2. Versioning — bump-on-change

Any content change to a published plugin **requires a semver bump** — enforced by `publish-check` diffing each plugin against the git base. Marketplace HEAD always = the best, latest build (it leads, never lags); older pinned versions exist only for deliberate freezes.

## 3. Credentials

- **No secret in any repo, plugin, or the marketplace.** Enforced by `plugin-security-check`'s secret scan (BLOCKER) + `submit-plugin`'s inline gate.
- **Declare** needed keys in `requires_credentials` (`<domain>/<service>/<field>`).
- **Read order at use time:** env var `<SERVICE>_<FIELD>` (bring-your-own) → `secret-resolver` (`get_secret(...)`, provider-agnostic) → fail loud. Use secrets **server-side only** — never surface a raw value to the model.
- **Store time:** value entered by the user via stdin (`secret-resolver set … --stdin`), never argv, never necessarily through the model.
- **Setup negotiation:** a credentialed plugin's `setup` must detect `secret-resolver`, ask whether to use it or a bring-your-own solution, instruct the user to get each `requires_credentials` key into the chosen one, and confirm the read path works.
- **Personal data (PII) ≠ credentials.** The user's own data (contact info, logs, transcripts, gathered research, drafts) is not a vault secret. Store it in a user-owned location — the project/working folder for project-scoped data, or a per-user app-data dir for cross-session config — and **instruct the AI to `.gitignore` any of it written into a folder that could be a git repo** (and never commit it). Credentials never live in a PII file. Full narrative: [Plugin anatomy → Personal data](https://ljainschigg.github.io/Larkin-Jainschigg-Marketplace/contributing/plugin-anatomy/#personal-data-pii).
- Full narrative + rationale: [Plugin anatomy → Credentials](https://ljainschigg.github.io/Larkin-Jainschigg-Marketplace/contributing/plugin-anatomy/#credentials).

## 4. Classification (skill vs tool vs app)

Declared by `type`. A capability that reaches an external service is a **tool** and must be independently packaged so many skills/apps can compose it — no capability duplicated across plugins (today's `gdrive`-in-three-places is the anti-pattern to retire).

---

## 5. External runtime dependencies — the `setup` skill

A plugin whose main skill depends on something outside Claude Code's built-in tools — an MCP server's runtime (`uv`, `node`/`npm`), a system binary it shells out to (`git`, `gh`, `ffmpeg`, `pass`), a browser binary (Playwright's Chromium), or first-run credentials — must give the user a way to check that dependency **before** it fails mid-workflow, not discover it three steps into real use.

Two shapes; pick whichever fits how the plugin is used:

- **A dedicated `setup` skill** (`skills/setup/SKILL.md`, invoked as `/setup`) — for plugins used repeatedly after one install. Checks runtime versions, installs one-time binaries (e.g. `npx playwright install chromium`), scaffolds credential files, and verifies each MCP tool actually responds. Reference implementations: `researcher`, `get-pdfs`, `subtitle-studio`, `example-mcp-node-skill`, `example-mcp-python-skill`.
- **An inline Step 0 preflight** in the main skill — for single-shot workflows rather than "install once, use forever" tools (`submit-plugin` checks `git`/`gh auth status` before cloning anything), or where the check belongs inside an existing multi-step `setup` *operation* rather than a separate slash command (`diet`, `secret-resolver`).

Either way:
- **Check, don't assume.** Every runtime prerequisite the plugin needs gets an explicit check, run before the operation that needs it.
- **Fail loud and stop.** Tell the user exactly what's missing and how to fix it. Don't auto-install system-level things a user didn't ask for — an MCP server's own npm/uv-managed dependencies auto-installing on first run is fine; installing `git`, `uv`, `node`, or `gh` itself is not this skill's job.
- **README agreement.** The `## Prerequisites` section in `README.md` and the `setup` skill/step must check exactly the same things — neither documents a dependency the other doesn't verify.

## 6. Enforcement map — who checks what (all reuse)

| Rule | Enforced/emitted by | Status |
|---|---|---|
| `type` present & valid | `publish-check` (CI), `validate-marketplace`, `plugin-security-check` | enforced (FAIL) |
| `type` prompted & emitted in new plugins | `plugin-scaffold` | done |
| README accuracy vs `type`/behavior | `plugin-docs-lint` | cross-check |
| No committed secrets | `publish-check`, `plugin-security-check`, `submit-plugin` gate | enforced (FAIL) |
| Bump-on-change (vs git base) | `publish-check` (all publish paths) | enforced (FAIL) |
| `setup` skill/preflight present when external deps exist (§5) | `validate-marketplace`, `plugin-security-check` | enforced |
| `setup` skill scaffolded for new MCP plugins | `plugin-scaffold` | done |
