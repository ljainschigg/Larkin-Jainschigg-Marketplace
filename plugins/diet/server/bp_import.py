# /// script
# dependencies = ["httpx"]
# ///
"""
Import Apple Health blood pressure data (via Simple Health Export CSV) into biometrics.csv.

The export produces a ZIP containing two CSVs:
  HKQuantityTypeIdentifierBloodPressureSystolic_*.csv
  HKQuantityTypeIdentifierBloodPressureDiastolic_*.csv

Usage:
    uv run server/bp_import.py                    # fetch latest ZIP from Google Drive
    uv run server/bp_import.py /path/to/file.zip  # import from local ZIP file
"""

import csv
import io
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

BIOMETRICS_FILE = Path(__file__).parent.parent / "biometrics.csv"


def _parse_hk_csv(content: str) -> list[dict]:
    lines = content.splitlines()
    # Skip the Excel sep= hint line if present
    if lines and lines[0].startswith("sep="):
        lines = lines[1:]
    reader = csv.DictReader(lines)
    return list(reader)


def _parse_zip(data: bytes) -> list[dict]:
    """Parse systolic + diastolic CSVs from ZIP, join by timestamp, return list of readings."""
    systolic = {}
    diastolic = {}

    with zipfile.ZipFile(io.BytesIO(data)) as z:
        for name in z.namelist():
            content = z.read(name).decode("utf-8-sig")
            rows = _parse_hk_csv(content)
            for row in rows:
                ts = row.get("startDate", "").strip()
                val = row.get("value", "").strip()
                if not ts or not val:
                    continue
                hk_type = row.get("type", "")
                if "Systolic" in hk_type:
                    systolic[ts] = float(val)
                elif "Diastolic" in hk_type:
                    diastolic[ts] = float(val)

    readings = []
    for ts, sys_val in systolic.items():
        if ts not in diastolic:
            continue
        # Parse UTC timestamp: "2026-04-27 18:20:15 +0000"
        try:
            dt_utc = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S %z")
        except ValueError:
            continue
        dt_local = dt_utc.astimezone()  # convert to system local timezone
        readings.append({
            "date": dt_local.strftime("%Y-%m-%d"),
            "time": dt_local.strftime("%H:%M"),
            "systolic": int(sys_val),
            "diastolic": int(diastolic[ts]),
        })

    return sorted(readings, key=lambda r: (r["date"], r["time"]))


def _load_existing() -> set[tuple]:
    existing = set()
    try:
        with BIOMETRICS_FILE.open() as f:
            reader = csv.DictReader(f)
            for row in reader:
                existing.add((row["date"], row["time"], row["metric"]))
    except FileNotFoundError:
        pass
    return existing


def import_from_bytes(data: bytes):
    readings = _parse_zip(data)
    existing = _load_existing()

    new_rows = []
    for r in readings:
        if (r["date"], r["time"], "bp_systolic") not in existing:
            new_rows.append({
                "date": r["date"], "time": r["time"],
                "metric": "bp_systolic", "value": r["systolic"],
                "unit": "mmHg", "notes": "Omron via Apple Health",
            })
        if (r["date"], r["time"], "bp_diastolic") not in existing:
            new_rows.append({
                "date": r["date"], "time": r["time"],
                "metric": "bp_diastolic", "value": r["diastolic"],
                "unit": "mmHg", "notes": "Omron via Apple Health",
            })

    if not new_rows:
        print(f"No new rows to import ({len(readings)} reading(s) parsed, all already present).")
        return

    with BIOMETRICS_FILE.open("a") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["date", "time", "metric", "value", "unit", "notes"],
            lineterminator="\n",
        )
        for row in new_rows:
            writer.writerow(row)

    imported = len(new_rows) // 2
    print(f"Imported {imported} new BP reading(s) ({len(new_rows)} rows):")
    for i in range(0, len(new_rows), 2):
        s = new_rows[i]
        d = new_rows[i + 1]
        print(f"  {s['date']} {s['time']}  {s['value']}/{d['value']} mmHg")


def main():
    if len(sys.argv) > 1:
        path = Path(sys.argv[1])
        if not path.exists():
            print(f"ERROR: file not found: {path}")
            raise SystemExit(1)
        data = path.read_bytes()
        print(f"Reading: {path.name}")
    else:
        import gdrive, httpx
        token = gdrive._access_token()
        r = httpx.get(
            gdrive.FILES_URL,
            headers={"Authorization": f"Bearer {token}"},
            params={
                "q": "name contains 'HealthVitals' and trashed=false",
                "orderBy": "name desc",
                "fields": "files(id,name)",
                "pageSize": 10,
            },
        )
        r.raise_for_status()
        files = r.json().get("files", [])
        if not files:
            print("No HealthVitals ZIP files found on Google Drive.")
            raise SystemExit(1)
        target = files[0]
        print(f"Fetching: {target['name']}")
        dl = httpx.get(
            f"https://www.googleapis.com/drive/v3/files/{target['id']}?alt=media",
            headers={"Authorization": f"Bearer {token}"},
            follow_redirects=True,
        )
        dl.raise_for_status()
        data = dl.content

    import_from_bytes(data)


if __name__ == "__main__":
    main()
