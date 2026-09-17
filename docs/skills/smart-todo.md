# smart-todo

A conversational to-do list manager for Claude Code. Paste freeform text from anywhere — emails, Slack, meeting notes, browser tabs — and Claude extracts structured tasks, stores them in a local CSV, and answers natural-language questions about what to do next.

---

## Install

If you haven't added the marketplace yet:

```
/plugin marketplace add ljainschigg/generic-marketplace-2
```

Then install the plugin:

```
/plugin install smart-todo@claude-plugins
```

---

## Use

```
/smart-todo
```

Claude opens in two modes:

- **Intake** — paste any freeform text. Claude extracts title, requestor, due date, links, tags, priority (1–5), and political weight (1–5), confirms with you, then writes the task.
- **Query** — ask anything: *"What should I do next?"*, *"What can I get done this morning?"*, *"What has Sarah asked me for?"*, *"What's overdue?"*

---

## How it works

Tasks are stored in `~/.local/share/smart-todo/tasks.csv`. A bundled Python script (`scripts/todo.py`) handles all structured reads and writes — Claude never touches the CSV directly. The script supports `add`, `list`, `show`, `update`, `done`, and `report` subcommands, and is self-documenting via `todo.py schema`. Claude reads the schema at startup and uses the script as its only interface to the data, so every session starts with full, consistent context about your task list.

Priority and political weight together drive a composite urgency score that determines ranking across all reports.

---

## Details

| | |
|---|---|
| **Version** | 1.0.4 |
| **Tier** | platform |
| **Maintained by** | Claude Plugins Marketplace |
| **Data** | `~/.local/share/smart-todo/tasks.csv` |
| **Dependencies** | Python 3 (stdlib only) |
