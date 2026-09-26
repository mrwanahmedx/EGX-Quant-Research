from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

from egx_quant.io import dump_json
from egx_quant.source_snapshot import (
    SourceSnapshot,
    freeze_source_snapshot_manifest,
)
from egx_quant.sources import load_source_catalog


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Freeze metadata for pre-holdout public source snapshots."
    )
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--source-catalog", default="config/source_catalog.json")
    parser.add_argument("--output", default="evidence/source_snapshot_manifest.json")
    args = parser.parse_args()

    raw = json.loads(Path(args.candidate).read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise SystemExit("candidate source snapshot file must be a JSON list")

    snapshots = tuple(
        SourceSnapshot(
            source_id=row["source_id"],
            source_version=row["source_version"],
            source_sha256=row["source_sha256"],
            row_count=int(row["row_count"]),
            min_session=date.fromisoformat(row["min_session"]),
            max_session=date.fromisoformat(row["max_session"]),
            license_status=row["license_status"],
            local_only=bool(row.get("local_only", True)),
            notes=row.get("notes", ""),
        )
        for row in raw
    )
    catalog = load_source_catalog(args.source_catalog)
    manifest = freeze_source_snapshot_manifest(
        snapshots,
        source_catalog=catalog,
    )
    destination = Path(args.output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    dump_json(destination, manifest)
    print(
        f"FROZEN: {len(manifest['sources'])} source snapshots -> {destination}"
    )
    print(f"COMPOSITE_FINGERPRINT: {manifest['composite_fingerprint']}")


if __name__ == "__main__":
    main()
