#!/usr/bin/env python3
"""
sync-registry.py — bulk-register raw/ source files into raw/_registry.md.

Scans raw/transcripts/, raw/slack/, raw/decks/, and raw/misc/ for .md files
not yet in the registry. Parses their frontmatter, validates required fields,
and appends new rows with compiled: false. Schema-generic: sources are keyed by
a free-form `topics:` list (no fixed vocabulary).

Usage:
  python3 sync-registry.py [--dry-run] [--vault-root PATH]

Exit codes:
  0 — registry already up to date, nothing to do
  1 — new sources registered (or --dry-run found unregistered files)
  2 — frontmatter errors found (files skipped, manual fix required)
"""

import argparse
import re
import sys
from pathlib import Path

RAW_SUBDIRS = ['transcripts', 'slack', 'decks', 'misc']
VALID_TYPES = {'transcript', 'slack', 'deck', 'misc'}
SOURCE_ID_RE = re.compile(r'^\d{4}-\d{2}-\d{2}_\w+_[\w-]+$')
DATE_RE = re.compile(r'^\d{4}-\d{2}-\d{2}$')


# ---------------------------------------------------------------------------
# Frontmatter parser
# ---------------------------------------------------------------------------

def parse_frontmatter(text: str) -> dict:
    """Parse YAML-lite frontmatter. Handles scalar values and flat lists."""
    if not text.startswith('---'):
        return {}
    end = text.find('\n---', 3)
    if end == -1:
        return {}
    result = {}
    current_list_key = None
    for line in text[4:end].splitlines():
        if not line.strip() or line.strip().startswith('#'):
            continue
        if line.startswith('  - ') or (line.startswith('- ') and current_list_key):
            val = line.strip().lstrip('- ').strip().strip('"\'')
            if current_list_key and isinstance(result.get(current_list_key), list):
                result[current_list_key].append(val)
        elif ':' in line and not line.startswith(' '):
            key, _, val = line.partition(':')
            key = key.strip()
            val = val.strip().strip('"\'')
            current_list_key = None
            if val:
                # Inline list syntax: `key: []` or `key: [a, b]`.
                if val.startswith('[') and val.endswith(']'):
                    inner = val[1:-1].strip()
                    result[key] = [x.strip().strip('"\'') for x in inner.split(',') if x.strip()] if inner else []
                else:
                    result[key] = val
            else:
                result[key] = []
                current_list_key = key
    return result


# ---------------------------------------------------------------------------
# Registry helpers
# ---------------------------------------------------------------------------

def load_registered_ids(registry_path: Path) -> set:
    if not registry_path.exists():
        return set()
    ids = set()
    header_seen = False
    for line in registry_path.read_text().splitlines():
        s = line.strip()
        if s.startswith('| id |'):
            header_seen = True
            continue
        if header_seen and s.startswith('|') and not s.startswith('|--'):
            cells = [c.strip() for c in s.split('|')]
            if len(cells) >= 2 and cells[1] and not cells[1].startswith('_'):
                ids.add(cells[1])
    return ids


def append_registry_rows(registry_path: Path, sources: list):
    """Append rows after the last existing table line (header, separator, or
    data row — whichever is last). Works whether or not the registry already
    has data rows and whether or not it uses a placeholder row."""
    text = registry_path.read_text()
    placeholder = '| _(none yet — add entries here)_ | | | | | | |'
    rows = [
        f"| {s['id']} | {s['path']} | {s['type']} | {s['date']} "
        f"| {s['topics']} | false | |"
        for s in sources
    ]
    if placeholder in text:
        # Replace the placeholder with the first row, append the rest below it.
        text = text.replace(placeholder, rows[0])
        remaining = rows[1:]
    else:
        remaining = rows

    if remaining:
        lines = text.splitlines(keepends=True)
        # Insert after the last table line. Include the separator (|--...) so a
        # fresh registry (header + separator only) appends AFTER the separator,
        # not between it and the header.
        table_line_idxs = [i for i, ln in enumerate(lines) if ln.lstrip().startswith('|')]
        insert_at = (table_line_idxs[-1] + 1) if table_line_idxs else len(lines)
        for row in reversed(remaining):
            lines.insert(insert_at, row + '\n')
        text = ''.join(lines)

    registry_path.write_text(text)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(
        description='Bulk-register raw/ source files into raw/_registry.md.')
    ap.add_argument('--dry-run', action='store_true',
                    help='Report unregistered files without modifying the registry.')
    ap.add_argument('--vault-root', type=Path, default=Path('.'),
                    help='Vault root directory (default: cwd).')
    args = ap.parse_args()

    vault_root = args.vault_root.resolve()
    dry_run = args.dry_run
    registry_path = vault_root / 'raw' / '_registry.md'

    registered = load_registered_ids(registry_path)
    new_sources = []
    errors = []

    for subdir_name in RAW_SUBDIRS:
        subdir = vault_root / 'raw' / subdir_name
        if not subdir.exists():
            continue
        for md in sorted(subdir.glob('*.md')):
            if md.name.startswith('TEMPLATE_') or md.name.startswith('_'):
                continue

            fm = parse_frontmatter(md.read_text())
            source_id = str(fm.get('source_id', md.stem)).strip().strip('"\'')

            if source_id in registered:
                continue

            # Validate
            errs = []
            if not SOURCE_ID_RE.match(source_id):
                errs.append(f"source_id '{source_id}' must match YYYY-MM-DD_type_slug")
            src_type = str(fm.get('type', '')).strip()
            if src_type not in VALID_TYPES:
                errs.append(f"type '{src_type}' must be one of {sorted(VALID_TYPES)}")
            date = str(fm.get('date', '')).strip().strip('"\'')
            if not DATE_RE.match(date):
                errs.append(f"date '{date}' must be YYYY-MM-DD")
            topics = fm.get('topics', [])
            if isinstance(topics, str):
                topics = [topics]
            topics = [t.strip() for t in topics if t.strip()]
            if not topics:
                errs.append("topics list is empty")

            rel = str(md.relative_to(vault_root))
            if errs:
                errors.append((rel, errs))
                continue

            new_sources.append({
                'id': source_id,
                'path': rel,
                'type': src_type,
                'date': date,
                'topics': ', '.join(topics),
            })

    # ── Output ──────────────────────────────────────────────────────────────
    exit_code = 0

    if errors:
        print(f'FRONTMATTER ERRORS — {len(errors)} file(s) skipped (fix before registering):\n')
        for rel, errs in errors:
            print(f'  {rel}')
            for e in errs:
                print(f'    • {e}')
        print()
        exit_code = 2

    if not new_sources:
        if not errors:
            print('raw/_registry.md is up to date — no new sources found.')
        else:
            print('No valid new sources to register.')
        sys.exit(exit_code)

    print(f'{"[dry run] " if dry_run else ""}{len(new_sources)} new source(s) found:\n')
    for s in new_sources:
        print(f'  {s["id"]}')
        print(f'    path:   {s["path"]}')
        print(f'    type:   {s["type"]}')
        print(f'    date:   {s["date"]}')
        print(f'    topics: {s["topics"]}')
        print()

    if dry_run:
        print('Run without --dry-run to register them.')
    else:
        append_registry_rows(registry_path, new_sources)
        print('Registry updated.')
        print('Next step: run /kb-compile to ingest the newly registered sources.')

    sys.exit(max(exit_code, 1))


if __name__ == '__main__':
    main()
