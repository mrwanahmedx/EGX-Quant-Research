from __future__ import annotations

import argparse
from pathlib import Path

from egx_quant.evidence_io import (
    evidence_records_to_jsonable,
    fingerprint_evidence_csv,
    load_evidence_csv,
)
from egx_quant.io import dump_json


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Convert audited row-level evidence CSV into the canonical "
            "pre-holdout JSON evidence format."
        )
    )
    parser.add_argument("source_csv")
    parser.add_argument(
        "--output",
        default="evidence/data_evidence_records.json",
    )
    args = parser.parse_args()

    records = load_evidence_csv(args.source_csv)
    fingerprint = fingerprint_evidence_csv(args.source_csv)
    destination = Path(args.output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    dump_json(destination, evidence_records_to_jsonable(records))

    print(f"IMPORTED: {len(records)} evidence rows -> {destination}")
    print(f"EVIDENCE_FINGERPRINT: {fingerprint}")


if __name__ == "__main__":
    main()
