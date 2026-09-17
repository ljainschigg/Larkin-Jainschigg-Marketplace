#!/usr/bin/env python3
"""
smart-todo CLI — structured task management for Claude Code.

DATA FILE: ~/.local/share/smart-todo/tasks.csv

SCHEMA:
  id            UUID4, assigned on creation, immutable
  title         Short summary (required)
  description   Full context extracted from source text
  requestor     Person or system that requested the task
  due_date      ISO date YYYY-MM-DD, or empty
  priority      Integer 1-5: 1=critical  2=high  3=medium  4=low  5=someday
  political     Integer 1-5: 1=routine  3=director/VP-visible  5=exec/customer-facing
  status        todo | in-progress | done | blocked | deferred
  links         Pipe-separated URLs
  tags          Comma-separated labels
  created_at    ISO datetime, set on creation
  updated_at    ISO datetime, updated on every write
  notes         Freeform additional context

COMPOSITE SCORE (lower = more urgent):
  score = priority * 2 - political
  Range: -3 (priority=1, political=5) to 9 (priority=5, political=1)
  High political weight elevates tasks above routine ones at the same priority.

COMMANDS:
  schema        Print this documentation
  add           Add a new task
  list          List tasks (filterable, sortable)
  show <id>     Show full detail of one task
  update <id>   Update fields on a task
  done <id>     Mark a task done
  report        Generate a named report

REPORT TYPES (--type):
  next          Single best next task by composite score
  morning       Top N tasks by composite score (--n N, default 5)
  overdue       Open tasks whose due_date is before today
  by-requestor  Open tasks grouped by requestor, sorted by score within each group
  by-priority   All open tasks sorted by priority then political weight
  all           All tasks including done and deferred

ID MATCHING: All commands that take an <id> accept the full UUID or any
unique prefix (minimum 4 characters).
"""

import argparse
import csv
import sys
import uuid
from datetime import date, datetime
from pathlib import Path

DATA_DIR = Path.home() / ".local" / "share" / "smart-todo"
DATA_FILE = DATA_DIR / "tasks.csv"

FIELDS = [
    "id", "title", "description", "requestor", "due_date",
    "priority", "political", "status", "links", "tags",
    "created_at", "updated_at", "notes",
]

VALID_STATUSES = ("todo", "in-progress", "done", "blocked", "deferred")


def now_iso():
    return datetime.now().isoformat(timespec="seconds")


def today_iso():
    return date.today().isoformat()


def load_tasks():
    if not DATA_FILE.exists():
        return []
    with open(DATA_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [dict(row) for row in reader]


def save_tasks(tasks):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(tasks)


def composite_score(task):
    try:
        p = int(task.get("priority") or 3)
        pol = int(task.get("political") or 1)
        return p * 2 - pol
    except (ValueError, TypeError):
        return 6


def open_tasks(tasks):
    return [t for t in tasks if t.get("status") not in ("done", "deferred")]


def resolve_id(tasks, prefix):
    prefix = prefix.strip()
    matches = [t for t in tasks if t["id"] == prefix or t["id"].startswith(prefix)]
    if not matches:
        print(f"Error: no task found with id starting with '{prefix}'", file=sys.stderr)
        sys.exit(1)
    if len(matches) > 1:
        print(f"Error: '{prefix}' is ambiguous — matches {len(matches)} tasks:", file=sys.stderr)
        for t in matches:
            print(f"  {t['id'][:12]}  {t['title']}", file=sys.stderr)
        sys.exit(1)
    return matches[0]


def fmt_task(task, verbose=False):
    tid = task.get("id", "")[:8]
    lines = [
        f"[{tid}] {task.get('title', '(no title)')}",
        (f"  status={task.get('status','?')}  "
         f"priority={task.get('priority','?')}  "
         f"political={task.get('political','?')}  "
         f"due={task.get('due_date') or 'none'}  "
         f"score={composite_score(task)}"),
    ]
    if task.get("requestor"):
        lines.append(f"  requestor: {task['requestor']}")
    if task.get("tags"):
        lines.append(f"  tags: {task['tags']}")
    if verbose:
        if task.get("description"):
            lines.append(f"  description: {task['description']}")
        if task.get("links"):
            for link in task["links"].split("|"):
                link = link.strip()
                if link:
                    lines.append(f"  link: {link}")
        if task.get("notes"):
            lines.append(f"  notes: {task['notes']}")
        lines.append(f"  id: {task.get('id', '')}")
        lines.append(f"  created: {task.get('created_at', '')}  updated: {task.get('updated_at', '')}")
    return "\n".join(lines)


# ---------- subcommand handlers ----------

def cmd_schema(args):
    print(__doc__)


def cmd_add(args):
    tasks = load_tasks()
    task = {f: "" for f in FIELDS}
    task["id"] = str(uuid.uuid4())
    task["title"] = args.title
    task["description"] = args.description or ""
    task["requestor"] = args.requestor or ""
    task["due_date"] = args.due_date or ""
    task["priority"] = str(args.priority)
    task["political"] = str(args.political)
    task["status"] = "todo"
    task["links"] = args.links or ""
    task["tags"] = args.tags or ""
    task["notes"] = args.notes or ""
    task["created_at"] = now_iso()
    task["updated_at"] = now_iso()
    tasks.append(task)
    save_tasks(tasks)
    print(f"Added [{task['id'][:8]}] {task['title']}")
    print(f"  priority={task['priority']}  political={task['political']}  due={task['due_date'] or 'none'}")


def cmd_list(args):
    tasks = load_tasks()
    if not args.all:
        tasks = open_tasks(tasks)
    if args.status:
        tasks = [t for t in tasks if t.get("status") == args.status]
    if args.requestor:
        tasks = [t for t in tasks if args.requestor.lower() in (t.get("requestor") or "").lower()]
    if args.tag:
        tasks = [t for t in tasks if args.tag.lower() in (t.get("tags") or "").lower()]

    sort = args.sort
    if sort == "score":
        tasks.sort(key=composite_score)
    elif sort == "due":
        tasks.sort(key=lambda t: t.get("due_date") or "9999-99-99")
    elif sort == "priority":
        tasks.sort(key=lambda t: (int(t.get("priority") or 3), -(int(t.get("political") or 1))))
    elif sort == "created":
        tasks.sort(key=lambda t: t.get("created_at") or "")
    elif sort == "updated":
        tasks.sort(key=lambda t: t.get("updated_at") or "", reverse=True)

    if args.limit:
        tasks = tasks[:args.limit]

    if not tasks:
        print("No tasks match.")
        return
    print(f"{len(tasks)} task(s):\n")
    for t in tasks:
        print(fmt_task(t))
        print()


def cmd_show(args):
    tasks = load_tasks()
    t = resolve_id(tasks, args.id)
    print(fmt_task(t, verbose=True))


def cmd_update(args):
    tasks = load_tasks()
    t = resolve_id(tasks, args.id)
    updatable = {
        "title": args.title,
        "description": args.description,
        "requestor": args.requestor,
        "due_date": args.due_date,
        "priority": str(args.priority) if args.priority is not None else None,
        "political": str(args.political) if args.political is not None else None,
        "status": args.status,
        "links": args.links,
        "tags": args.tags,
        "notes": args.notes,
    }
    changed = []
    for field, val in updatable.items():
        if val is not None:
            t[field] = val
            changed.append(field)
    if not changed:
        print("No fields specified — nothing changed.")
        return
    t["updated_at"] = now_iso()
    save_tasks(tasks)
    print(f"Updated [{t['id'][:8]}] {t['title']}")
    print(f"  changed: {', '.join(changed)}")


def cmd_done(args):
    tasks = load_tasks()
    t = resolve_id(tasks, args.id)
    if t["status"] == "done":
        print(f"Already done: [{t['id'][:8]}] {t['title']}")
        return
    t["status"] = "done"
    t["updated_at"] = now_iso()
    save_tasks(tasks)
    print(f"Done: [{t['id'][:8]}] {t['title']}")


def cmd_report(args):
    tasks = load_tasks()
    rtype = args.type

    if rtype == "next":
        candidates = sorted(open_tasks(tasks), key=composite_score)
        if not candidates:
            print("No open tasks.")
            return
        print("NEXT TASK:\n")
        print(fmt_task(candidates[0], verbose=True))

    elif rtype == "morning":
        n = args.n
        candidates = sorted(open_tasks(tasks), key=composite_score)[:n]
        if not candidates:
            print("No open tasks.")
            return
        print(f"TOP {n} FOR THIS MORNING:\n")
        for i, t in enumerate(candidates, 1):
            print(f"{i}. {fmt_task(t)}\n")

    elif rtype == "overdue":
        today = today_iso()
        candidates = sorted(
            [t for t in open_tasks(tasks) if t.get("due_date") and t["due_date"] <= today],
            key=lambda t: t.get("due_date") or "",
        )
        if not candidates:
            print("No overdue tasks.")
            return
        print(f"DUE TODAY OR OVERDUE ({len(candidates)}):\n")
        for t in candidates:
            print(fmt_task(t))
            print()

    elif rtype == "by-requestor":
        candidates = sorted(open_tasks(tasks), key=composite_score)
        groups: dict = {}
        for t in candidates:
            req = t.get("requestor") or "(no requestor)"
            groups.setdefault(req, []).append(t)
        if not groups:
            print("No open tasks.")
            return
        print(f"OPEN TASKS BY REQUESTOR ({len(candidates)} total):\n")
        for req in sorted(groups):
            print(f"── {req} ({len(groups[req])}) ──")
            for t in groups[req]:
                print(fmt_task(t))
            print()

    elif rtype == "by-priority":
        candidates = sorted(
            open_tasks(tasks),
            key=lambda t: (int(t.get("priority") or 3), -(int(t.get("political") or 1))),
        )
        if not candidates:
            print("No open tasks.")
            return
        print(f"OPEN TASKS BY PRIORITY ({len(candidates)} total):\n")
        for t in candidates:
            print(fmt_task(t))
            print()

    elif rtype == "all":
        if not tasks:
            print("No tasks yet.")
            return
        done = [t for t in tasks if t.get("status") == "done"]
        deferred = [t for t in tasks if t.get("status") == "deferred"]
        active = open_tasks(tasks)
        print(f"ALL TASKS: {len(tasks)} total  ({len(active)} open, {len(done)} done, {len(deferred)} deferred)\n")
        for t in sorted(active, key=composite_score):
            print(fmt_task(t))
            print()
        if done:
            print("── DONE ──")
            for t in done:
                print(fmt_task(t))
                print()
        if deferred:
            print("── DEFERRED ──")
            for t in deferred:
                print(fmt_task(t))
                print()


# ---------- parser ----------

def build_parser():
    parser = argparse.ArgumentParser(
        prog="todo.py",
        description="smart-todo: structured task management for Claude Code.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Run 'todo.py schema' for full field documentation.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("schema", help="Print schema and field documentation")

    p = sub.add_parser("add", help="Add a new task")
    p.add_argument("--title", required=True, help="Short summary (required)")
    p.add_argument("--description", help="Full context")
    p.add_argument("--requestor", help="Who asked for this")
    p.add_argument("--due-date", dest="due_date", metavar="YYYY-MM-DD")
    p.add_argument("--priority", type=int, choices=range(1, 6), default=3,
                   metavar="1-5", help="1=critical 5=someday (default 3)")
    p.add_argument("--political", type=int, choices=range(1, 6), default=1,
                   metavar="1-5", help="1=routine 5=exec-facing (default 1)")
    p.add_argument("--links", help="Pipe-separated URLs")
    p.add_argument("--tags", help="Comma-separated tags")
    p.add_argument("--notes", help="Freeform notes")

    p = sub.add_parser("list", help="List tasks")
    p.add_argument("--all", action="store_true", help="Include done and deferred")
    p.add_argument("--status", choices=VALID_STATUSES)
    p.add_argument("--requestor", help="Filter by requestor (partial match)")
    p.add_argument("--tag", help="Filter by tag (partial match)")
    p.add_argument("--sort", choices=["score", "due", "priority", "created", "updated"],
                   default="score")
    p.add_argument("--limit", type=int, metavar="N")

    p = sub.add_parser("show", help="Show full detail of one task")
    p.add_argument("id", help="Task id or unique prefix")

    p = sub.add_parser("update", help="Update one or more fields on a task")
    p.add_argument("id", help="Task id or unique prefix")
    p.add_argument("--title")
    p.add_argument("--description")
    p.add_argument("--requestor")
    p.add_argument("--due-date", dest="due_date", metavar="YYYY-MM-DD")
    p.add_argument("--priority", type=int, choices=range(1, 6), metavar="1-5")
    p.add_argument("--political", type=int, choices=range(1, 6), metavar="1-5")
    p.add_argument("--status", choices=VALID_STATUSES)
    p.add_argument("--links")
    p.add_argument("--tags")
    p.add_argument("--notes")

    p = sub.add_parser("done", help="Mark a task done")
    p.add_argument("id", help="Task id or unique prefix")

    p = sub.add_parser("report", help="Generate a named report")
    p.add_argument("--type", choices=["next", "morning", "overdue", "by-requestor", "by-priority", "all"],
                   default="next")
    p.add_argument("--n", type=int, default=5, metavar="N",
                   help="Number of tasks for morning report (default 5)")

    return parser


HANDLERS = {
    "schema": cmd_schema,
    "add": cmd_add,
    "list": cmd_list,
    "show": cmd_show,
    "update": cmd_update,
    "done": cmd_done,
    "report": cmd_report,
}


if __name__ == "__main__":
    args = build_parser().parse_args()
    HANDLERS[args.cmd](args)
