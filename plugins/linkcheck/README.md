# linkcheck

Scans a versioned MkDocs documentation site for broken links and saves a full report.

Discovers all published versions via `versions.json`, enumerates pages from the navigation sidebar, checks every content link once (cached across versions), and reports broken links grouped by version with anchor text and referencing pages.

---

## Prerequisites

- [`uv`](https://docs.astral.sh/uv/) must be available in your shell. The skill runs the bundled `linkcheck.py` via `uv run`, which manages the script's Python dependencies automatically — no manual `pip install` needed. `/linkcheck` checks for `uv` before it does anything.

## Install

If you haven't added the marketplace yet:

```
/plugin marketplace add ljainschigg/Larkin-Jainschigg-Marketplace
```

Then install the plugin:

```
/plugin install linkcheck@Larkin-Jainschigg-Marketplace
```

## Use

```
/linkcheck
```

Claude will ask you:

1. **Which site** to scan (a URL, or an entry from an optional saved list)
2. **Which URL prefixes to ignore** (private GitHub repos, staging hosts, etc.)
3. **Which versions** to check (all, or specific version strings)
4. **Output filename** for the report (defaults to `<site>-YYYY-MM-DD.txt`)

It then runs the scan, shows live progress, saves the full output to your chosen file, and summarises the results with suggested next steps.

A full multi-version scan typically takes 5–15 minutes depending on site size.

---

## Details

| | |
|---|---|
| **Version** | 1.0.6 |
| **Type** | skill |
| **Maintained by** | Claude Plugins Marketplace |
| **Runtime** | Python via `uv` (dependencies declared inline in `linkcheck.py`) |

---

## CLI Reference

The underlying script can also be run directly for scripting or CI use. Its dependencies are declared inline (PEP 723), so `uv` installs them on first run:

```
uv run linkcheck.py SITE_URL
```

`SITE_URL` is the root of the docs site, e.g. `https://docs.example.com/project`.

### Options

| Flag | Default | Description |
|------|---------|-------------|
| `-w, --workers N` | 10 | Concurrent request workers |
| `-t, --timeout N` | 10 | Request timeout in seconds |
| `-v, --version VER` | all | Check only this version; repeatable |
| `--ignore PREFIX` | — | Skip links starting with PREFIX; repeatable |
| `--no-color` | — | Disable ANSI color output |

`http://127.0.0.1`, `http://localhost`, and `http://0.0.0.0` are always ignored regardless of `--ignore` flags.

### Examples

Check a single version:

```
uv run linkcheck.py -v 1.3.1 https://docs.example.com/project
```

Ignore private GitHub repositories, save output to a file:

```
uv run linkcheck.py \
  --no-color \
  --ignore https://github.com/example-org/private-repo \
  --ignore https://staging.example.com \
  https://docs.example.com/project \
  2>&1 | tee report.txt
```

Exit code is `0` if no broken links are found, `1` otherwise.
