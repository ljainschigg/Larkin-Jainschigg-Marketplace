---
name: setup
description: One-time preflight for karpathy-kb — verifies Python 3 is available for the bundled lint helper.
---

Run this once after installing the plugin.

## Check: Python 3

!`python3 --version 2>&1 || true`

- If it prints **Python 3.8 or newer**, report "Python OK — you're set" and stop.
- If the command is missing or the version is older than 3.8, stop and tell the user:

  > karpathy-kb's deterministic vault scaffolder (`/kb-setup`), mechanical linter (`/kb-lint`), and bulk source registration (`/kb-ingest`) use **Python 3.8+**. Install Python 3, then run `/setup` again. Do not attempt to install it for them.

## Note

The knowledge-base skills all work without Python for their prompt-driven steps. Python powers three mechanical helpers: the deterministic scaffolder in `/kb-setup`, the auto-fix path of `/kb-lint`, and the bulk registration in `/kb-ingest`. Without it, each falls back to a manual equivalent — `/kb-setup` scaffolds by prompt, `/kb-lint` checks by hand per the KB's `CLAUDE.md`, and `/kb-ingest` falls back to `/kb-add` per file.
