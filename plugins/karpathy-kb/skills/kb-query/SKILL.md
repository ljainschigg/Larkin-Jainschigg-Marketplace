---
name: kb-query
description: Answers a question against the knowledge base wiki, preserving full provenance and flagging conflicts.
---

This skill runs from the knowledge base root directory (where `CLAUDE.md` lives).

Read `./CLAUDE.md` fully before taking any action. It contains all query rules, provenance requirements, and output conventions for this knowledge base.

## What this skill does

It answers a question using only the compiled wiki — no speculation, no claims beyond what sources say, full attribution throughout.

## Input

The user's question is the argument passed to this skill. If no question was provided, ask for one.

## Steps

Follow the **Query Workflow** in `./CLAUDE.md` exactly:

1. Read `wiki/_index.md` to identify which topic areas and articles are relevant to the question.

2. Read only the relevant articles — do not load the entire wiki.

3. Synthesize a clear answer that:
   - Preserves provenance: cite `[Person, source-id, date]` for every claim
   - Flags any open conflicts from `wiki/_conflicts.md` that bear on the answer
   - Rates confidence:
     - **High** — multiple independent sources agree, at least one formal (deck/spec)
     - **Medium** — one formal source, or multiple informal sources agreeing
     - **Low** — single informal source (Slack/transcript), no corroboration
   - Notes where information is absent from the wiki (not "unknown" — "not yet compiled")

4. Save the answer to `qa/[YYYY-MM-DD]_[short-slug].md` using the template format from `qa/TEMPLATE_qa.md`.

5. Add the new entry to `qa/_index.md`.

6. Do NOT modify any wiki articles during this pass.

7. Report to the user: where the Q&A file was saved and the confidence rating.
