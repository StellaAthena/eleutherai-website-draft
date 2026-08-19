#!/usr/bin/env python3
"""Report whether external build data was fetched live or supplied by a fallback."""

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FRESHNESS_DIR = ROOT / "data" / "generated" / "freshness"
FRESH_STATUSES = {"live", "provided", "local"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-live", action="store_true")
    args = parser.parse_args()

    reports = sorted(FRESHNESS_DIR.glob("*.json"))
    if not reports:
        raise SystemExit("No data freshness reports found; run a data build first")

    stale = []
    for report_path in reports:
        report = json.loads(report_path.read_text(encoding="utf-8"))
        print(f"{report_path.stem}: {report.get('mode', 'unknown')} ({report.get('generated_at', 'unknown time')})")
        for name, details in report.get("sources", {}).items():
            status = details.get("status", "unknown")
            print(f"  {name}: {status}")
            if status not in FRESH_STATUSES:
                stale.append(f"{name} ({status})")

    if args.require_live and stale:
        raise SystemExit("Non-live data sources: " + ", ".join(stale))


if __name__ == "__main__":
    main()
