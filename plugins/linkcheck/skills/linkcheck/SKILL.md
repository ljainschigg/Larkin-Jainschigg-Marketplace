---
name: linkcheck
description: Scan a versioned MkDocs documentation site for broken links and save a full report.
---

Guide the user through a broken-link scan of a versioned MkDocs documentation site. Follow the steps below in order.

## Step 0 — Check prerequisites

The scan runs a bundled Python script via `uv`, which manages the script's
dependencies automatically. Verify `uv` is available before going further:

!`uv --version 2>&1 || true`

If the command is not found, stop and tell the user:

> `linkcheck` needs [`uv`](https://docs.astral.sh/uv/) on your PATH to run.
> Install it with `curl -LsSf https://astral.sh/uv/install.sh | sh` (or see the
> docs), then run `/linkcheck` again.

Do not proceed to Step 1 until `uv` reports a version.

## Step 1 — Choose a site

Ask the user for the root URL of the versioned MkDocs site to scan (for example, `https://docs.example.com/project`).

If a `linkcheck-sites.md` file exists in the current directory, read it and present its entries as a numbered menu (one `Label | URL` per line), while always allowing a custom URL as well. This is an optional convenience for teams that scan the same sites regularly — the skill works fine without it.

## Step 2 — Ignore prefixes

`http://127.0.0.1`, `http://localhost`, and `http://0.0.0.0` are always suppressed automatically — no action needed for these.

Ask the user whether any URL prefixes should be ignored. The most common case is private or gated links that return 404/403 for anonymous users — private GitHub repositories, staging hosts, or intranet URLs — which would otherwise show up as false-positive broken links. Collect any prefixes they name; each becomes an `--ignore PREFIX` flag.

## Step 3 — Version filter

Ask whether to check all published versions (default) or only specific ones. If specific, collect the version strings (e.g. `1.3.1`). Warn the user that scanning all versions of a large site can take 5–15 minutes.

## Step 4 — Output filename

Suggest a default filename in the current directory: `<site-slug>-YYYY-MM-DD.txt` using a slug derived from the site host and today's date (e.g. `project-2026-05-05.txt`). Confirm or let the user change it.

## Step 5 — Confirm and run

Show the complete command you are about to run. Ask the user to confirm before proceeding.

Build the command as follows:
- Start with: `uv run "${CLAUDE_PLUGIN_ROOT}/linkcheck.py"`
- Always add `--no-color` (output goes to a file)
- Add `--ignore PREFIX` for each ignore prefix the user selected
- Add `-v VERSION` for each specific version (omit entirely if checking all versions)
- Append the site URL as the final positional argument
- Redirect both stdout and stderr through `tee OUTPUT_FILE` so the user can watch progress while the result is saved

Example, ignoring two private URL prefixes, all versions, output to file:

```
uv run "${CLAUDE_PLUGIN_ROOT}/linkcheck.py" \
  --no-color \
  --ignore https://github.com/example-org/private-repo \
  --ignore https://staging.example.com \
  https://docs.example.com/project \
  2>&1 | tee project-2026-05-05.txt
```

Run this command with a bash timeout of at least 600 seconds.

## Step 6 — Report and next steps

After the run completes, extract from the output and report:
- Which versions were checked and how many pages per version
- Total unique links checked across all versions
- Total broken links found
- Path to the saved report file

Then suggest concrete next steps:
- Open the report file to review broken links by version
- Fix or remove broken links in the source docs, then re-run with `-v VERSION` to verify a single version
- Add further `--ignore PREFIX` flags for any false positives (e.g. additional private repos or staging hosts)
- If the broken count is unexpectedly high, check whether private GitHub repo links are slipping through without an ignore rule
