#!/usr/bin/env python3
"""
create-vault.py — deterministically scaffold a Karpathy-loop knowledge base.

Emits the invariant skeleton the bundled tooling depends on (raw/ subdirs, the
exact raw/_registry.md header, wiki index/conflict/source files, the source and
article templates, and a CLAUDE.md generated from the operating manual), plus
the caller's custom parameters (name, description, topic areas, owner).

This is the layer that MUST be exact — sync-registry.py and lint.py key off the
registry columns and template frontmatter field names. Custom prose (the KB's
purpose, per-topic detail) is layered on afterward by the /kb-setup dialogue.

Usage:
  python3 create-vault.py TARGET_DIR --name "KB Name" --topics a,b,c \
      [--description "..."] [--owner "Name/Team"] [--guide PATH]

Exit codes:
  0 — vault created
  1 — target exists and is non-empty, or bad arguments
"""

import argparse
import re
import sys
from pathlib import Path

RAW_SUBDIRS = ['transcripts', 'slack', 'decks', 'misc']

REGISTRY = """\
---
title: "Raw Source Registry"
description: "Index of all raw source documents."
last_updated: ""
---

# Raw Source Registry

| id | path | type | date | topics | compiled | compiled_date |
|----|------|------|------|--------|----------|---------------|
"""

TEMPLATE_TRANSCRIPT = """\
---
source_id: "YYYY-MM-DD_transcript_[slug]"
type: transcript
date: "YYYY-MM-DD"
meeting_type: "[sync | review | interview | other]"
topics: []
participants:
  - "[Full Name] (@handle)"
compiled: false
compiled_date: ""
context: "[One sentence: what this meeting was about]"
---

[Paste transcript here]
"""

TEMPLATE_SLACK = """\
---
source_id: "YYYY-MM-DD_slack_[channel]-[slug]"
type: slack
channel: "#[channel-name]"
date_range: "YYYY-MM-DD to YYYY-MM-DD"
topics: []
participants:
  - "@handle"
compiled: false
compiled_date: ""
context: "[One sentence: what thread or topic this covers]"
---

[Paste Slack thread here, preserving timestamp and handle structure]
"""

TEMPLATE_DECK = """\
---
source_id: "YYYY-MM-DD_deck_[slug]"
type: deck
date: "YYYY-MM-DD"
author: "[Full Name]"
audience: "[internal | customer | conference | other]"
event: "[Event or meeting name]"
topics: []
compiled: false
compiled_date: ""
context: "[One sentence: what this deck covered]"
---

--- SLIDE 1 ---
[Slide content]

NOTES:
[Speaker notes if available]

--- SLIDE 2 ---
[Continue...]
"""

TEMPLATE_MISC = """\
---
source_id: "YYYY-MM-DD_misc_[slug]"
type: misc
doc_type: "[engineering-spec | design-doc | blog-post | email | external-article | other]"
date: "YYYY-MM-DD"
author: "[Full Name or Org]"
topics: []
compiled: false
compiled_date: ""
context: "[One sentence: what this document is]"
---

[Document content here]
"""

TEMPLATE_ELICITATION = """\
---
source_id: "YYYY-MM-DD_misc_elicitation-[slug]"
type: misc
doc_type: elicitation
date: "YYYY-MM-DD"
author: "[Full Name of the person interviewed]"
topics: []
compiled: false
compiled_date: ""
context: "[One sentence: what task/gap this elicitation addressed]"
---

[Structured capture of the interview. Attribute every statement to the author
by name. One point per paragraph; keep the author's own framing.]
"""

TEMPLATE_ARTICLE = """\
---
title: "[Article Title]"
area: "[topic area]"
tags: []
version: ""
last_compiled: ""
sources_used: []
superseded_sources: []
---

# [Article Title]

> [!uncited]
> This article has no citations yet. Run a compile pass to populate it from raw sources.

## Summary

_(To be compiled from raw sources.)_

## Related

- [[wiki/cross-cutting/org-and-people|People]]
"""

TEMPLATE_QA = """\
---
question: ""
date: "YYYY-MM-DD"
areas_consulted: []
confidence: "High | Medium | Low"
---

# Q&A: [Question]

_Date: YYYY-MM-DD_

## Answer

[Answer with provenance citations]

## Confidence

**[High | Medium | Low]** — [rationale]

## Sources consulted

[List of wiki articles and raw sources referenced]

## Open conflicts relevant to this answer

[Any conflicts from wiki/_conflicts.md that bear on this answer]
"""

CONFLICTS = """\
---
title: "Conflicts Log"
description: "Contradictory claims awaiting human triage."
---

# Conflicts Log

## Open

_(none yet)_

## Resolved

_(none yet)_
"""

SOURCES = """\
---
title: "Source Inventory"
description: "Aggregated inventory of compiled sources."
---

# Source Inventory

_(Populated during compile passes.)_
"""

QA_INDEX = """\
# Q&A Index

| Date | Question | Confidence | File |
|------|----------|------------|------|
"""


def slugify(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r'[^a-z0-9]+', '-', s)
    return s.strip('-')


def wiki_index(name, description, areas):
    area_lines = "\n".join(
        f"- [[wiki/{slug}/_index|{label}]]" for label, slug in areas
    ) or "_(No topic areas yet.)_"
    return f"""\
---
title: "Knowledge Base Index"
description: "{description}"
last_updated: ""
---

# {name} — Knowledge Base

## Topic areas

{area_lines}
- [[wiki/cross-cutting/_index|Cross-cutting]]

## Stats

- Sources compiled: 0
- Articles: 0
- Open conflicts: 0
"""


def area_index(label):
    return f"""\
---
title: "{label}"
description: "Compiled knowledge for {label}."
---

# {label}

_(Articles appear here as sources are compiled.)_
"""


def crosscutting_index():
    return """\
---
title: "Cross-cutting"
description: "Topics that span multiple areas."
---

# Cross-cutting

- [[wiki/cross-cutting/org-and-people|Org and People]]
"""


def org_and_people(owner):
    owner_row = f"| {owner} | | | [added at setup] |" if owner else "| _(none yet)_ | | | |"
    return f"""\
---
title: "Org and People"
description: "Identity authority — maps full names to handles, affiliations, and roles."
---

# Org and People

This file is the identity authority. All citations use the canonical full name from here.

| Full name | Handle(s) | Role / team | Notes |
|-----------|-----------|-------------|-------|
{owner_row}
"""


def readme(name, description):
    return f"""\
# {name}

{description}

A citation-tracked knowledge base maintained with the **karpathy-kb** plugin.

## Add sources
Drop files into `raw/transcripts/`, `raw/slack/`, `raw/decks/`, or `raw/misc/`
(use the `TEMPLATE_*` files as a guide), then from this directory:

- `/kb-add <path>` — register one file
- `/kb-ingest` — bulk-register everything new at once

## Compile, query, maintain
- `/kb-compile` — extract cited claims into the wiki
- `/kb-query <question>` — answer from compiled content, with provenance
- `/kb-coverage-check` / `/kb-conflict-review` / `/kb-elicit` — assess and fill gaps
- `/kb-lint` — structural checks and auto-fix

All commands run from this directory (the one containing `CLAUDE.md`).
"""


def build_claude_md(name, description, areas, owner, guide_text):
    area_map = "\n".join(f"| `wiki/{slug}/` | {label} |" for label, slug in areas)
    preamble = f"""\
# {name} — Knowledge Base

{description}

**Maintained by:** {owner or "[unset]"}

**Topic areas:**

| Path | Area |
|------|------|
{area_map}
| `wiki/cross-cutting/` | Topics spanning multiple areas |

This knowledge base follows the Karpathy-loop workflow. The operating manual
below governs every Claude operation here — read it fully before acting.

---

"""
    return preamble + guide_text


GITIGNORE = """\
# OS / editor cruft
.DS_Store
Thumbs.db
*.swp

# ── Sensitive source material ──────────────────────────────────────────────
# A knowledge base is often deliberately versioned, so nothing here is ignored
# by default. But raw/ holds your original sources — transcripts, Slack exports,
# decks — which frequently contain personal or proprietary data, and qa/ holds
# answered questions that may embed sensitive queries. Decide deliberately what
# to commit. To keep the sensitive parts local-only, uncomment:
# raw/transcripts/
# raw/slack/
# raw/decks/
# raw/misc/
# qa/
"""


def main():
    ap = argparse.ArgumentParser(description='Scaffold a Karpathy-loop knowledge base.')
    ap.add_argument('target', type=Path, help='Directory to create the vault in.')
    ap.add_argument('--name', required=True, help='KB name.')
    ap.add_argument('--topics', required=True,
                    help='Comma-separated topic areas (become wiki/<slug>/ dirs).')
    ap.add_argument('--description', default='', help='One-line KB description.')
    ap.add_argument('--owner', default='', help='Owner name or team.')
    ap.add_argument('--guide', type=Path,
                    default=Path(__file__).resolve().parent.parent / 'skills' / 'kb-setup' / 'kb-guide.md',
                    help='Path to kb-guide.md (default: bundled copy).')
    args = ap.parse_args()

    target = args.target.expanduser().resolve()
    if target.exists() and any(target.iterdir()):
        print(f"ERROR: target '{target}' exists and is not empty. Refusing to scaffold.",
              file=sys.stderr)
        sys.exit(1)

    labels = [t.strip() for t in args.topics.split(',') if t.strip()]
    if not labels:
        print("ERROR: --topics must list at least one topic area.", file=sys.stderr)
        sys.exit(1)
    areas = []
    seen = set()
    for label in labels:
        slug = slugify(label)
        if not slug or slug in seen or slug == 'cross-cutting':
            continue
        seen.add(slug)
        areas.append((label, slug))

    if not args.guide.exists():
        print(f"ERROR: guide not found at '{args.guide}'. Pass --guide.", file=sys.stderr)
        sys.exit(1)
    guide_text = args.guide.read_text()

    description = args.description or f"Knowledge base for {args.name}."

    # ── Directories ──────────────────────────────────────────────────────────
    for sub in RAW_SUBDIRS:
        (target / 'raw' / sub).mkdir(parents=True, exist_ok=True)
    (target / 'wiki' / 'cross-cutting').mkdir(parents=True, exist_ok=True)
    for _, slug in areas:
        (target / 'wiki' / slug).mkdir(parents=True, exist_ok=True)
    (target / 'qa').mkdir(parents=True, exist_ok=True)

    # ── Files ────────────────────────────────────────────────────────────────
    def w(rel, text):
        (target / rel).write_text(text)

    w('raw/_registry.md', REGISTRY)
    w('raw/transcripts/TEMPLATE_transcript.md', TEMPLATE_TRANSCRIPT)
    w('raw/slack/TEMPLATE_slack.md', TEMPLATE_SLACK)
    w('raw/decks/TEMPLATE_deck.md', TEMPLATE_DECK)
    w('raw/misc/TEMPLATE_misc.md', TEMPLATE_MISC)
    w('raw/misc/TEMPLATE_elicitation.md', TEMPLATE_ELICITATION)

    w('wiki/_index.md', wiki_index(args.name, description, areas))
    w('wiki/_conflicts.md', CONFLICTS)
    w('wiki/_sources.md', SOURCES)
    w('wiki/TEMPLATE_article.md', TEMPLATE_ARTICLE)
    w('wiki/cross-cutting/_index.md', crosscutting_index())
    w('wiki/cross-cutting/org-and-people.md', org_and_people(args.owner))
    for label, slug in areas:
        w(f'wiki/{slug}/_index.md', area_index(label))

    w('qa/_index.md', QA_INDEX)
    w('qa/TEMPLATE_qa.md', TEMPLATE_QA)

    w('CLAUDE.md', build_claude_md(args.name, description, areas, args.owner, guide_text))
    w('README.md', readme(args.name, description))
    w('.gitignore', GITIGNORE)

    # ── Report ───────────────────────────────────────────────────────────────
    print(f"Created knowledge base '{args.name}' at {target}")
    print(f"  topic areas: {', '.join(slug for _, slug in areas) or '(none)'} + cross-cutting")
    print("  next: drop sources into raw/, then run /kb-ingest and /kb-compile from the KB root.")
    sys.exit(0)


if __name__ == '__main__':
    main()
