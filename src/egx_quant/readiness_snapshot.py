from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .readiness import build_repository_readiness_report


def build_readiness_snapshot(*, generated_at: str | None = None) -> dict[str, Any]:
    report = build_repository_readiness_report()
    timestamp = generated_at or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    return {
        "kind": "repository-readiness-snapshot",
        "generated_at": timestamp,
        "modeling_authorized": report.modeling_authorized,
        "blocker_count": len(report.blockers),
        "checks": [asdict(check) for check in report.checks],
    }


def write_readiness_snapshot(
    path: str | Path,
    *,
    generated_at: str | None = None,
) -> dict[str, Any]:
    payload = build_readiness_snapshot(generated_at=generated_at)
    Path(path).write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return payload
