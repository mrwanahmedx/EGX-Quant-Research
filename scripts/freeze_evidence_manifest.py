from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path

from egx_quant.evidence_manifest import freeze_preholdout_evidence_manifest
from egx_quant.io import dump_json, load_evidence_json, load_quarantine_csv
from egx_quant.source_snapshot import validate_frozen_source_snapshot_manifest
from egx_quant.sources import load_source_catalog


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Freeze a pre-holdout EGX data-evidence manifest."
    )
    parser.add_argument("--evidence", required=True)
    parser.add_argument("--quarantine-register", required=True)
    parser.add_argument("--source-snapshot-manifest", required=True)
    parser.add_argument("--source-catalog", default="config/source_catalog.json")
    parser.add_argument("--decision-time", required=True)
    parser.add_argument("--code-ref", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    records = load_evidence_json(args.evidence)
    quarantines = load_quarantine_csv(args.quarantine_register)
    source_snapshot_manifest = json.loads(
        Path(args.source_snapshot_manifest).read_text(encoding="utf-8")
    )
    source_catalog = load_source_catalog(args.source_catalog)
    validate_frozen_source_snapshot_manifest(
        source_snapshot_manifest,
        source_catalog=source_catalog,
    )
    decision_time = datetime.fromisoformat(
        args.decision_time.replace("Z", "+00:00")
    )

    manifest = freeze_preholdout_evidence_manifest(
        records,
        decision_time=decision_time,
        code_ref=args.code_ref,
        source_snapshot_fingerprint=source_snapshot_manifest[
            "composite_fingerprint"
        ],
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
