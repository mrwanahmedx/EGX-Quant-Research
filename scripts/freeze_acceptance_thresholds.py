from __future__ import annotations

import argparse
import json
from pathlib import Path

from egx_quant.acceptance import AcceptanceThresholds
from egx_quant.acceptance_freeze import freeze_acceptance_thresholds


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Freeze development acceptance thresholds before holdout evaluation."
    )
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--code-ref", required=True)
    parser.add_argument("--development-evidence-ref", required=True)
    parser.add_argument("--rationale", required=True)
    parser.add_argument("--output", default="config/acceptance.frozen.json")
    parser.add_argument("--frozen-at", default=None)
    args = parser.parse_args()

    raw = json.loads(Path(args.candidate).read_text(encoding="utf-8"))
    values = raw["thresholds"]
    thresholds = AcceptanceThresholds(
        min_mean_rank_ic=values.get("min_mean_rank_ic"),
        min_positive_ic_fraction=values.get("min_positive_ic_fraction"),
        max_one_way_turnover=values.get("max_one_way_turnover"),
        min_net_return=values.get("min_net_return"),
        max_drawdown_abs=values.get("max_drawdown_abs"),
        multiple_testing_method=raw.get("multiple_testing_method"),
        trial_registry_required=bool(raw.get("trial_registry_required", True)),
    )

    payload = freeze_acceptance_thresholds(
        thresholds,
        code_ref=args.code_ref,
        development_evidence_ref=args.development_evidence_ref,
        rationale=args.rationale,
        holdout_unopened=True,
        frozen_at=args.frozen_at,
    )
    Path(args.output).write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"FROZEN: acceptance thresholds -> {args.output}")


if __name__ == "__main__":
    main()
