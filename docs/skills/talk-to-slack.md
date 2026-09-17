# talk-to-slack

Generate reports from a Slack channel's activity using Claude Code's **built-in Slack connector** — no API keys, bot tokens, or Python dependencies to manage.

- **`/report`** — a collaboration report across one or more channels: what's exciting right now, introductions worth brokering, the single most promising multi-person collaboration, things everyone should hear about, and a one-paragraph leadership pulse.
- **`/briefing <name>`** — a per-person prep briefing reconstructed from someone's Slack activity: what they're invested in (ranked), their key interlocutors, visible time pressures, and pointed questions to walk in with.

---

## Prerequisites

- Claude Code's **Slack connector** connected and authenticated (add it from `/mcp` → connectors, then sign in). Both skills run a Step 0 preflight that verifies it before doing anything.
- The signed-in Slack user must be a **member of the channel(s)** you report on, and able to see the people you brief on.

---

## Install

If you haven't added the marketplace yet:

```
/plugin marketplace add ljainschigg/generic-marketplace-2
```

Then install the plugin:

```
/plugin install talk-to-slack@claude-plugins
```

---

## Use

```
/report                 # asks which channel + time range (default: last 7 days)
/report last 30 days
/report all time
/briefing Randy Bias
```

Both save a timestamped markdown file under `./reports/` in the current working directory and print the path.

---

## Details

| | |
|---|---|
| **Version** | 1.0.2 |
| **Type** | skill |
| **Maintained by** | Claude Plugins Marketplace |
| **Dependency** | Claude Code built-in Slack connector (authenticated) |
| **Output** | `./reports/*.md` |
