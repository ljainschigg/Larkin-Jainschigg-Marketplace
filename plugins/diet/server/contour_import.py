# /// script
# dependencies = []
# ///
"""
Import Contour glucose CSV exports into biometrics.csv.

Usage:
    uv run server/contour_import.py <path-to-contour-export.csv>

The Contour Diabetes app exports a comma-delimited, BOM-prefixed file. Column
headers vary in spacing between export formats, e.g.:
    #  Date and Time  BGValue [mg/dL]  Meal Marker  Data Source  Notes  Activity  Meal [g]  Medication  Location

Column lookup is whitespace-insensitive (so "BGValue [mg/dL]" and
"BGValue[mg/dL]" both work), and several date formats (with/without seconds,
12h/24h) are accepted.

Only rows with Data Source == "Meter" are imported (skips manual entries).
Existing rows in biometrics.csv with the same date+time+metric are skipped.
"""

import csv
import io
import sys
from datetime import datetime
from pathlib import Path

BIOMETRICS_FILE = Path(__file__).parent.parent / "biometrics.csv"

# Meal marker (lowercased) -> biometrics metric name.
MEAL_MARKER_MAP = {
    "fasting":     "blood_glucose_fasted",
    "before meal": "blood_glucose_fasted",
    "after meal":  "blood_glucose_postprandial",
    "no marker":   "blood_glucose",
    "":            "blood_glucose",
}

# Accepted Date/Time formats, most specific first.
_DT_FORMATS = [
    "%m/%d/%Y %I:%M:%S %p",
    "%m/%d/%Y %I:%M %p",
    "%m/%d/%Y %H:%M:%S",
    "%m/%d/%Y %H:%M",
]


def _norm(key: str) -> str:
    """Normalize a column header for whitespace-insensitive lookup."""
    return "".join(key.split()).lower()


def _parse_dt(raw: str) -> "datetime | None":
    # Collapse any whitespace (incl. the NBSP/narrow-NBSP some exports put
    # before AM/PM) to single spaces before parsing.
    raw = " ".join(raw.split())
    for fmt in _DT_FORMATS:
        try:
            return datetime.strptime(raw, fmt)
        except ValueError:
            continue
    return None


def _parse_row(row: dict) -> "dict | None":
    # Whitespace-insensitive view of the row so header spacing doesn't matter.
    r = {_norm(k): (v or "").strip() for k, v in row.items() if k}

    if r.get("datasource", "").lower() != "meter":
        return None

    dt = _parse_dt(r.get("dateandtime", ""))
    if dt is None:
        return None

    bg_raw = r.get("bgvalue[mg/dl]", "")
    if not bg_raw:
        return None
    try:
        bg = float(bg_raw)
    except ValueError:
        return None

    marker = r.get("mealmarker", "")
    metric = MEAL_MARKER_MAP.get(marker.lower(), "blood_glucose")

    notes_parts = ["Contour Next One"]
    if marker:
        notes_parts.append(marker)
    if r.get("notes"):
        notes_parts.append(r["notes"])
    if r.get("medication"):
        notes_parts.append(f"med: {r['medication']}")

    return {
        "date": dt.strftime("%Y-%m-%d"),
        "time": dt.strftime("%H:%M"),
        "metric": metric,
        "value": int(bg) if bg == int(bg) else bg,
        "unit": "mg/dL",
        "notes": "; ".join(notes_parts),
    }


def _load_existing() -> set:
    existing = set()
    try:
        with BIOMETRICS_FILE.open() as f:
            reader = csv.DictReader(f)
            for row in reader:
                existing.add((row["date"], row["time"], row["metric"]))
    except FileNotFoundError:
        pass
    return existing


def _import_parsed(parsed: list):
    existing = _load_existing()
    new_rows = [
        r for r in parsed
        if (r["date"], r["time"], r["metric"]) not in existing
    ]

    if not new_rows:
        print(f"No new rows to import ({len(parsed)} parsed, all already present).")
        return

    with BIOMETRICS_FILE.open("a") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["date", "time", "metric", "value", "unit", "notes"],
            lineterminator="\n",
        )
        for row in new_rows:
            writer.writerow(row)

    print(f"Imported {len(new_rows)} new row(s) from {len(parsed)} parsed:")
    for r in new_rows:
        print(f"  {r['date']} {r['time']}  {r['metric']:35s}  {r['value']} mg/dL  ({r['notes']})")


def _parse_text(content: str) -> list:
    # Strip a leading BOM if present so the first header key isn't mangled.
    content = content.lstrip("﻿")
    reader = csv.DictReader(io.StringIO(content), delimiter=",")
    return [r for r in (_parse_row(row) for row in reader) if r is not None]


def main(csv_path: str):
    path = Path(csv_path)
    if not path.exists():
        print(f"ERROR: file not found: {csv_path}")
        raise SystemExit(1)

    content = path.read_text(encoding="utf-8-sig")
    _import_parsed(_parse_text(content))


def main_from_text(content: str):
    _import_parsed(_parse_text(content))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: uv run server/contour_import.py <contour-export.csv>")
        raise SystemExit(1)
    main(sys.argv[1])
