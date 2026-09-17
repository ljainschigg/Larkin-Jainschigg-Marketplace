---
name: kb-coverage-check
description: Assesses whether the knowledge base has enough compiled, cited coverage to answer a given question before answering it, and flags gaps.
---

This skill runs from the knowledge base root directory (where `CLAUDE.md` lives).

Read `./CLAUDE.md` fully before taking any action.

## What this skill does

It evaluates, before you answer a substantive question, whether the wiki has
sufficient information to support a good answer — and tells the user where it
does not. A project may reference multiple KBs; check all of them.

## Steps

1. If operating in a project context, read the project `CLAUDE.md` to identify
   all listed KBs and their paths. If operating directly inside a single KB,
   that KB is the only one to check.

2. For each KB, read its `wiki/_index.md` to see what topic areas are covered
   and when each was last compiled.

3. Identify which KB(s) and which articles are relevant to the user's question.

4. For each relevant topic area, rate coverage:
   - **Strong** — articles exist, are compiled, have multiple cited sources.
   - **Thin** — stubs, `[!uncited]` warnings, or a single informal source only.
   - **Missing** — topic absent from all listed KBs.

5. For topics missing from all KBs, rate the training fallback explicitly:
   **Training: usable** (may be stale / lack internal context),
   **Training: weak**, or **Training: none** (internal/proprietary — cannot
   answer without a KB source).

6. Produce a coverage report before answering:

   > **Coverage for this question:**
   > KB: [name] (`path`)
   > - [Topic A]: strong — N sources compiled
   > - [Topic B]: thin — stub only
   > Not covered by any KB:
   > - [Topic C]: training fallback — usable but may be stale
   > [One-sentence verdict: answerable reliably / partially / not at all.]

7. If coverage is sufficient, proceed to answer, prefixing each citation with
   the KB name when more than one KB is in play:
   `[Person, source-id, date] — via [KB name]`.

8. If coverage is insufficient, tell the user what is lacking, then decide:
   - **Suggest adding a KB** when a whole domain is missing and recurring.
   - **Escalate to /kb-elicit** when the task is complex/high-stakes, the gaps
     are central, and the missing knowledge is tacit/undocumented.
   - **Use training with an explicit caveat** for well-known public topics on
     low-stakes questions the user accepts at lower confidence.

## When to skip

Meta questions about the KB itself, purely mechanical requests (run lint,
compile), and brainstorming where the user is not asking for grounded facts.
