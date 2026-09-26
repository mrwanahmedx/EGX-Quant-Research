from __future__ import annotations

import argparse
from collections import Counter

from egx_quant.io import load_quarantine_csv


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate an exact machine-readable EGX quarantine register."
    )
    parser.add_argument("path")
    args = parser.parse_args()

    rows = load_quarantine_csv(args.path)
    ids = [row.quarantine_id for row in rows]
    duplicates = [key for key, count in Counter(ids).items() if count > 1]
    if duplicates:
        raise SystemExit(f"duplicate quarantine IDs: {sorted(duplicates)}")

    quarantined = sum(row.disposition == "quarantine" for row in rows)
    overrides = sum(
        row.disposition == "accepted_source_override" for row in rows
    )
    print(
        f"valid quarantine register: rows={len(rows)}, "
        f"quarantine={quarantined}, source_overrides={overrides}"
    )


if __name__ == "__main__":
    main()
