from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

from egx_quant.panel import PanelRow
from egx_quant.panel_manifest import freeze_development_panel_manifest


def load_panel(path: str | Path) -> tuple[PanelRow, ...]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError("panel JSON must be a list")
    return tuple(
        PanelRow(
            canonical_security_id=item["canonical_security_id"],
            session_date=date.fromisoformat(item["session_date"]),
            values=item["values"],
        )
        for item in raw
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Freeze a model-development panel only after row-level evidence is authorized."
    )
    parser.add_argument("--panel", required=True)
    parser.add_argument("--evidence-manifest", required=True)
    parser.add_argument("--code-ref", required=True)
    parser.add_argument("--output", default="evidence/frozen_development_panel.json")
    parser.add_argument("--created-at", default=None)
    args = parser.parse_args()

    rows = load_panel(args.panel)
    evidence_manifest = json.loads(
        Path(args.evidence_manifest).read_text(encoding="utf-8")
    )
    manifest = freeze_development_panel_manifest(
        rows,
        frozen_evidence_manifest=evidence_manifest,
        code_ref=args.code_ref,
        created_at=args.created_at,
    )
    Path(args.output).write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        f"FROZEN: {manifest['row_count']} rows, "
        f"{manifest['security_count']} securities, "
        f"through {manifest['last_session']}"
    )


if __name__ == "__main__":
    main()
