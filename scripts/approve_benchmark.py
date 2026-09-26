from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from egx_quant.benchmark_approval import approve_frozen_benchmark
from egx_quant.benchmarks import load_benchmark_catalog
from egx_quant.sources import load_source_catalog


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Approve a frozen benchmark series only after explicit review."
    )
    parser.add_argument("--benchmark-id", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--manifest-ref", required=True)
    parser.add_argument("--reviewer", required=True)
    parser.add_argument("--catalog", default="config/benchmark_catalog.json")
    parser.add_argument("--sources", default="config/source_catalog.json")
    parser.add_argument("--review-output", required=True)
    parser.add_argument("--reviewed-at", default=None)
    parser.add_argument("--notes", default="")
    parser.add_argument("--confirm-methodology", action="store_true")
    parser.add_argument("--confirm-source-snapshot", action="store_true")
    parser.add_argument("--confirm-return-convention", action="store_true")
    args = parser.parse_args()

    benchmarks = list(load_benchmark_catalog(args.catalog))
    sources = load_source_catalog(args.sources)
    benchmark = next(
        (b for b in benchmarks if b.benchmark_id == args.benchmark_id),
        None,
    )
    if benchmark is None:
        raise SystemExit(f"benchmark not found: {args.benchmark_id}")
    source = next(s for s in sources if s.source_id == benchmark.source_id)
    frozen = json.loads(Path(args.manifest).read_text(encoding="utf-8"))

    approved, review = approve_frozen_benchmark(
        benchmark,
        source,
        frozen,
        frozen_manifest_ref=args.manifest_ref,
        reviewer=args.reviewer,
        methodology_reviewed=args.confirm_methodology,
        source_snapshot_reviewed=args.confirm_source_snapshot,
        return_convention_reviewed=args.confirm_return_convention,
        reviewed_at=args.reviewed_at,
        notes=args.notes,
    )

    benchmarks = [
        approved if item.benchmark_id == approved.benchmark_id else item
        for item in benchmarks
    ]
    Path(args.catalog).write_text(
        json.dumps([asdict(item) for item in benchmarks], indent=2) + "\n",
        encoding="utf-8",
    )
    output = Path(args.review_output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(review, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        f"APPROVED: {approved.benchmark_id} "
        f"{approved.series_fingerprint[:12]}..."
    )


if __name__ == "__main__":
    main()
