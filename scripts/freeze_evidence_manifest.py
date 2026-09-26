from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

from egx_quant.evidence_manifest import freeze_preholdout_evidence_manifest
from egx_quant.io import dump_json, load_evidence_json, load_quarantine_csv


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Freeze a pre-holdout EGX data-evidence manifest."
    )
    parser.add_argument("--evidence", required=True)
    parser.add_argument("--quarantine-register", required=True)
    parser.add_argument("--decision-time", required=True)
    parser.add_argument("--code-ref", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    records = load_evidence_json(args.evidence)
    quarantines = load_quarantine_csv(args.quarantine_register)
    decision_time = datetime.fromisoformat(
        args.decision_time.replace("Z", "+00:00")
    )

    manifest = freeze_preholdout_evidence_manifest(
        records,
        decision_time=decision_time,
        code_ref=args.code_ref,
        quarantines=quarantines,
    )
    dump_json(args.output, manifest)

    state = "AUTHORIZED" if manifest["modeling_authorized"] else "BLOCKED"
    print(
        f"{state}: {manifest['eligible_record_count']}/"
        f"{manifest['record_count']} evidence rows eligible"
    )


if __name__ == "__main__":
    main()
