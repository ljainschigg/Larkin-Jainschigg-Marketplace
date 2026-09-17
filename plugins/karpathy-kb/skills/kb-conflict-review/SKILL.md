---
name: kb-conflict-review
description: Read-only triage of open conflicts in the knowledge base — summarizes each disagreement and suggests a human action, without modifying anything.
---

This skill runs from the knowledge base root directory (where `CLAUDE.md` lives).

Read `./CLAUDE.md` fully before taking any action.

This is a **read-only** analysis pass. It produces a triage report and does
NOT modify any files, does NOT pick a winner, and does NOT resolve conflicts.

## Steps

1. Read `wiki/_conflicts.md` and list all open conflicts.
2. If there are no open conflicts, report that and stop.
3. For each open conflict:
   a. Read the article section where the conflict appears.
   b. Read the two (or more) raw source documents underlying it.
   c. Summarize the disagreement in plain language.
   d. Note the relative recency of each source and the roles/seniority of the
      people making each claim.
   e. Note whether one source is formal (deck/spec) vs. informal (Slack/transcript).
   f. Note if one claim is stated intent rather than observed fact.
4. Produce a triage report per conflict:
   - What the disagreement is about.
   - Which claim appears more recent or authoritative, and why.
   - A suggested human action (e.g. "ask @handle to clarify", "check whether
     source-B supersedes source-A", "may be resolved by a newer source not yet
     compiled").
5. Do NOT modify `wiki/_conflicts.md` or any article. Analysis only.
