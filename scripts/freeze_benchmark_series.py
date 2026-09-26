from __future__ import annotations

import argparse
import csv
import json
from datetime import date
from pathlib import Path

from egx_quant.benchmark_series import (
    BenchmarkObservation,
    freeze_benchmark_series_manifest,
)


def load_series(path: str | Path) -> tuple[BenchmarkObservation, ...]:
    with Path(path).open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError("benchmark CSV is empty")
    required = {"date", "value"}
    missing = required - set(rows[0])
    if missing:
        raise ValueError(f"benchmark CSV missing columns: {sorted(missing)}")
    return tuple(
        BenchmarkObservation(
            session_date=date.fromisoformat(row["date"].strip()),
            value=float(row["value"]),
        )
        for row in rows
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Freeze a pre-holdout benchmark series manifest."
    )
    parser.add_argument("--series", required=True)
    parser.add_argument("--benchmark-id", required=True)
    parser.add_argument("--source-id", required=True)
    parser.add_argument("--source-snapshot-ref", required=True)
    parser.add_argument("--return-convention", required=True)
    parser.add_argument("--methodology-ref", required=True)
    parser.add_argument("--code-ref", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    observations = load_series(args.series)
    manifest = freeze_benchmark_series_manifest(
        observations,
        benchmark_id=args.benchmark_id,
        source_id=args.source_id,
        source_snapshot_ref=args.source_snapshot_ref,
        return_convention=args.return_convention,
        methodology_ref=args.methodology_ref,
        code_ref=args.code_ref,
        approved_for_model_comparison=False,
    )
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        f"FROZEN, NOT YET APPROVED: {manifest['benchmark_id']} "
        f"{manifest['observation_count']} observations "
        f"through {manifest['last_date']}"
    )


if __name__ == "__main__":
    main()
