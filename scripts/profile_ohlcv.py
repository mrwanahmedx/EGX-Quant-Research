from __future__ import annotations

import argparse
import csv
import json
from datetime import date
from pathlib import Path

from egx_quant.quality import (
    OHLCVRecord,
    detect_close_discontinuities,
    profile_quality,
)


def load_csv(path: str) -> tuple[OHLCVRecord, ...]:
    with Path(path).open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        required = {
            "canonical_security_id",
            "session_date",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "source",
        }
        missing = required - set(reader.fieldnames or ())
        if missing:
            raise ValueError(f"missing columns: {sorted(missing)}")
        rows = [
            OHLCVRecord(
                canonical_security_id=row["canonical_security_id"],
                session_date=date.fromisoformat(row["session_date"]),
                open=float(row["open"]),
                high=float(row["high"]),
                low=float(row["low"]),
                close=float(row["close"]),
                volume=float(row["volume"]),
                source=row["source"],
            )
            for row in reader
        ]
    return tuple(rows)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Profile canonical EGX OHLCV without repairing data."
    )
    parser.add_argument("csv_path")
    parser.add_argument("--output", required=True)
    parser.add_argument(
        "--discontinuity-threshold",
        type=float,
        required=True,
        help="Absolute close-to-close return threshold, e.g. 0.30.",
    )
    args = parser.parse_args()

    rows = load_csv(args.csv_path)
    report = profile_quality(rows)
    flags = detect_close_discontinuities(
        rows,
        absolute_return_threshold=args.discontinuity_threshold,
    )
    report["discontinuity_flag_count"] = len(flags)
    report["discontinuities"] = [
        {
            "canonical_security_id": flag.canonical_security_id,
            "previous_date": flag.previous_date.isoformat(),
            "session_date": flag.session_date.isoformat(),
            "source": flag.source,
            "previous_close": flag.previous_close,
            "current_close": flag.current_close,
            "absolute_return": flag.absolute_return,
        }
        for flag in flags
    ]
    Path(args.output).write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        f"profiled {report['record_count']} rows; "
        f"affected source-grain rows="
        f"{report['affected_source_grain_count']}; "
        f"discontinuity flags={len(flags)}"
    )


if __name__ == "__main__":
    main()
