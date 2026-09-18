# /// script
# dependencies = []
# ///
"""diet.py — logging helpers for the diet plugin.

One CLI for the repetitive compliance.csv / biometrics.csv operations, so they
don't have to be improvised with shell one-liners:

    log      append food rows for a day, recompute the daily_total, show gaps
    close    finalize a day's daily_total (status = DAY CLOSED)
    show     print a day's rows + gap analysis
    summary  gap analysis only for a day
    bio      append biometric rows with (date,time,metric) dedup
    today    print today's date (avoids $(date) in shell)

Design notes:
  * Invocation is always literal — `python3 server/diet.py <cmd> ...` — so it can
    be allowlisted with a single Bash rule (no $(...) / variables to "obfuscate").
  * Row payloads come in as JSON via --file / --json / stdin, never as long shell
    args, so notes with commas/em-dashes need no quoting gymnastics.
  * daily_total is always RECOMPUTED from the day's rows, never hand-summed.
  * A <file>.bak snapshot is written before every mutation.
  * Operates on the (gitignored) personal CSVs; this tool itself is committable.
"""

import argparse
import csv
import json
import shutil
import sys
from datetime import date as _date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COMPLIANCE = ROOT / "compliance.csv"
BIOMETRICS = ROOT / "biometrics.csv"
TARGETS = ROOT / "targets.json"

COMPLIANCE_COLS = ["date", "meal_context", "food_item", "amount_g", "kcal",
                   "protein_g", "sat_fat_g", "soy_protein_g", "omega3_g",
                   "soluble_fiber_g", "sodium_mg", "notes"]
BIO_COLS = ["date", "time", "metric", "value", "unit", "notes"]
SUM_COLS = ["kcal", "protein_g", "sat_fat_g", "soy_protein_g", "omega3_g",
            "soluble_fiber_g", "sodium_mg"]

# Fallback if targets.json is absent; mirrors templates/targets.json. These are
# generic starting values, not anyone's prescription — the instance's own
# targets.json is the source of truth and overrides every key it defines.
DEFAULT_TARGETS = {
    "kcal":      {"target": 2000, "dir": "under", "label": "Calories", "short": "kcal",    "unit": "kcal"},
    "protein_g": {"target": 100,  "dir": "min",   "label": "Protein",  "short": "protein", "unit": "g"},
    "sat_fat_g": {"target": 20,   "dir": "under", "label": "Sat fat",  "short": "sat fat", "unit": "g"},
    "sodium_mg": {"target": 2300, "dir": "under", "label": "Sodium",   "short": "sodium",  "unit": "mg"},
}


def today():
    return _date.today().isoformat()


def fmt(x):
    f = float(x)
    return str(int(f)) if f == int(f) else str(round(f, 2))


def _num(v):
    try:
        return float((v or "").strip())
    except (ValueError, AttributeError):
        return 0.0


def load_targets(path):
    t = {k: dict(v) for k, v in DEFAULT_TARGETS.items()}
    if path.exists():
        user = json.loads(path.read_text())
        for k, v in user.items():
            t.setdefault(k, {}).update(v)
    return t


def _read(path):
    if not path.exists():
        return []
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def _write(path, cols, rows):
    if path.exists():
        shutil.copy2(path, path.with_name(path.name + ".bak"))
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "") for c in cols})


def _load_json(args):
    if args.file:
        text = Path(args.file).read_text()
    elif args.json:
        text = args.json
    else:
        text = sys.stdin.read()
    data = json.loads(text)
    return [data] if isinstance(data, dict) else data


def _totals(rows, d):
    day = [r for r in rows if r["date"] == d and r["meal_context"] != "daily_total"]
    return {c: sum(_num(r[c]) for r in day) for c in SUM_COLS}, len(day)


def _evaluate(totals, targets):
    """Return (rows_for_display, list_of_missed_labels)."""
    display, misses = [], []
    for col in SUM_COLS:
        t = targets[col]
        val, tgt = totals[col], t["target"]
        met = (val >= tgt) if t["dir"] == "min" else (val < tgt)
        comp = f"{'≥' if t['dir'] == 'min' else '<'}{fmt(tgt)}"
        if met:
            delta = ""
        elif t["dir"] == "min":
            delta = f" (short {fmt(tgt - val)}{t['unit']})"
        else:
            delta = f" (over by {fmt(val - tgt)}{t['unit']})"
        if not met:
            misses.append(t["label"])
        display.append((t["label"], fmt(val), comp, t["unit"], "✓" if met else "✗", delta))
    return display, misses


def _total_notes(totals, targets, status):
    parts = []
    for col in SUM_COLS:
        t = targets[col]
        val, tgt = totals[col], t["target"]
        met = (val >= tgt) if t["dir"] == "min" else (val < tgt)
        parts.append(f"{t['short']} {fmt(val)}/{fmt(tgt)}{t['unit']} {'✓' if met else '✗'}")
    return "; ".join(parts) + " — " + status


def _make_total_row(d, totals, targets, status):
    row = {c: "" for c in COMPLIANCE_COLS}
    row.update(date=d, meal_context="daily_total", food_item="TOTAL")
    for c in SUM_COLS:
        row[c] = fmt(totals[c])
    row["notes"] = _total_notes(totals, targets, status)
    return row


def _print_gap(d, totals, targets):
    display, misses = _evaluate(totals, targets)
    print(f"[{d}] — diet summary")
    print("─" * 42)
    for label, val, comp, unit, mark, delta in display:
        print(f"  {label + ':':15} {val}/{comp} {unit}  {mark}{delta}")
    print("─" * 42)
    print("Misses: " + (", ".join(misses) if misses else "none — all targets met"))


def _rebuild(d, targets, new_rows, status):
    rows = [r for r in _read(COMPLIANCE)
            if not (r["date"] == d and r["meal_context"] == "daily_total")]
    for item in new_rows:
        r = {c: "" for c in COMPLIANCE_COLS}
        r.update({k: str(v) for k, v in item.items() if k in COMPLIANCE_COLS})
        r["date"] = d
        rows.append(r)
    totals, n = _totals(rows, d)
    _, misses = _evaluate(totals, targets)
    miss_tail = f"; misses: {', '.join(misses)}" if misses else (
        "; all targets met" if status.startswith("PARTIAL") else "; CLEAN SWEEP")
    rows.append(_make_total_row(d, totals, targets, status + miss_tail))
    _write(COMPLIANCE, COMPLIANCE_COLS, rows)
    return totals, n


def cmd_log(args, targets):
    d = args.date or today()
    totals, _ = _rebuild(d, targets, _load_json(args), "PARTIAL")
    _print_gap(d, totals, targets)


def cmd_close(args, targets):
    d = args.date or today()
    rows = _read(COMPLIANCE)
    _, n = _totals(rows, d)
    if n == 0:
        print(f"No rows for {d} — nothing to close.")
        return
    totals, _ = _rebuild(d, targets, [], "DAY CLOSED")
    _print_gap(d, totals, targets)


def cmd_show(args, targets):
    d = args.date or today()
    rows = [r for r in _read(COMPLIANCE) if r["date"] == d]
    if not rows:
        print(f"No rows for {d}.")
        return
    for r in rows:
        if r["meal_context"] == "daily_total":
            continue
        amt = f"{r['amount_g']}g" if r["amount_g"] else ""
        print(f"  {r['meal_context']:11} {r['food_item']:24} {amt:8} {r['kcal']:>5} kcal")
    print()
    totals, _ = _totals(rows, d)
    _print_gap(d, totals, targets)


def cmd_summary(args, targets):
    d = args.date or today()
    totals, n = _totals(_read(COMPLIANCE), d)
    if n == 0:
        print(f"No rows for {d}. Use `log` to start.")
        return
    _print_gap(d, totals, targets)


def cmd_bio(args, targets):
    payload = _load_json(args)
    rows = _read(BIOMETRICS)
    seen = {(r["date"], r["time"], r["metric"]) for r in rows}
    added = []
    for item in payload:
        r = {c: "" for c in BIO_COLS}
        r.update({k: str(v) for k, v in item.items() if k in BIO_COLS})
        r["date"] = r["date"] or today()
        r["time"] = r["time"] or "morning"
        key = (r["date"], r["time"], r["metric"])
        if key in seen:
            continue
        seen.add(key)
        rows.append(r)
        added.append(r)
    if not added:
        print("No new biometric rows (all duplicates).")
        return
    _write(BIOMETRICS, BIO_COLS, rows)
    for r in added:
        print(f"Logged: {r['metric']} {r['value']} {r['unit']} ({r['date']} {r['time']})")


def cmd_today(args, targets):
    print(today())


def main():
    p = argparse.ArgumentParser(description="Diet logging helpers")
    p.add_argument("--compliance", help="override compliance.csv path")
    p.add_argument("--biometrics", help="override biometrics.csv path")
    p.add_argument("--targets", help="override targets.json path")
    sub = p.add_subparsers(dest="cmd", required=True)

    def add_json(sp):
        sp.add_argument("--file", help="JSON file of row(s)")
        sp.add_argument("--json", help="inline JSON of row(s)")

    sp = sub.add_parser("log"); add_json(sp); sp.add_argument("--date")
    sub.add_parser("close").add_argument("--date")
    sub.add_parser("show").add_argument("--date")
    sub.add_parser("summary").add_argument("--date")
    add_json(sub.add_parser("bio"))
    sub.add_parser("today")

    args = p.parse_args()

    global COMPLIANCE, BIOMETRICS, TARGETS
    if args.compliance:
        COMPLIANCE = Path(args.compliance)
    if args.biometrics:
        BIOMETRICS = Path(args.biometrics)
    if args.targets:
        TARGETS = Path(args.targets)

    targets = load_targets(TARGETS)
    {"log": cmd_log, "close": cmd_close, "show": cmd_show, "summary": cmd_summary,
     "bio": cmd_bio, "today": cmd_today}[args.cmd](args, targets)


if __name__ == "__main__":
    main()
