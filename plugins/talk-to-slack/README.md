# talk-to-slack

Generate reports from a Slack channel's activity using Claude Code's **built-in Slack connector** — no API keys, bot tokens, or Python dependencies. Two reports:

- **`/report`** — a collaboration report across one or more channels: what's exciting, introductions worth brokering, the most promising multi-person collaboration, and a leadership pulse.
- **`/briefing <name>`** — a per-person prep briefing reconstructed from someone's Slack activity: what they're invested in, who they're engaging, time pressures, and pointed questions to ask.

---

## Prerequisites

- Claude Code's **Slack connector** connected and authenticated (add it from `/mcp` → connectors, then sign in to your Slack workspace). This is the plugin's only dependency; both skills run a Step 0 preflight that checks it before doing anything.
- The signed-in Slack user must be a **member of the channel(s)** you report on and able to see the people you brief on.

## Install

If you haven't added the marketplace yet:

```
/plugin marketplace add ljainschigg/Larkin-Jainschigg-Marketplace
```

Then install the plugin:

```
/plugin install talk-to-slack@lj-marketplace
```

## Use

Collaboration report (asks which channel and time range; defaults to the last 7 days):

```
/report
/report last 30 days
/report all time
```

Per-person briefing:

```
/briefing <person's display name>
```

Both save a timestamped markdown file under `./reports/` in the current working directory and print the path.

---

## How it works

Each skill drives the built-in Slack connector directly (`slack_search_channels`, `slack_read_channel`, `slack_read_user_profile`, `slack_search_users`, `slack_search_public_and_private`, `slack_read_thread`) — fetching messages, resolving display names, and analysing the transcript. Nothing is stored beyond the report files you generate; there are no credentials for this plugin to manage.

---

## Details

| | |
|---|---|
| **Version** | 1.0.5 |
| **Type** | skill |
| **Maintained by** | Claude Plugins Marketplace |
| **Dependency** | Claude Code built-in Slack connector (authenticated) |
| **Output** | `./reports/*.md` |
