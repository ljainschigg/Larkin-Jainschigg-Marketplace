---
name: briefing
description: Prepare a briefing on a specific person from their Slack activity — what they're working on, who they're engaging, time pressures, and pointed questions to ask. Reads Slack via Claude Code's built-in connector.
---

# briefing

Prepare for a substantive conversation with a specific person by reconstructing what they've been working on and communicating about — drawn entirely from Slack activity you have access to. The goal is to walk in already knowing what they care about.

**Tone:** Informed colleague, not investigator. Surface what the evidence suggests; flag where it's thin. This is personal prep material — treat it accordingly.

## Step 0 — Preflight: Slack connector

This skill relies on Claude Code's **built-in Slack connector** (the `slack_*` MCP tools). There are no plugin-managed credentials.

Confirm the connector is available and authenticated before proceeding: make one lightweight call — `slack_search_users` with the target's name. If the `slack_*` tools are not available at all, or the call returns an authentication error, stop and tell the user:

> This skill needs Claude Code's **Slack connector** to be connected and authenticated. Add it from Claude Code's connector settings (`/mcp`), sign in to your Slack workspace, and make sure the signed-in user can see the person and channels you're briefing on. Then run `/briefing <name>` again.

Do not proceed until a Slack call succeeds.

## Step 1 — Identify the target

Extract the person's name from the user's request. Call `slack_search_users` with their name. If multiple results are returned, present the options and ask the user to confirm. Record the target's `user_id` and Slack username.

## Step 2 — Establish the time window

Ask the user: *"How far back should I look — last 4 weeks, 3 months, longer?"* If they don't specify, default to 6 weeks. Compute the `after` date in YYYY-MM-DD format.

## Step 3 — Collect the target's messages

Call `slack_search_public_and_private` with:
- `query`: `from:<@USER_ID> after:YYYY-MM-DD`
- `sort`: `timestamp`, `sort_dir`: `asc`
- `limit`: 20
- `include_context`: true

Paginate through all results using the cursor. Collect every message.

## Step 4 — Fetch substantive threads

For each collected message that is a **parent message with replies**: call `slack_read_thread` to fetch the full thread. Skip threads with only 1–2 short replies unless the target's contribution was substantial.

For each collected message that is a **thread reply**: fetch the parent thread if not already collected, to get context. Skip if the target's reply is a one-word acknowledgement or reaction.

The goal is signal, not completeness — use judgment about what's worth fetching.

## Step 5 — Extract topics and signals

From all collected messages and threads, identify:

**Topics** — cluster messages by subject matter. Name each cluster concisely (e.g. "billing system rewrite", "ACME partnership integration"). A message may belong to more than one cluster.

**People in orbit** — every person the target @-mentioned, directed messages to, or engaged with in thread exchange. Note frequency.

**Urgency signals** — deadline language: "by Friday", "before the call", "EOQ", "GA", "launch", "demo", "PoC", "beta", "release", explicit dates.

**Initiative type** — tag each cluster: `[Tech Dev]`, `[Partnership]`, `[Sales]`, `[Ops]`, `[Other]`.

## Step 6 — Score and rank topics

For each topic cluster, compute an investment signal from message count, number of distinct people addressed, presence of urgency/deadline language (weighted), and initiative type: `[Tech Dev]`, `[Partnership]`, and `[Sales]` topics surface to the top regardless of message volume. Rank by composite signal; at equal strength, `[Tech Dev]` / `[Partnership]` / `[Sales]` outrank `[Ops]` and `[Other]`.

## Step 7 — Write the briefing

### About [Name]
One or two sentences on their apparent role — drawn only from what's visible in Slack (profile title, channel memberships, how others address them). Note the time window covered.

### What They're Invested In
Ranked list of topics by investment signal. For each:

**Topic name** `[Type]`
What it appears to be, based on the evidence. Who they're engaging with. Any deadline or urgency signals. Date range of activity.
*Flag quietly if the work appears significant but has low internal visibility — active in small channels or DMs but not broadly announced.*

### Their Key Interlocutors
The people they're spending communication energy on during this window. Note the apparent nature of each relationship (collaborating, briefing, seeking input, escalating, managing).

### Time Pressures Visible
Specific deadlines, demos, POCs, or deliverables surfaced in the messages, with dates where visible.

### Questions Worth Asking
3–5 pointed questions derived directly from what you now know — the kind a well-informed colleague would arrive with. Don't make the mechanism obvious.

### What This Doesn't Show
Honest accounting of gaps: work that didn't surface in Slack, private conversations you can't see, topics where the evidence is thin. Don't overstate certainty.

## Step 8 — Save the briefing

Save the briefing to `./reports/YYYY-MM-DD_HH-MM_briefing-<lastname>.md` in the current working directory. Create `reports/` if it doesn't exist. Print the saved path.

A briefing is **personal data about a specific individual** and lands in a folder that may be a git repo. Before saving, ensure `./reports/` is `.gitignore`d — create or append a `./.gitignore` with `reports/` — and never `git add`/commit it.
