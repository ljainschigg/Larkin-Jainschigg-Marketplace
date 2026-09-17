#!/usr/bin/env python3
"""publish-check.py — the shared publish gate for the marketplace (roadmap P5).

ONE deterministic check, run by every publish path so the discipline can't be
skipped:
  - contributors, via `submit-plugin`
  - owners/maintainers, publishing directly
  - CI, on every push / PR to main (see .github/workflows/publish-check.yml)

Checks each plugin under `plugins/`:
  1. Manifest — valid `plugin.json`, `name` == directory, semver `version`,
     and `type` in {skill,tool,app}  (all FAIL).
  2. No committed secrets — credential files or secret-looking content  (FAIL).
  3. Bump-on-change — if a plugin's files changed vs `--base` but its `version`
     did not, FAIL. Plugins that did not exist at `--base` are exempt (new).

`mkdocs build --strict` is run separately (validate-docs workflow).

Usage:
    python3 scripts/publish-check.py                # manifest + secret scan
    python3 scripts/publish-check.py --base <ref>   # + bump-on-change vs a git ref
Exit 0 if clean (warnings allowed), 1 on any FAIL, 2 on usage error.
"""
import argparse
import json
import os
import re
import subprocess
import sys

PLUGINS = "plugins"
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
CRED_FILE = re.compile(
    r"(client_secret.*\.json$|.*credentials.*\.json$|^credentials\.json$|"
    r"^token.*\.json$|.*tokens.*\.json$|^\.env$|.*\.pem$|^id_rsa$|^id_ed25519$)",
    re.I,
)
CONTENT_PATTERNS = [
    (re.compile(r"AKIA[0-9A-Z]{16}"), "AWS access key"),
    (re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"), "private key"),
    (re.compile(r'"private_key"\s*:\s*"-----BEGIN'), "service-account private key"),
    (re.compile(r'"(?:refresh_token|access_token)"\s*:\s*"[A-Za-z0-9._\-]{20,}"'), "OAuth token value"),
    (re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"), "Slack token"),
    (re.compile(r"ghp_[A-Za-z0-9]{36}"), "GitHub PAT"),
]
# Content patterns are scanned only in code/config, never docs (.md legitimately
# discusses secrets, e.g. key-name conventions).
SCAN_EXT = {".json", ".env", ".py", ".js", ".ts", ".sh", ".yaml", ".yml", ".txt", ".cfg", ".ini"}
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv"}


def sh(*args):
    return subprocess.run(args, capture_output=True, text=True)


def manifest_and_secret_checks():
    fails, warns = [], []
    plugins = sorted(d for d in os.listdir(PLUGINS) if os.path.isdir(os.path.join(PLUGINS, d)))
    for name in plugins:
        pdir = os.path.join(PLUGINS, name)
        pj = os.path.join(pdir, ".claude-plugin", "plugin.json")
        if not os.path.isfile(pj):
            fails.append(f"{name}: missing .claude-plugin/plugin.json")
        else:
            try:
                m = json.load(open(pj))
                if m.get("name") != name:
                    fails.append(f"{name}: plugin.json name={m.get('name')!r} != directory")
                if not SEMVER.match(str(m.get("version", ""))):
                    fails.append(f"{name}: version {m.get('version')!r} is not semver")
                if m.get("type") not in ("skill", "tool", "app"):
                    fails.append(f"{name}: `type` must be one of skill|tool|app")
            except Exception as e:
                fails.append(f"{name}: invalid plugin.json ({e})")
        # secret scan
        for root, dirs, files in os.walk(pdir):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            for fn in files:
                rel = os.path.relpath(os.path.join(root, fn), PLUGINS)
                if CRED_FILE.search(fn):
                    fails.append(f"committed secret file: plugins/{rel}")
                if os.path.splitext(fn)[1].lower() in SCAN_EXT:
                    try:
                        txt = open(os.path.join(root, fn), encoding="utf-8", errors="ignore").read()
                    except OSError:
                        continue
                    for pat, label in CONTENT_PATTERNS:
                        if pat.search(txt):
                            fails.append(f"committed secret ({label}): plugins/{rel}")
    return plugins, fails, warns


def bump_check(base, plugins):
    if sh("git", "rev-parse", "--verify", "--quiet", base).returncode != 0:
        return [], [f"bump-check skipped: base ref {base!r} not available"]
    fails = []
    for name in plugins:
        pdir = f"{PLUGINS}/{name}"
        diff = sh("git", "diff", "--quiet", base, "--", pdir)
        if diff.returncode != 1:  # 0 = unchanged; 128 handled by rev-parse above
            continue
        base_manifest = sh("git", "show", f"{base}:{pdir}/.claude-plugin/plugin.json")
        if base_manifest.returncode != 0:
            continue  # plugin didn't exist at base → new, exempt
        try:
            bv = json.loads(base_manifest.stdout).get("version")
            cur = json.load(open(f"{pdir}/.claude-plugin/plugin.json")).get("version")
        except Exception:
            continue
        if bv is not None and bv == cur:
            fails.append(f"{name}: content changed vs {base} but version still {cur} — bump required")
    return fails, []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", help="git ref to check bump-on-change against (e.g. origin/main, HEAD^)")
    args = ap.parse_args()
    if not os.path.isdir(PLUGINS):
        print("ERROR: run from the marketplace repo root (no plugins/ dir here)")
        sys.exit(2)

    plugins, fails, warns = manifest_and_secret_checks()
    if args.base:
        bf, bw = bump_check(args.base, plugins)
        fails += bf
        warns += bw

    for w in warns:
        print(f"WARN  {w}")
    for f in fails:
        print(f"FAIL  {f}")
    print(f"\npublish-check: {len(plugins)} plugins · {len(fails)} failure(s) · {len(warns)} warning(s)")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
