# /// script
# requires-python = ">=3.9"
# dependencies = ["keyring"]
# ///
"""secret_resolver — provider-agnostic secret access for platform tools.

The one shared credential broker. Tools never read secrets from their own
files or the plugin dir; they ask this for a key.

KEY FORMAT (always three parts):
    <domain>/<service>/<field>
    e.g.  personal/withings/refresh_token   corporate/jira/api_token
The domain (personal|corporate|...) is the trust boundary and, where the
backend supports it, selects the vault/collection.

BACKENDS (auto-detected; override with env SECRET_RESOLVER_BACKEND or --backend):
    keyring  OS keyring / Secret Service via python-keyring (best; encrypted)
    pass     the `pass` GPG password store (encrypted; WSL2-friendly)
    file     ~/.config/health/secrets.json, mode 0600 (FALLBACK ONLY; plaintext)

No bespoke crypto: encryption, when present, comes entirely from keyring or
pass. The file backend is an unencrypted last resort and says so.

CLI:
    secret_resolver.py get    <key>
    secret_resolver.py set    <key> [--value V | --stdin]
    secret_resolver.py list
    secret_resolver.py status
Library:
    from secret_resolver import get_secret, set_secret
"""
import argparse
import json
import os
import shutil
import subprocess
import sys

CONFIG_DIR = os.path.join(
    os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config")), "health"
)
FILE_STORE = os.path.join(CONFIG_DIR, "secrets.json")


def _split(key):
    parts = key.split("/")
    if len(parts) != 3 or not all(p.strip() for p in parts):
        raise ValueError(f"key must be '<domain>/<service>/<field>', got: {key!r}")
    return parts


# ---------- backend detection ----------
def _keyring_ok():
    try:
        import keyring
        from keyring.backends.fail import Keyring as FailKeyring
        return not isinstance(keyring.get_keyring(), FailKeyring)
    except Exception:
        return False


def detect_backend():
    override = os.environ.get("SECRET_RESOLVER_BACKEND")
    if override:
        return override
    if _keyring_ok():
        return "keyring"
    if shutil.which("pass"):
        return "pass"
    return "file"


# ---------- keyring ----------
def _kr_get(key):
    import keyring
    d, s, f = _split(key)
    return keyring.get_password(f"{d}/{s}", f)


def _kr_set(key, val):
    import keyring
    d, s, f = _split(key)
    keyring.set_password(f"{d}/{s}", f, val)


def _kr_list():
    return None  # keyring has no portable enumeration API


# ---------- pass ----------
def _pass_get(key):
    _split(key)
    r = subprocess.run(["pass", "show", key], capture_output=True, text=True)
    if r.returncode != 0:
        return None
    lines = r.stdout.splitlines()
    return lines[0] if lines else None


def _pass_set(key, val):
    _split(key)
    subprocess.run(
        ["pass", "insert", "--multiline", "--force", key],
        input=val if val.endswith("\n") else val + "\n",
        text=True,
        check=True,
    )


def _pass_list():
    r = subprocess.run(["pass", "ls"], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


# ---------- file (fallback, plaintext 0600) ----------
def _file_load():
    if not os.path.exists(FILE_STORE):
        return {}
    with open(FILE_STORE) as fh:
        return json.load(fh)


def _file_save(data):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    os.chmod(CONFIG_DIR, 0o700)
    fd = os.open(FILE_STORE, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as fh:
        json.dump(data, fh, indent=2, sort_keys=True)


def _file_get(key):
    _split(key)
    return _file_load().get(key)


def _file_set(key, val):
    _split(key)
    data = _file_load()
    data[key] = val
    _file_save(data)


def _file_list():
    return "\n".join(sorted(_file_load().keys())) or "(empty)"


_BACKENDS = {
    "keyring": (_kr_get, _kr_set, _kr_list),
    "pass": (_pass_get, _pass_set, _pass_list),
    "file": (_file_get, _file_set, _file_list),
}


# ---------- public API ----------
def get_secret(key, backend=None):
    """Return the secret for key, or None if unset. Raises ValueError on a bad key."""
    b = backend or detect_backend()
    return _BACKENDS[b][0](key)


def set_secret(key, value, backend=None):
    b = backend or detect_backend()
    _BACKENDS[b][1](key, value)


# ---------- CLI ----------
def _main(argv=None):
    p = argparse.ArgumentParser(description="Provider-agnostic secret broker.")
    p.add_argument("--backend", choices=list(_BACKENDS), help="override auto-detection")
    sub = p.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("get", help="print a secret's value to stdout")
    g.add_argument("key")

    s = sub.add_parser("set", help="store a secret")
    s.add_argument("key")
    src = s.add_mutually_exclusive_group(required=True)
    src.add_argument("--value", help="value inline (avoid: visible in process args)")
    src.add_argument("--stdin", action="store_true", help="read value from stdin (preferred)")

    sub.add_parser("list", help="list stored keys (where the backend supports it)")
    sub.add_parser("status", help="show the active backend and store location")
    sub.add_parser("install", help="register this resolver so other tools can find it")

    args = p.parse_args(argv)
    backend = args.backend or detect_backend()

    try:
        if args.cmd == "install":
            self_path = os.path.abspath(__file__)
            os.makedirs(CONFIG_DIR, exist_ok=True)
            os.chmod(CONFIG_DIR, 0o700)
            pointer = os.path.join(CONFIG_DIR, "resolver-path")
            with open(pointer, "w") as fh:
                fh.write(self_path + "\n")
            bindir = os.path.expanduser("~/.local/bin")
            os.makedirs(bindir, exist_ok=True)
            launcher = os.path.join(bindir, "secret-resolver")
            with open(launcher, "w") as fh:
                fh.write(f'#!/bin/sh\nexec python3 "{self_path}" "$@"\n')
            os.chmod(launcher, 0o755)
            print(f"pointer:  {pointer}")
            print(f"launcher: {launcher}  (ensure ~/.local/bin is on PATH)")
            print("tools now discover the resolver via the pointer file; no env var needed.")
            return 0
        if args.cmd == "status":
            print(f"backend: {backend}")
            if backend == "file":
                print(f"store:   {FILE_STORE} (plaintext, mode 0600 — FALLBACK; "
                      f"install `pass` or a keyring backend for encryption)")
            elif backend == "keyring":
                import keyring
                print(f"store:   {keyring.get_keyring().__class__.__name__}")
            else:
                print("store:   pass (GPG password store)")
            return 0

        if args.cmd == "get":
            val = get_secret(args.key, backend)
            if val is None:
                print(f"(no secret set for {args.key})", file=sys.stderr)
                return 1
            print(val)
            return 0

        if args.cmd == "set":
            val = args.value if args.value is not None else sys.stdin.read().rstrip("\n")
            set_secret(args.key, val, backend)
            print(f"stored {args.key} in {backend}", file=sys.stderr)
            return 0

        if args.cmd == "list":
            out = _BACKENDS[backend][2]()
            print(out if out is not None
                  else f"(the {backend} backend does not support enumeration)")
            return 0
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(_main())
