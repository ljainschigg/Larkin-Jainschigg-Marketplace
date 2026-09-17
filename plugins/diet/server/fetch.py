# /// script
# dependencies = ["httpx"]
# ///

import sys
from datetime import date, timedelta

import fitbit
import withings


def print_section(title: str, data: dict):
    print(f"\n{'=' * 40}")
    print(f"  {title}")
    print(f"{'=' * 40}")
    if not data:
        print("  (no data)")
        return
    for k, v in data.items():
        if k == "date":
            continue
        if v is not None:
            print(f"  {k:<25} {v}")
        else:
            print(f"  {k:<25} —")


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else str(date.today() - timedelta(days=1))
    print(f"\nFetching metrics for {target} ...")

    try:
        fb = fitbit.fetch(target)
        print_section(f"FitBit — {target}", fb)
    except Exception as e:
        print(f"\n[FitBit ERROR] {e}")

    try:
        w = withings.fetch(target)
        print_section(f"Withings — {target}", w)
    except Exception as e:
        print(f"\n[Withings ERROR] {e}")


if __name__ == "__main__":
    main()
