# Plugin anatomy — what every plugin needs

This is the canonical reference for the *shape* of a marketplace plugin: every concern a plugin addresses, whether it is **required** or **optional**, and how it's realized. Most plugins stub or omit the optional concerns — a one-skill prompt plugin touches only a handful of rows below. Nothing here is aspirational; each row is checked by the tooling or by review.

Read this alongside the other two contributing pages, which cover the *how* rather than the *what*:

- **[Plugin structure](plugin-structure.md)** — the required directory layout and the rules the loader enforces.
- **[Build & submit a plugin](build-and-submit.md)** — the end-to-end process (scaffold → verify → security-check → PR).

The terse, tooling-facing version of the enforceable rules lives in [`CONVENTIONS.md`](https://github.com/ljainschigg/Larkin-Jainschigg-Marketplace/blob/main/CONVENTIONS.md) in the repo; this page is the complete narrative. The two must agree.

---

## The manifest at a glance

`.claude-plugin/plugin.json` — required in every plugin:

```json
{
  "name": "my-plugin",
  "description": "One sentence: what this plugin does.",
  "version": "1.0.0",
  "type": "skill"
}
```

| Field | Required? | Notes |
|---|---|---|
| `name` | **Required** | Must equal the plugin's folder name. |
| `description` | **Required** | One sentence, present tense. |
| `version` | **Required** | Semver. Bumps on every content change (see Lifecycle). |
| `type` | **Required** | `skill` \| `tool` \| `app` (see Classification). |
| `mcpServers` | If MCP | A **path** to `.mcp.json` — never an inline object. |
| `requires_credentials` | If a tool needs secrets | Resolver keys only (declares need, never holds values). |
| `consumes` / `provides` | Optional | Capabilities composed or offered, for reuse/dedupe visibility. |

There is **no `source_of_truth` field.** This repo is canonical — plugins are developed and edited in place; provenance is the repo plus git history.

---

## Every concern, one row at a time

| Concern | Required? | How it's realized | The rule |
|---|---|---|---|
| **Identity** | Required | `name` / `description` / `version` in the manifest | Semver; `name` == folder name. |
| **Classification** | Required | `type` field | `skill` (behavior only), `tool` (reaches an external service / needs credentials), or `app` (a person's instance composing skills/tools). |
| **Capability** | Required | `skills/<name>/SKILL.md` (with YAML frontmatter: `name`, `description`) | The prompt is lean; real logic lives in a bundled script or MCP server, not in prose. |
| **Invocation** | Required | The skill name (`/<plugin>:<skill>`), optional `$ARGUMENTS` | How the user triggers and parameterizes it. |
| **Runtime substrate** | As needed | `.mcp.json` + `server/` (MCP) or `scripts/` under the skill; declares its runtime (`uv`, `node`, none) | Bundled tool dependencies travel with the plugin. |
| **Dependency preflight** | Required **if** it has external deps | A dedicated `skills/setup/SKILL.md`, **or** an inline Step 0 in the main skill | Check, don't assume; fail loud *before* the step that needs the dep. See [External dependencies](#external-dependencies-the-preflight-5) below. |
| **Credentials** | As needed | `secret-resolver` via `requires_credentials` keys | No secret ever in a plugin, repo, or the marketplace. PII (name/email) is instance config, not a secret. |
| **State & data** | As needed | `${CLAUDE_PLUGIN_DATA}` for persistence; instance config files for personalization | Person-neutral *engine* vs *instance* config are separate; user data (PII) is `.gitignore`d, never a credential (see below). |
| **Portability** | Required | `${CLAUDE_PLUGIN_ROOT}` / `${CLAUDE_PLUGIN_DATA}` | Never hardcode home directories or absolute paths. |
| **Composition** | Optional | `consumes` / `provides` in the manifest | Declare composed capabilities so the same capability isn't duplicated across plugins. |
| **Documentation** | Required | `README.md` + a page under `docs/skills/` + a `mkdocs.yml` nav entry | The README's `## Prerequisites` must check exactly what the preflight checks. |
| **Validation** | Required | Passes `publish-check`, `plugin-security-check`, and the strict docs build | Manifest valid, no committed secrets, bump-on-change satisfied. |
| **Distribution** | Automatic | The generated `.claude-plugin/marketplace.json` (`git-subdir` source) | Never hand-edit the index; it's regenerated from `plugins/`. |
| **Lifecycle** | Required | Semver bump-on-change; clean retirement; optionally a second distribution (a claude.ai Project) | Marketplace HEAD always leads. |
| **Provenance** | n/a (no field) | The repo + git history | The repo is canonical. |

**The stubbing principle:** a plugin only needs the rows that apply to it. A pure prompt skill (say, `markdown-doc-cleaner`) satisfies Identity, Classification, Capability, Invocation, Documentation, Validation, Distribution, Lifecycle — and legitimately *stubs* (omits) Runtime, Preflight, Credentials, State, and Composition. An MCP tool with device sync (say, `diet`) lights up nearly every row. Omitting a row you don't need is correct; skipping a row you *do* need is the defect.

---

## The required rules, in full

### Classification (skill vs tool vs app)
Declared by `type`. A capability that reaches an external service is a **tool** and should be independently packaged so many skills/apps can compose it — no capability duplicated across plugins.

### Credentials

A plugin that reaches a system of record on the user's behalf needs the user's credentials — **without those credentials ever living in the plugin, the repo, or (raw) the AI's context.** The rules:

- **No secret in any repo, plugin, or the marketplace** — enforced by the secret scan (a hard BLOCKER).
- **Secrets ≠ profile config.** PII (name, email, company) is *instance config* (an instance `.env` / profile), not a vault secret. Only actual credentials (API keys, OAuth client secrets, tokens) go through the credential path below.
- **Declare what you need.** List the credential keys in the manifest's `requires_credentials` (`<domain>/<service>/<field>`, e.g. `personal/fitbit/client_id`). This is the machine-readable contract the setup flow iterates and the store's walkthrough reads. Declare need; never store values.

**Use secrets server-side, never surface them to the model.** A credentialed plugin must fetch and use secrets **inside its own MCP server / bundled script** (call the resolver there, make the API call there, return only *results*). Never `get` a raw secret into the model's context. This is the property that makes "the AI acts on your behalf without holding your credentials" true.

**The credential-read contract (use time).** Read in this order, so the user's *preferred* solution wins and there's always a bring-your-own escape hatch:

1. **Environment variable** — `<SERVICE>_<FIELD>` uppercased (e.g. `FITBIT_CLIENT_ID`). Lets a user inject a secret from *their own* solution (1Password CLI, Vault, direnv, plain shell) without adopting the resolver.
2. **`secret-resolver`** — the sanctioned managed store (`get_secret("<domain>/<service>/<field>")`); provider-agnostic (keyring / pass / file), so the user picks their own backend/security posture.
3. **Fail loud** — if neither is set, stop with exact instructions (run the plugin's `/setup`).

**Storing a secret without exposing it to the AI (store time).** The default path is the user entering the value themselves so it never enters the model's context: either in their own terminal, or via the `!` bang so the value isn't in the model's input — always piped via **stdin**, never on the command line:
```
printf '%s' "$VALUE" | secret-resolver set personal/fitbit/client_id --stdin
```
Only if the user chooses to hand a value to the assistant does the assistant store it on their behalf.

**The setup negotiation (required for any credentialed plugin's `setup`).** The plugin's `setup` skill/step must:

1. **Detect** whether the user already has `secret-resolver` installed and adopted as their preferred credential store.
2. **Ask** whether to use `secret-resolver` for *this* plugin, or whether they have another preferred solution (env-injected).
3. **Instruct** them to get each required credential (from `requires_credentials`) into the chosen solution — via `secret-resolver set … --stdin` (user enters the value), or by exporting the `<SERVICE>_<FIELD>` env vars from their own tool.
4. **Confirm the read path** works for the chosen solution before finishing (the plugin reads env-first, then resolver, at use time).

### Personal data (PII)

Distinct from credentials — don't conflate them. **Credentials** grant access and are used *indirectly* through the resolver (the model never holds the value; they're revocable). **PII** is the user's own *data* — contact details, health logs, transcripts, gathered research, drafts. The model *does* see and work with PII; that's the point, so the control is **not** encryption or hiding it from the model. It's **location + keeping it out of version control**:

- **Store it in a user-owned standard place.** Project-scoped data goes in the user's **project/working folder** (e.g. `<project-dir>/resources/`, `<project-dir>/outputs/`). Cross-session profile/config can live in a per-user app-data dir (`${CLAUDE_PLUGIN_DATA}` or `~/.local/share/<plugin>/` — outside any repo). Never in the plugin or the marketplace.
- **Keep it out of git.** Whenever a plugin writes user data into a folder that could be a git repository (any project/working dir), its skill must **ensure that data is `.gitignore`d** — create or append a `.gitignore` covering the data/output paths *and any cloned reference material* — and must never `git add`/commit it. The dominant leak vector in an AI-assisted, git-centric workflow is an accidental `git add . && push`; `.gitignore` is the primary control.
- **PII is not a vault secret.** Don't push contact info or a research corpus through `secret-resolver` — that's a category error and overkill. And a credential never lives in a PII file.

### External dependencies — the preflight (§5)
A plugin whose skill depends on anything outside Claude Code's built-in tools — an MCP runtime (`uv`, `node`/`npm`), a system binary it shells out to (`git`, `gh`, `ffmpeg`), a browser binary (Playwright's Chromium), or first-run credentials — must let the user **check that dependency before it fails mid-workflow.** Two shapes:

- **A dedicated `setup` skill** (`skills/setup/SKILL.md`, `/setup`) — for plugins used repeatedly after one install. Checks runtime versions, installs one-time binaries, scaffolds credential files, verifies each MCP tool responds.
- **An inline Step 0 preflight** in the main skill — for single-shot workflows, or where the check belongs inside a larger operation.

Either way: **check, don't assume; fail loud and stop** with exact fix instructions; and keep the README's `## Prerequisites` in agreement with what the preflight checks. (Note: skill `` !`…` `` blocks all run at load and abort the skill on non-zero exit — use them only for lightweight checks with `|| true`, and do installs / file creation as model-run steps.)

### Versioning — bump-on-change
Any content change to a published plugin **requires a semver bump**, enforced by `publish-check` diffing each plugin against the git base. Marketplace HEAD always equals the best, latest build.

### Person-neutral engine vs instance
A published plugin is a **person-neutral engine** — it hardcodes no identity. Whatever personalizes a deployment (a user's targets, profile, role, data) lives in **instance config** read at runtime, never baked into the skill. `diet` is the reference: the engine reads `targets.json` / `food-reference.md` from the instance; a specific person's instance lives separately. This holds even when a given deployment is personalized — the personalization is config, not code.

---

## Enforcement — who checks what

| Rule | Enforced by | Status |
|---|---|---|
| Manifest valid (`name`==dir, semver `version`, valid `type`) | `publish-check` (CI), `validate-marketplace`, `plugin-security-check` | FAIL |
| No committed secrets | `publish-check`, `plugin-security-check`, `submit-plugin` | FAIL |
| Bump-on-change (vs git base) | `publish-check` (all publish paths) | FAIL |
| Preflight present when external deps exist (§5) | `validate-marketplace`, `plugin-security-check` | FAIL |
| README accuracy vs `type` / behavior | `plugin-docs-lint` | cross-check |
| Docs page + nav entry exists | `validate-marketplace` | check |
| New plugins emit `type` + a `setup` stub for MCP | `plugin-scaffold` | done |

Run them yourself before submitting: `/plugin-docs-lint`, then `/plugin-security-check`, then `/submit-plugin` (which re-runs the checks and files the PR). See [Build & submit a plugin](build-and-submit.md).

---

## The two ends of the spectrum

**Minimal well-formed plugin** (pure prompt skill):

```
my-plugin/
  .claude-plugin/plugin.json      # name, description, version, type: skill
  skills/my-plugin/SKILL.md       # frontmatter + the prompt
  README.md                       # what it is, how to install, how to use
```
plus a `docs/skills/my-plugin.md` page and a `mkdocs.yml` nav entry.

**Fully-loaded plugin** (MCP tool with credentials) additionally has: `.mcp.json` + `server/`, a `skills/setup/SKILL.md` preflight, `requires_credentials` in the manifest reading via `secret-resolver`, and state under `${CLAUDE_PLUGIN_DATA}`. See `researcher`, `diet`, and `subtitle-studio` as worked examples, and the [example plugins](../skills/example-skill.md) for the smallest runnable MCP templates.
