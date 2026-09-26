from __future__ import annotations

import argparse
from pathlib import Path

from egx_quant.evidence_import import (
    import_exact_quarantine_register,
    update_reconciliation_import_state,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Import the original exact pre-holdout quarantine register."
    )
    parser.add_argument("source_csv")
    parser.add_argument(
        "--destination",
        default="evidence/quarantine_register.csv",
    )
    parser.add_argument(
        "--summary",
        default="evidence/reconciliation_summary.json",
    )
    parser.add_argument("--expected-count", type=int, default=47)
    args = parser.parse_args()

    rows = import_exact_quarantine_register(
        args.source_csv,
        args.destination,
        expected_count=args.expected_count,
    )
    update_reconciliation_import_state(
        args.summary,
        exact_quarantine_register_committed=True,
    )
    print(
        f"IMPORTED: {len(rows)} exact quarantine ranges -> "
        f"{Path(args.destination)}"
    )


if __name__ == "__main__":
    main()
