---
name: secret-resolver
description: Store and retrieve per-user secrets (OAuth secrets, tokens, API keys) for platform tools, provider-agnostically
---

The shared credential broker for the platform. Tools never keep secrets in their own files or the plugin directory — they ask this broker for a key.

Read the first word of the user's message to pick the operation: `status`, `get`, `set`, `list`, `install`, or `setup`. If none is given, print the usage below.

**Key format** is always three parts: `<domain>/<service>/<field>` — e.g. `personal/withings/refresh_token`, `corporate/jira/api_token`. The domain is the trust boundary (personal vs corporate) and, where the backend supports it, selects the vault.

All operations run the bundled script:

```bash
uv run "${CLAUDE_PLUGIN_ROOT}/skills/secret-resolver/scripts/secret_resolver.py" <cmd> [args]
```

## Operations

- **status** — show the active backend (keyring / pass / file) and where secrets are stored. Run this first when helping a user set up.
- **get `<key>`** — print a secret's value. Used by tools; auto-detects the backend.
- **set `<key>`** — store a secret. **Always read the value from stdin, never pass it on the command line** (argv is visible to other processes):
  ```bash
  printf '%s' "$VALUE" | uv run "${CLAUDE_PLUGIN_ROOT}/skills/secret-resolver/scripts/secret_resolver.py" set personal/withings/refresh_token --stdin
  ```
- **list** — list stored keys (keyring can't enumerate; pass/file can).
- **install** — register this resolver so other tools can find it (drops a pointer file + PATH launcher; see connector docs). Run this once before configuring any tool's device sync.
- **setup** — first-time runtime check + guided backend selection (see below).

## Operation: setup

**Step 1 — Check `uv`**

```bash
uv --version
```

Every operation in this skill runs via `uv run`. If not found, stop and tell the user to install it from https://docs.astral.sh/uv/ before continuing.

**Step 2 — Check the active backend**

Run `status` and report the backend it detects (`keyring`, `pass`, or `file`) and where it stores secrets. If it reports `file` (the plaintext fallback), tell the user their secrets would be stored unencrypted at `~/.config/health/secrets.json` and suggest installing `pass` (good on WSL2) or ensuring an OS keyring / Secret Service is available, then re-run `status` to confirm the better backend is picked up. Do not proceed to Step 3 on the `file` backend without the user explicitly accepting that tradeoff.

**Step 3 — Register the resolver**

Run `install` so tools can discover this resolver via their pointer-file convention.

**Step 4 — Store credentials**

If the user is setting up a specific tool, check that tool's `plugin.json` for a `requires_credentials` list and walk through storing each key with `set` (value via stdin, never on the command line).

## Backends (auto-detected; override with `SECRET_RESOLVER_BACKEND`)

| Backend | When | Encryption |
|---|---|---|
| `keyring` | an OS keyring / Secret Service is available | yes (OS-managed) |
| `pass` | `pass` is installed (good on WSL2) | yes (GPG) |
| `file` | nothing else present | **no** — `~/.config/health/secrets.json`, mode `0600`, fallback only |

Encryption comes entirely from `keyring` or `pass` — this tool rolls no crypto of its own. If it falls back to `file`, tell the user their secrets are plaintext-on-disk and suggest installing `pass`.

## For tool authors

Consume secrets either way:
- **Shell:** `uv run .../secret_resolver.py get <key>` and capture stdout.
- **Import:** `from secret_resolver import get_secret; get_secret("personal/withings/refresh_token")`.

Declare needs in the tool's `plugin.json` as `requires_credentials: ["personal/<service>/<field>", ...]`. Never store values there — only keys.

## Usage

```
/secret-resolver status                          — show backend & store
/secret-resolver get <domain>/<service>/<field>  — retrieve a secret
/secret-resolver set <domain>/<service>/<field>  — store one (value via stdin)
/secret-resolver list                            — list stored keys
/secret-resolver install                         — register this resolver for other tools to find
/secret-resolver setup                           — first-time runtime check + guided backend selection
```
