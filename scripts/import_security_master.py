from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

from egx_quant.evidence_import import import_preholdout_security_master


DEFAULT_DECISION_TIME = "2026-01-31T23:59:59+02:00"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Import a validated pre-holdout point-in-time security master."
    )
    parser.add_argument("source_json")
    parser.add_argument(
        "--destination",
        default="evidence/security_master.json",
    )
    parser.add_argument(
        "--decision-time",
        default=DEFAULT_DECISION_TIME,
    )
    args = parser.parse_args()

    decision_time = datetime.fromisoformat(
        args.decision_time.replace("Z", "+00:00")
    )
    rows = import_preholdout_security_master(
        args.source_json,
        args.destination,
        decision_time=decision_time,
    )
    print(
        f"IMPORTED: {len(rows)} pre-holdout security-master records -> "
        f"{Path(args.destination)}"
    )


if __name__ == "__main__":
    main()
