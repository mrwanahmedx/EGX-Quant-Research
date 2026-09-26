from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Iterable, Mapping, Any

from .sources import SourceDefinition
from .splits import DEVELOPMENT_END


@dataclass(frozen=True)
class SourceSnapshot:
    source_id: str
    source_version: str
    source_sha256: str
    row_count: int
    min_session: date
    max_session: date
    license_status: str
    local_only: bool
    notes: str = ""

    def __post_init__(self) -> None:
        digest = self.source_sha256.lower()
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            raise ValueError("source_sha256 must be a 64-character hex digest")
        if self.row_count <= 0:
            raise ValueError("row_count must be positive")
        if self.max_session < self.min_session:
            raise ValueError("source session range is invalid")
        if self.max_session > DEVELOPMENT_END:
            raise ValueError(
                "pre-holdout source snapshot crosses the frozen development cutoff"
            )
        if not self.source_id.strip() or not self.source_version.strip():
            raise ValueError("source_id and source_version are required")
        if not self.license_status.strip():
            raise ValueError("license_status is required")


def validate_snapshot_sources(
    snapshots: Iterable[SourceSnapshot],
    source_catalog: Iterable[SourceDefinition],
) -> tuple[SourceSnapshot, ...]:
    snapshots = tuple(snapshots)
    if not snapshots:
        raise ValueError("at least one source snapshot is required")

    catalog = {source.source_id: source for source in source_catalog}
    ids = [snapshot.source_id for snapshot in snapshots]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate source_id in frozen snapshot manifest")

    for snapshot in snapshots:
        source = catalog.get(snapshot.source_id)
        if source is None:
            raise ValueError(
                f"source snapshot references unknown catalog source: {snapshot.source_id}"
            )
        if snapshot.license_status != source.license_status:
            raise ValueError(
                f"license status mismatch for {snapshot.source_id}: "
                f"{snapshot.license_status!r} != {source.license_status!r}"
            )

    return tuple(sorted(snapshots, key=lambda x: x.source_id))


def composite_source_fingerprint(
    snapshots: Iterable[SourceSnapshot],
) -> str:
    ordered = sorted(snapshots, key=lambda x: x.source_id)
    payload = [
        {
            "source_id": item.source_id,
            "source_version": item.source_version,
            "source_sha256": item.source_sha256.lower(),
            "row_count": item.row_count,
            "min_session": item.min_session.isoformat(),
            "max_session": item.max_session.isoformat(),
            "license_status": item.license_status,
            "local_only": item.local_only,
            "notes": item.notes,
        }
        for item in ordered
    ]
    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def freeze_source_snapshot_manifest(
    snapshots: Iterable[SourceSnapshot],
    *,
    source_catalog: Iterable[SourceDefinition],
    created_at: str | None = None,
) -> dict[str, Any]:
    snapshots = validate_snapshot_sources(snapshots, source_catalog)
    return {
        "kind": "frozen-preholdout-source-snapshot",
        "created_at": created_at
        or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "development_cutoff": DEVELOPMENT_END.isoformat(),
        "sources": [
            {
                "source_id": item.source_id,
                "source_version": item.source_version,
                "source_sha256": item.source_sha256.lower(),
                "row_count": item.row_count,
                "min_session": item.min_session.isoformat(),
                "max_session": item.max_session.isoformat(),
                "license_status": item.license_status,
                "local_only": item.local_only,
                "notes": item.notes,
            }
            for item in snapshots
        ],
        "composite_fingerprint": composite_source_fingerprint(snapshots),
        "authorized_for_development": True,
    }


def validate_frozen_source_snapshot_manifest(
    manifest: Mapping[str, Any],
    *,
    source_catalog: Iterable[SourceDefinition],
) -> None:
    if manifest.get("kind") != "frozen-preholdout-source-snapshot":
        raise ValueError("unexpected source snapshot manifest kind")
    if manifest.get("development_cutoff") != DEVELOPMENT_END.isoformat():
        raise ValueError("development cutoff does not match repository contract")
    if manifest.get("authorized_for_development") is not True:
        raise ValueError("source snapshot manifest is not authorized")

    snapshots = tuple(
        SourceSnapshot(
            source_id=row["source_id"],
            source_version=row["source_version"],
            source_sha256=row["source_sha256"],
            row_count=int(row["row_count"]),
            min_session=date.fromisoformat(row["min_session"]),
            max_session=date.fromisoformat(row["max_session"]),
            license_status=row["license_status"],
            local_only=bool(row["local_only"]),
            notes=row.get("notes", ""),
        )
        for row in manifest["sources"]
    )
    snapshots = validate_snapshot_sources(snapshots, source_catalog)
    expected = composite_source_fingerprint(snapshots)
    if manifest.get("composite_fingerprint") != expected:
        raise ValueError("source snapshot composite fingerprint mismatch")
