# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""Migrate legacy in-repo credentials into secret-resolver (one-time).

Reads the old files (server/secrets.json, tokens.json, gdrive_credentials.json,
gdrive_tokens.json) and stores each value under a resolver key
`<domain>/<service>/<field>` (domain defaults to 'personal'). Idempotent.
Prints only key names, never secret values. Does NOT delete the old files —
verify the resolver works, then remove them yourself.

    uv run server/migrate_secrets_to_resolver.py [--from DIR] [--domain personal]
"""
import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import creds  # noqa: E402


def _load(path):
    try:
        return json.loads(Path(path).read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="src", default=str(Path(__file__).resolve().parent),
                    help="directory holding the legacy JSON files")
    ap.add_argument("--domain", default="personal")
    args = ap.parse_args()
    src = Path(args.src)
    dom = args.domain
    migrated = []

    def put(service, field, value):
        if value in (None, ""):
            return
        creds.set(service, field, str(value), dom)
        migrated.append(f"{dom}/{service}/{field}")

    secrets = _load(src / "secrets.json") or {}
    put("fitbit", "client_id", secrets.get("fitbit_client_id"))
    put("fitbit", "client_secret", secrets.get("fitbit_client_secret"))
    put("withings", "client_id", secrets.get("withings_client_id"))
    put("withings", "client_secret", secrets.get("withings_client_secret"))
    put("withings", "user_id", secrets.get("withings_user_id"))

    tokens = _load(src / "tokens.json") or {}
    for svc in ("fitbit", "withings"):
        t = tokens.get(svc) or {}
        put(svc, "access_token", t.get("access_token"))
        put(svc, "refresh_token", t.get("refresh_token"))
        if t.get("expires_at") is not None:
            put(svc, "expires_at", t.get("expires_at"))

    gcred = _load(src / "gdrive_credentials.json") or {}
    installed = gcred.get("installed") or gcred.get("web") or {}
    put("gdrive", "client_id", installed.get("client_id"))
    put("gdrive", "client_secret", installed.get("client_secret"))
    gtok = _load(src / "gdrive_tokens.json") or {}
    put("gdrive", "access_token", gtok.get("token") or gtok.get("access_token"))
    put("gdrive", "refresh_token", gtok.get("refresh_token"))
    if gtok.get("expiry"):
        put("gdrive", "expires_at", gtok.get("expiry"))

    print(f"Backend: {creds._load_resolver().detect_backend()}")
    if migrated:
        print(f"Migrated {len(migrated)} keys:")
        for k in migrated:
            print(f"  {k}")
        print("\nVerify with: secret_resolver.py get <key>, then delete the old JSON files.")
    else:
        print("No legacy credentials found to migrate.")


if __name__ == "__main__":
    main()
