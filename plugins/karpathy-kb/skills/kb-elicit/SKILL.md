---
name: kb-elicit
description: Conducts a structured interview to capture tacit knowledge missing from the knowledge base, saves it as a cited raw source, and compiles it into the wiki.
---

This skill runs from the knowledge base root directory (where `CLAUDE.md` lives).

Read `./CLAUDE.md` fully before taking any action.

Run this when coverage is thin and the missing knowledge is tacit, cultural, or
experiential rather than something that could simply be looked up. Can be
invoked explicitly by the user or triggered after a coverage check before a
complex task.

## Phase 1 — Gap inventory
1. If a coverage check has not been run, run `/kb-coverage-check` now.
2. Classify each gap:
   - **Document gap** — resolvable if the user provides a specific resource
     (name it specifically, not generically).
   - **Tacit gap** — cultural/experiential knowledge only the user can
     articulate.
3. Enter plan mode. Present the elicitation plan: the task, the document gaps
   (what you're asking for and why), the tacit themes you'll explore, and a
   rough scope. Ask the user to confirm, cut, or add themes. Exit plan mode
   only on approval.

## Phase 2 — Document collection
For each document gap the user will fill: ask them to paste/attach/describe it,
read it, note what it resolves and what it leaves open. Fold new questions into
Phase 3. Record any unfilled gap as unresolved.

## Phase 3 — Structured interview
For tacit gaps, interview: one theme at a time, two or three questions per
theme, follow up when an answer opens something unexpected, periodically
reflect back ("So the key point is X — right?"), and stop when you have enough.
Do not over-interview.

## Phase 4 — Capture
1. Write to `raw/misc/YYYY-MM-DD_elicitation_[task-slug].md`. Use
   `raw/misc/TEMPLATE_elicitation.md` as the format if it exists; otherwise the
   frontmatter must include: `type: misc`, `doc_type: elicitation`, a filled
   `topics:` list, the user's name as `author`, the date, and `compiled: false`.
2. Attribute all statements to the user by name (ask if unknown).
3. Register and compile the new source by running `/kb-add` on the new file,
   then `/kb-compile`.

## Phase 5 — Confirm and proceed
Tell the user what you now know that you didn't, what gaps remain and why, and
whether you now have enough grounding. Then proceed with the task, or ask
whether to proceed with caveats.
