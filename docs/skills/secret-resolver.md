# secret-resolver

The platform's shared, per-user secret broker. Tools (Fitbit, Withings, Google, …) ask it for a credential by key instead of keeping secrets in their own files or the plugin directory. One place to store secrets; one place to revoke them; provider-agnostic so each machine can back it with whatever it has.

## Prerequisites

- `uv` (runs the bundled Python script; `keyring` is pulled in automatically via the script header).
- Optionally `pass` (GPG password store) — recommended on WSL2, where there's usually no OS keyring service.

## Install

```
/plugin install secret-resolver@claude-plugins
```

## Use

```
/secret-resolver status                          — show the active backend and store location
/secret-resolver set <domain>/<service>/<field>  — store a secret (value read from stdin)
/secret-resolver get <domain>/<service>/<field>  — retrieve a secret
/secret-resolver list                            — list stored keys
```

Keys are always `<domain>/<service>/<field>`, e.g. `personal/withings/refresh_token`. The domain (`personal`, `corporate`, …) is the trust boundary and selects the vault where the backend supports it.

## How it works

A thin, provider-agnostic shim over proven infrastructure — the OS keyring (`python-keyring`), the `pass` GPG store, or, as a last resort, a `0600` plaintext file under `~/.config/health/`. The backend is auto-detected and overridable with `SECRET_RESOLVER_BACKEND`. It rolls no cryptography of its own; encryption comes from keyring or pass. Tools consume it by shelling out to `secret_resolver.py get <key>` or importing `get_secret`.

## Details

| | |
|---|---|
| **Version** | 0.2.1 |
| **Tier** | extended |
| **Type** | tool |
| **Maintained by** | Claude Plugins Marketplace |
