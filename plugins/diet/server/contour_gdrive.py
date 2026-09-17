# /// script
# dependencies = ["httpx"]
# ///
"""
Fetch the latest Contour CSV export from Google Drive and import into biometrics.csv.

Usage:
    uv run server/contour_gdrive.py              # most recent file
    uv run server/contour_gdrive.py 2026-04-26   # specific date
    uv run server/contour_gdrive.py --list       # list available files, don't import
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import gdrive
import contour_import


def main():
    args = sys.argv[1:]

    if "--list" in args:
        files = gdrive.list_contour_files()
        if not files:
            print("No ContourCSVReport files found on Google Drive.")
        else:
            print(f"Found {len(files)} file(s):")
            for f in files:
                print(f"  {f['name']}  (id: {f['id'][:12]}...)")
        return

    date = args[0] if args else None

    try:
        filename, content = gdrive.fetch_contour(date)
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        raise SystemExit(1)

    print(f"Fetched: {filename}")

    import io
    contour_import.main_from_text(content)


if __name__ == "__main__":
    main()
