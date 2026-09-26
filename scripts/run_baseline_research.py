from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

from egx_quant.baseline import (
    BaselineObservation,
    evaluate_transparent_rank_baseline,
    require_readiness,
)
from egx_quant.costs import ExecutionCostModel
from egx_quant.readiness import build_repository_readiness_report


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the transparent rank baseline after all real-data gates pass."
    )
    parser.add_argument("--observations", required=True)
    parser.add_argument("--top-k", type=int, required=True)
    parser.add_argument("--commission-bps", type=float, default=0.0)
    parser.add_argument("--slippage-bps", type=float, default=0.0)
    parser.add_argument("--taxes-fees-bps", type=float, default=0.0)
    args = parser.parse_args()

    readiness = build_repository_readiness_report()
    try:
        require_readiness(readiness)
    except RuntimeError as exc:
        print(f"BLOCKED: {exc}")
        raise SystemExit(2)

    raw = json.loads(Path(args.observations).read_text(encoding="utf-8"))
    rows = tuple(
        BaselineObservation(
            session_date=date.fromisoformat(row["session_date"]),
            canonical_security_id=row["canonical_security_id"],
            score=float(row["score"]),
            target_return=float(row["target_return"]),
        )
        for row in raw
    )

    result = evaluate_transparent_rank_baseline(
        rows,
        k=args.top_k,
        cost_model=ExecutionCostModel(
            commission_bps=args.commission_bps,
            slippage_bps=args.slippage_bps,
            taxes_fees_bps=args.taxes_fees_bps,
        ),
    )
    print(json.dumps(result.__dict__, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
