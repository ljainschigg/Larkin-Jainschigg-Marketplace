---
name: report
description: Produce a collaboration report from a Slack channel — surfaces exciting work, brokers introductions, and gives a leadership pulse on team momentum. Reads channel history via Claude Code's built-in Slack connector.
---

# report

Generate a collaboration report from one or more Slack channels. Surfaces exciting work, brokers introductions, identifies the most promising multi-person collaborations, and delivers a leadership pulse on team momentum.

## Step 0 — Preflight: Slack connector

This skill relies on Claude Code's **built-in Slack connector** (the `slack_*` MCP tools). There are no plugin-managed credentials.

Confirm the connector is available and authenticated before doing anything else: make one lightweight call — `slack_search_channels` with `query` set to the channel you'll scan. If the `slack_*` tools are not available at all, or the call returns an authentication error, stop and tell the user:

> This skill needs Claude Code's **Slack connector** to be connected and authenticated. Add it from Claude Code's connector settings (`/mcp`), sign in to your Slack workspace, and make sure the signed-in user is a **member of the channel(s)** you want to report on. Then run `/report` again.

Do not proceed until a Slack call succeeds.

## Step 1 — Determine channel(s) and time range

**Channel(s):** From the user's request, determine which channel(s) to scan. If they didn't name one, ask (offer a sensible default if they've used the skill before). More than one channel is allowed — see the multi-channel note below.

**Time range:** derive from what the user asked:
- Number of days to cover (default 7 if unspecified; all history if they say "all time" / "everything" / "since the beginning")
- `oldest_ts`: Unix timestamp for the start of the window (now minus N×86400 seconds). Omit for all-time.
- A human label: e.g. "last 7 days", "last 30 days", "entire channel history"

**Multi-channel runs:** if scanning more than one channel, fetch and process each separately, then synthesise into a single report. Label each observation with its source channel (e.g. *"#platform-eng"*). In sections 2 and 3, actively look for introductions and collaborations that span channels — these are often the most valuable connections.

## Step 2 — Find the channel

Call `slack_search_channels` with `query` set to the channel name and `channel_types="public_channel,private_channel"`. Use the `channel_id` of the exact-name match.

## Step 3 — Fetch all messages

Call `slack_read_channel` with `channel_id`, `limit=100`, and `oldest=oldest_ts` (omit `oldest` for all-time). The API returns newest-first — page through all results using the cursor, collect everything, then reverse to oldest-first order.

## Step 4 — Resolve user display names

For each unique user ID in the messages, call `slack_read_user_profile`. Build a map of `user_id → real_name` (fall back to `display_name`, then the raw ID).

## Step 5 — Format the transcript

For each message oldest-first, skip any with a `subtype` field or blank text. Format as:

```
[YYYY-MM-DD] Name: message text
```

## Step 6 — Analyse and write the report

Read the transcript as an enthusiastic, people-obsessed CEO. Your instinct is always "these two people need to meet" or "this work deserves a bigger audience." You're here to amplify, not audit. Be specific, warm, and genuinely excited. Connect dots boldly where the connection is real. Never invent details not present in the messages.

**Date anchoring:** every observation must carry a time reference so the reader can judge freshness. Use a relative label (today, yesterday, 3 days ago, last week) followed by the absolute date in parentheses — e.g. *"3 days ago (Jun 15)"*. For a span, give a range: *"Jun 13–16"*. Place the date reference inline, naturally.

Produce a markdown report with these five sections:

### 1. What's Exciting Right Now
Ranked list of the most compelling work — who, what, when it surfaced, and one sentence on why it matters or where it could go. Be selective, not exhaustive.

### 2. Introductions I'd Make
Connections you'd broker. For each: **[Person A] meets [Person B]** — a punchy human pitch, what could come of it, framed as opportunity not correction. Note when each person's relevant work appeared.

### 3. The Collaboration I'm Most Excited About
The single most promising multi-person collaboration visible in the data. What could they build together that none of them could build alone? Be specific about what each brings and when their contributions appeared.

### 4. Things Everyone Should Hear About
Underappreciated threads, quiet breakthroughs, ideas that got buried. Frame each as a "you should know about this" moment, and note how long ago it happened.

### 5. The Pulse — One Paragraph for Leadership
One energetic paragraph a CEO could paste into a board update or all-hands. Capture the spirit, the momentum, and one concrete opportunity to invest in. Include a date range.

## Step 7 — Save the report

Save the report to `./reports/YYYY-MM-DD_HH-MM_<label>.md` in the current working directory (label e.g. `last-7d`, `all-time`, or a channel slug). Create `reports/` if it doesn't exist. Print the saved path.

These reports contain **personal data about colleagues** (names, what people are working on) and land in a folder that may be a git repo. Before saving, ensure `./reports/` is `.gitignore`d — create or append a `./.gitignore` with `reports/` — and never `git add`/commit them.
