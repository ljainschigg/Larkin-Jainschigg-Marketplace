#!/usr/bin/env python3
"""
Walks the plugins/ directory, reads each plugin's .claude-plugin/plugin.json,
and writes the marketplace index to .claude-plugin/marketplace.json (the canonical
copy consumed via the `github` marketplace source), mirroring it into
site/marketplace.json when a mkdocs build is present (for gh-pages).
"""

import json
import os
import sys

REPO = "https://github.com/ljainschigg/Larkin-Jainschigg-Marketplace.git"
MARKETPLACE_NAME = "lj-marketplace"
PLUGINS_DIR = "plugins"
# Canonical index, committed to main. Consumed by
# `/plugin marketplace add ljainschigg/Larkin-Jainschigg-Marketplace`
# (Claude Code clones the repo and reads this file with the user's git creds).
CANONICAL_PATH = os.path.join(".claude-plugin", "marketplace.json")
# Copy served by the mkdocs site on gh-pages; only written when a build exists.
SITE_PATH = os.path.join("site", "marketplace.json")


def load_plugin(plugin_dir):
    manifest_path = os.path.join(PLUGINS_DIR, plugin_dir, ".claude-plugin", "plugin.json")
    if not os.path.isfile(manifest_path):
        print(f"  WARNING: no plugin.json found in {plugin_dir}, skipping", file=sys.stderr)
        return None

    with open(manifest_path) as f:
        manifest = json.load(f)

    return {
        "name": manifest["name"],
        "description": manifest.get("description", ""),
        "version": manifest.get("version", "1.0.0"),
        "source": {
            "source": "git-subdir",
            "url": REPO,
            "path": f"plugins/{plugin_dir}"
        }
    }


def main():
    if not os.path.isdir(PLUGINS_DIR):
        print(f"ERROR: {PLUGINS_DIR}/ directory not found. Run from repo root.", file=sys.stderr)
        sys.exit(1)

    plugins = []
    for entry in sorted(os.listdir(PLUGINS_DIR)):
        if os.path.isdir(os.path.join(PLUGINS_DIR, entry)):
            print(f"Processing plugin: {entry}")
            plugin = load_plugin(entry)
            if plugin:
                plugins.append(plugin)

    marketplace = {
        "name": MARKETPLACE_NAME,
        "owner": {"name": "Larkin J."},
        "plugins": plugins
    }

    payload = json.dumps(marketplace, indent=2)

    os.makedirs(os.path.dirname(CANONICAL_PATH), exist_ok=True)
    with open(CANONICAL_PATH, "w") as f:
        f.write(payload)
    print(f"Wrote {len(plugins)} plugin(s) to {CANONICAL_PATH}")

    # Mirror into the built site for gh-pages, when a mkdocs build is present.
    if os.path.isdir("site"):
        with open(SITE_PATH, "w") as f:
            f.write(payload)
        print(f"Mirrored to {SITE_PATH}")


if __name__ == "__main__":
    main()
