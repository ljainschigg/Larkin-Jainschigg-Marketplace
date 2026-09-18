#!/usr/bin/env bash
#
# One-command publish for the marketplace.
#
# Regenerates the committed index (.claude-plugin/marketplace.json) from the
# current plugins/ tree, then commits every pending change together with it and
# pushes to main — in a single step, so what's on main is always self-consistent.
#
# The `github` marketplace source reads .claude-plugin/marketplace.json from
# main, so once this pushes, consumers get the fresh index. gh-pages redeploys
# on its own via the Build and Deploy workflow.
#
# Usage:
#   scripts/publish.sh ["commit message"]     # or: make publish m="commit message"
#
set -euo pipefail

cd "$(dirname "$0")/.."

# Publish only from main — the github source reads the default branch.
branch="$(git rev-parse --abbrev-ref HEAD)"
if [ "$branch" != "main" ]; then
  echo "ERROR: on branch '$branch'. Publish from 'main'." >&2
  exit 1
fi

# Sync first so the index reflects everyone's plugins and the push won't be
# rejected. --autostash tucks away your uncommitted plugin edits across the
# rebase and restores them afterward.
echo "==> Syncing with origin/main"
git pull --rebase --autostash origin main

# Regenerate the committed index from plugins/.
echo "==> Regenerating .claude-plugin/marketplace.json"
python3 scripts/generate-marketplace.py

# Nothing staged, nothing unstaged, index already current -> stop.
if git diff --quiet && git diff --cached --quiet; then
  echo "==> Nothing to publish: working tree clean and index already up to date."
  exit 0
fi

echo "==> Changes to publish:"
git add -A
git status --short

msg="${1:-Update marketplace}"
git commit -m "$msg"

echo "==> Pushing to origin/main"
git push origin main

echo
echo "Done. Consumers will pick up the new index with:"
echo "  /plugin marketplace update Larkin-Jainschigg-Marketplace"
