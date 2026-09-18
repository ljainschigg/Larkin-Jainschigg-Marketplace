# Build and submit a plugin

This is the end-to-end path from an idea to a plugin published in the marketplace. There are two routes:

- **Contributors** build a plugin and open a **pull request** with `/submit-plugin`. A curator reviews and merges it. **This is the default and what most of this page covers.**
- **Maintainers** (with write access) may push complete, validated work straight to `main` — see [Maintainer path](#maintainer-path-direct-push) at the end.

The recommended tooling — [Plugin Dev Tools](../skills/plugin-dev-tools/index.md) — encodes the same standards a curator applies, so you can catch problems before you submit.

---

## Before you start

- **Claude Code** installed, with the marketplace added and authenticated. This is a **private** marketplace, so you need **read access to the repo** and git configured to authenticate — see [the authentication section on the home page](../index.md#do-you-need-to-authenticate). To *submit*, you also need permission to push a branch (collaborator access, or a fork).
- **The Plugin Dev Tools installed:**
  ```
  /plugin install plugin-scaffold@claude-plugins
  /plugin install plugin-docs-lint@claude-plugins
  /plugin install plugin-security-check@claude-plugins
  /plugin install submit-plugin@claude-plugins
  ```
- **Decide your plugin's `type`:** `skill` (behavior only), `tool` (reaches an external service, needs credentials), or `app` (a person's instance composing skills/tools). This goes in the manifest and is checked at submit time.

---

## 1. Scaffold

```
/plugin-scaffold
```

Describe what your plugin does. The scaffolder generates a correctly structured directory — manifest (`.claude-plugin/plugin.json` with `name`, `description`, `version`, `type`), `skills/<name>/SKILL.md`, `README.md`, and — if you asked for an MCP server — a `.mcp.json`, a `server/` stub, and a `skills/setup/SKILL.md` stub. See the [Plugin structure reference](plugin-structure.md) for the full layout and the rules the loader enforces.

## 2. Build your skill(s)

- Write your `SKILL.md`. Keep the prompt lean — put real logic in a bundled script (`skills/<name>/scripts/`) or an MCP `server/`, not in prose.
- Reference bundled files with **`${CLAUDE_PLUGIN_ROOT}`** and persistent state with **`${CLAUDE_PLUGIN_DATA}`** — never hardcode home directories.
- **If your plugin depends on anything outside Claude Code's built-in tools** — a runtime like `uv`/`node`, a system binary (`ffmpeg`, `git`), a browser (Playwright's Chromium), or first-run credentials — you **must** give the user a way to check it *before* it fails mid-workflow: either a dedicated `skills/setup/SKILL.md` (`/setup`) or an inline Step 0 preflight. Check, don't assume; fail loud. (Conventions §5.)
- **Never put secrets in the plugin.** Personal tokens/keys are read at runtime through the [secret-resolver](../skills/secret-resolver.md) tool, keyed `<domain>/<service>/<field>` — never committed. PII like name/email is instance config, not a secret.

## 3. Verify it actually runs

Install your plugin locally and drive the real flow — don't just read the prompt. Run `/setup` (if you wrote one) on a clean machine profile if you can, and exercise the main skill end to end. The most common submission failure is a dependency that only surfaces three steps into real use.

## 4. Lint the docs

```
/plugin-docs-lint
```

Fast check that your `README.md` meets the marketplace's documentation standards, and that it matches your plugin's actual `type` and behavior (e.g. the `## Prerequisites` section must check exactly what `/setup` checks).

## 5. Security & compliance check

```
/plugin-security-check
```

A deep inspection: manifest format (valid `type`), **committed-secret scan (a hard BLOCKER)**, blast radius, and documentation quality. Clear every BLOCKER; review and acknowledge any WARNINGs. This same check runs again automatically during submission, and its report is attached to your PR for the reviewer.

## 6. Submit (contributor path)

```
/submit-plugin
```

This runs the security check, clones the repo, creates a branch, and files a **pull request** with the review report included for the curator.

## 7. What happens next

- **CI runs automatically** on the PR: `publish-check` (manifest conventions, no committed secrets, and that `.claude-plugin/marketplace.json` is regenerated and in sync) and the strict docs build. Fix anything they flag and push again.
- **A curator reviews** the PR and the attached security report.
- **On merge to `main`**, the marketplace index regenerates and the docs site redeploys.
- **Users pick it up** with `/plugin marketplace update claude-plugins`, then `/plugin install <your-plugin>@claude-plugins`.

Updating an existing plugin later? Any content change requires a **semver version bump** (bump-on-change) — CI fails a changed plugin that wasn't bumped. [`/plugin-diff`](../skills/plugin-dev-tools/plugin-diff.md) summarizes what changed between two versions.

---

## Conventions your plugin must satisfy

These are enforced by the tooling and CI. The complete reference is **[Plugin anatomy](plugin-anatomy.md)** (the terse enforcement checklist is [`CONVENTIONS.md`](https://github.com/ljainschigg/Larkin-Jainschigg-Marketplace/blob/main/CONVENTIONS.md) in the repo):

- **Manifest:** `name` (== folder name), `description`, `version` (semver), and **`type`** (`skill` \| `tool` \| `app`). This repo is canonical — plugins are edited in place; there is no external `source_of_truth`.
- **Setup for external dependencies:** a `setup` skill or inline preflight that checks every runtime prerequisite (Conventions §5), with the README's `## Prerequisites` matching it exactly.
- **No secrets, ever** — in any plugin, repo, or the marketplace. Tools read secrets only via `secret-resolver`.
- **Bump-on-change:** any content change to a published plugin requires a semver bump.
- **Structure:** only the directories the loader allows at the plugin root (see [Plugin structure](plugin-structure.md)); everything else lives under `skills/<name>/` or `server/`.

---

## Maintainer path (direct push)

If you have write access and your change is **complete and valid**, you may publish directly instead of opening a PR. Validate locally first — the same gates CI enforces:

```
mkdocs build --strict                        # docs build must be clean
python3 scripts/publish-check.py --base HEAD # conventions, secrets, index freshness
```

Then publish in one step, which regenerates `.claude-plugin/marketplace.json`, commits it with your changes, and pushes:

```
make publish m="Add <your-plugin-name>"      # or scripts/publish.sh
```

**A push to `main` is a live production deploy** (it rebuilds and redeploys the site and the marketplace feed), so only take this path for work you've validated. Bump-on-change still applies. When in doubt, use the PR path.

---

## Reference

- [Plugin structure](plugin-structure.md) — the required directory layout and manifest
- [Plugin Dev Tools](../skills/plugin-dev-tools/index.md) — every tool in the workflow
- [Example plugins](../skills/example-skill.md) — a plain skill, plus Python and Node.js MCP examples
