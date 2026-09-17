#!/usr/bin/env python3
"""
lint.py — mechanical lint for a Karpathy-loop knowledge base vault.

Checks (auto-fixes where noted):
  1. Broken wikilinks        [auto-fix: [[target]] → [[MISSING: target]]]
  2. Unknown citation IDs    [report only — cannot infer correct ID]
  3. Uncited articles        [auto-fix: prepend [!uncited] callout]
  4. Index drift             [auto-fix: add stub row to nearest _index.md]
  5. Resolved conflicts      [auto-fix: move block to ## Resolved]
  6. Supersession integrity  [report only — claims citing superseded sources
                              that are not yet marked [!superseded]]

Usage:
  python tools/lint.py [--dry-run] [--vault-root PATH]

Exit code 0 = clean (or dry-run with no issues). Exit code 1 = issues found.
"""

import argparse
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Patterns
# ---------------------------------------------------------------------------

# [[target]] or [[target|display]] or [[target\|display]] (table-escaped pipe).
# Negative lookahead skips already-marked [[MISSING: ...]] links.
# Group 1 = path/target only (no display text, no trailing whitespace).
WIKILINK_RE = re.compile(r'\[\[(?!MISSING:)([^\]|\\]+?)(?:\\?\|[^\]]+?)?\]\]')

# `[Person Name, source-id, YYYY-MM-DD]` inline citation.
# Group 1 = full inner text; source-id is fields[1] after splitting on ', '.
CITATION_RE = re.compile(r'`\[([^\]]+)\]`')

# HTML comment blocks — content inside these is ignored by all checks.
HTML_COMMENT_RE = re.compile(r'<!--.*?-->', re.DOTALL)


def comment_spans(text: str) -> list:
    """Return list of (start, end) byte ranges for HTML comment blocks."""
    return [(m.start(), m.end()) for m in HTML_COMMENT_RE.finditer(text)]


def in_comment(pos: int, spans: list) -> bool:
    return any(s <= pos < e for s, e in spans)

UNCITED_CALLOUT = (
    '> [!uncited]\n'
    '> This article has no citations yet. Run a compile pass to populate it from raw sources.\n'
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# Meta files that live under wiki/ but are registries, not claims articles —
# exempt from the uncited-article check.
META_FILENAMES = {'org-and-people.md'}


def is_article(path: Path) -> bool:
    """True for wiki .md files that are substantive articles (not templates or meta files)."""
    return (
        path.suffix == '.md'
        and not path.name.startswith('TEMPLATE_')
        and not path.name.startswith('_')
        and path.name not in META_FILENAMES
    )


def parse_registry(vault_root: Path) -> set:
    """Return the set of source-ids registered in raw/_registry.md."""
    reg = vault_root / 'raw' / '_registry.md'
    if not reg.exists():
        return set()
    ids = set()
    header_seen = False
    for line in reg.read_text().splitlines():
        s = line.strip()
        if s.startswith('| id |'):
            header_seen = True
            continue
        if header_seen and s.startswith('|') and not s.startswith('|--'):
            cells = [c.strip() for c in s.split('|')]
            if len(cells) >= 2:
                sid = cells[1]
                # Skip placeholder rows
                if sid and not sid.startswith('_'):
                    ids.add(sid)
    return ids


def resolve_wikilink(target: str, vault_root: Path) -> Path:
    """Convert a wikilink target string to the expected filesystem path."""
    p = Path(target.strip())
    if not p.suffix:
        p = p.with_suffix('.md')
    return vault_root / p


def insert_after_frontmatter(text: str, callout: str) -> str:
    """Insert a callout block immediately after the closing '---' of YAML frontmatter."""
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != '---':
        return callout + '\n' + text
    close_idx = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == '---':
            close_idx = i
            break
    if close_idx is None:
        return text + '\n' + callout
    insert_at = close_idx + 1
    # Skip blank lines immediately following frontmatter
    while insert_at < len(lines) and not lines[insert_at].strip():
        insert_at += 1
    lines.insert(insert_at, '\n' + callout + '\n')
    return ''.join(lines)


# ---------------------------------------------------------------------------
# Check 1 — broken wikilinks
# ---------------------------------------------------------------------------

def check_wikilinks(vault_root: Path, dry_run: bool) -> list:
    issues = []
    for md in (vault_root / 'wiki').rglob('*.md'):
        if md.name.startswith('TEMPLATE_'):
            continue
        text = md.read_text()
        spans = comment_spans(text)
        patched = text
        for m in WIKILINK_RE.finditer(text):
            if in_comment(m.start(), spans):
                continue
            target = m.group(1)
            if not resolve_wikilink(target, vault_root).exists():
                rel = md.relative_to(vault_root)
                issues.append(f'  BROKEN LINK  {rel}: [[{target}]]')
                if not dry_run:
                    old = m.group(0)
                    new = old.replace('[[' + target, '[[MISSING: ' + target, 1)
                    patched = patched.replace(old, new, 1)
        if not dry_run and patched != text:
            md.write_text(patched)
    return issues


# ---------------------------------------------------------------------------
# Check 2 — citation source-ids not in registry
# ---------------------------------------------------------------------------

def check_citations(vault_root: Path, source_ids: set) -> list:
    issues = []
    for md in (vault_root / 'wiki').rglob('*.md'):
        if md.name.startswith('TEMPLATE_'):
            continue
        text = md.read_text()
        spans = comment_spans(text)
        for m in CITATION_RE.finditer(text):
            if in_comment(m.start(), spans):
                continue
            fields = [f.strip() for f in m.group(1).split(',')]
            if len(fields) >= 2:
                sid = fields[1]
                if sid and sid not in source_ids:
                    rel = md.relative_to(vault_root)
                    issues.append(f"  UNKNOWN SOURCE-ID  {rel}: '{sid}'")
    return issues


# ---------------------------------------------------------------------------
# Check 3 — uncited articles
# ---------------------------------------------------------------------------

def check_uncited(vault_root: Path, dry_run: bool) -> list:
    issues = []
    for md in (vault_root / 'wiki').rglob('*.md'):
        if not is_article(md):
            continue
        text = md.read_text()
        if not CITATION_RE.search(text) and '[!uncited]' not in text:
            rel = md.relative_to(vault_root)
            issues.append(f'  UNCITED  {rel}')
            if not dry_run:
                md.write_text(insert_after_frontmatter(text, UNCITED_CALLOUT))
    return issues


# ---------------------------------------------------------------------------
# Check 4 — index drift
# ---------------------------------------------------------------------------

def check_index_drift(vault_root: Path, dry_run: bool) -> list:
    issues = []
    for index_file in (vault_root / 'wiki').rglob('_index.md'):
        dir_path = index_file.parent
        # Accumulate all missing entries before writing, so we write once per index
        missing = []
        index_text = index_file.read_text()
        for md in sorted(dir_path.glob('*.md')):
            if not is_article(md):
                continue
            if md.stem not in index_text:
                rel = md.relative_to(vault_root)
                issues.append(f'  DRIFT  {rel} not listed in {index_file.relative_to(vault_root)}')
                missing.append(md)

        if missing and not dry_run:
            lines = index_text.splitlines(keepends=True)
            # Find the last table data row (starts with | but not a separator |---)
            last_tbl = max(
                (i for i, ln in enumerate(lines)
                 if ln.startswith('|') and not ln.startswith('|--')),
                default=len(lines) - 1,
            )
            for md in reversed(missing):
                link = str(md.relative_to(vault_root).with_suffix(''))
                row = f'| [[{link}|{md.stem}]] | _(to be summarized)_ | _(not yet compiled)_ |\n'
                lines.insert(last_tbl + 1, row)
            index_file.write_text(''.join(lines))

    return issues


# ---------------------------------------------------------------------------
# Check 5 — resolved conflict entries
# ---------------------------------------------------------------------------

# Each conflict block runs from a ### CONFLICT-NNN heading until just before
# the next such heading, a ## section, or end-of-string.
CONFLICT_BLOCK_RE = re.compile(
    r'(### CONFLICT-\d+.*?)(?=\n### CONFLICT-\d+|\n## |\Z)',
    re.DOTALL,
)


def check_resolved_conflicts(vault_root: Path, dry_run: bool) -> list:
    cf = vault_root / 'wiki' / '_conflicts.md'
    if not cf.exists():
        return []
    text = cf.read_text()
    issues = []
    resolved_blocks = []

    for m in CONFLICT_BLOCK_RE.finditer(text):
        block = m.group(1)
        if re.search(r'-\s+\*\*Status\*\*:\s+resolved', block, re.IGNORECASE):
            headline = block.splitlines()[0].strip()
            issues.append(f'  RESOLVED CONFLICT  {headline}')
            resolved_blocks.append(block)

    if resolved_blocks and not dry_run:
        new_text = text
        for block in resolved_blocks:
            new_text = new_text.replace(block, '')
        joined = '\n\n'.join(b.strip() for b in resolved_blocks)
        if '_(none yet)_' in new_text:
            new_text = new_text.replace(
                '## Resolved\n\n_(none yet)_',
                f'## Resolved\n\n{joined}\n',
            )
        else:
            new_text = re.sub(r'(## Resolved\n)', r'\1\n' + joined + '\n\n', new_text)
        cf.write_text(new_text)

    return issues


# ---------------------------------------------------------------------------
# Check 6 — supersession integrity
# ---------------------------------------------------------------------------

def load_supersession_map(vault_root: Path) -> dict:
    """Return {superseded-source-id: superseding-source-id} from all raw sources."""
    mapping = {}
    for subdir in ['transcripts', 'slack', 'decks', 'misc']:
        d = vault_root / 'raw' / subdir
        if not d.exists():
            continue
        for md in d.glob('*.md'):
            if md.name.startswith('TEMPLATE_') or md.name.startswith('_'):
                continue
            fm = {}
            text = md.read_text()
            if not text.startswith('---'):
                continue
            end = text.find('\n---', 3)
            if end == -1:
                continue
            current_list_key = None
            for line in text[4:end].splitlines():
                if not line.strip():
                    continue
                if (line.startswith('  - ') or line.startswith('- ')) and current_list_key:
                    val = line.strip().lstrip('- ').strip().strip('"\'')
                    if val and isinstance(fm.get(current_list_key), list):
                        fm[current_list_key].append(val)
                elif ':' in line and not line.startswith(' '):
                    key, _, val = line.partition(':')
                    key = key.strip()
                    val = val.strip().strip('"\'')
                    current_list_key = None
                    if val:
                        fm[key] = val
                    else:
                        fm[key] = []
                        current_list_key = key
            supersedes = fm.get('supersedes', [])
            if isinstance(supersedes, str):
                supersedes = [supersedes]
            source_id = fm.get('source_id', md.stem).strip().strip('"\'')
            for old_id in supersedes:
                old_id = old_id.strip()
                if old_id:
                    mapping[old_id] = source_id
    return mapping


def check_supersession_integrity(vault_root: Path, source_ids: set) -> list:
    """Check 6: wiki claims citing superseded source-ids not marked [!superseded]."""
    supersession_map = load_supersession_map(vault_root)
    if not supersession_map:
        return []

    issues = []
    for md in (vault_root / 'wiki').rglob('*.md'):
        if md.name.startswith('TEMPLATE_'):
            continue
        text = md.read_text()
        spans = comment_spans(text)
        for m in CITATION_RE.finditer(text):
            if in_comment(m.start(), spans):
                continue
            fields = [f.strip() for f in m.group(1).split(',')]
            if len(fields) < 2:
                continue
            sid = fields[1]
            if sid in supersession_map:
                # Check whether this citation is already inside a [!superseded] block
                # by looking at the preceding ~200 chars for the callout marker
                preceding = text[max(0, m.start() - 200):m.start()]
                if '[!superseded]' not in preceding:
                    rel = md.relative_to(vault_root)
                    new_id = supersession_map[sid]
                    issues.append(
                        f"  UNMARKED SUPERSESSION  {rel}: "
                        f"citation '{sid}' superseded by '{new_id}' but not marked [!superseded]"
                    )
    return issues


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description='Mechanical lint for a Karpathy-loop knowledge base vault.')
    ap.add_argument('--dry-run', action='store_true',
                    help='Report issues without modifying any files.')
    ap.add_argument('--vault-root', type=Path, default=Path('.'),
                    help='Path to the vault root (default: current directory).')
    args = ap.parse_args()

    vault_root = args.vault_root.resolve()
    dry_run = args.dry_run
    mode = ' (dry run)' if dry_run else ''

    print(f'KB Lint{mode} — {vault_root}\n')

    source_ids = parse_registry(vault_root)

    checks = [
        ('Broken wikilinks',        lambda: check_wikilinks(vault_root, dry_run)),
        ('Citation integrity',      lambda: check_citations(vault_root, source_ids)),
        ('Uncited articles',        lambda: check_uncited(vault_root, dry_run)),
        ('Index drift',             lambda: check_index_drift(vault_root, dry_run)),
        ('Resolved conflicts',      lambda: check_resolved_conflicts(vault_root, dry_run)),
        ('Supersession integrity',  lambda: check_supersession_integrity(vault_root, source_ids)),
    ]

    total = 0
    for title, fn in checks:
        print(f'=== {title} ===')
        found = fn()
        if found:
            print('\n'.join(found))
        else:
            print('  OK')
        total += len(found)
        print()

    print('─' * 48)
    summary = f'{total} issue(s) found'
    if dry_run and total:
        summary += ' — no files modified'
    print(summary)
    sys.exit(1 if total else 0)


if __name__ == '__main__':
    main()
