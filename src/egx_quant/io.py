from __future__ import annotations

import csv
import json
from datetime import date, datetime
from pathlib import Path
from typing import Iterable

from .evidence import DataEvidenceRecord, QuarantineRange
from .security_master import SecurityMasterRecord


def _parse_date(value: str) -> date:
    return date.fromisoformat(value)


def _parse_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def load_quarantine_csv(path: str | Path) -> tuple[QuarantineRange, ...]:
    with Path(path).open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))

    required = {
        "quarantine_id",
        "canonical_security_id",
        "start_date",
        "end_date",
        "conflict_class",
        "disposition",
        "evidence_ref",
    }
    missing = required - set(rows[0].keys() if rows else ())
    if missing:
        raise ValueError(f"quarantine register missing columns: {sorted(missing)}")

    output = []
    for row in rows:
        output.append(
            QuarantineRange(
                quarantine_id=row["quarantine_id"].strip(),
                canonical_security_id=row["canonical_security_id"].strip(),
                source_symbol=(row.get("source_symbol") or "").strip() or None,
                start_date=_parse_date(row["start_date"].strip()),
                end_date=_parse_date(row["end_date"].strip()),
                conflict_class=row["conflict_class"].strip(),
                disposition=row["disposition"].strip(),
                accepted_source=(row.get("accepted_source") or "").strip() or None,
                source_vintage=(row.get("source_vintage") or "").strip() or None,
                evidence_ref=row["evidence_ref"].strip(),
            )
        )
    return tuple(output)


def load_evidence_json(path: str | Path) -> tuple[DataEvidenceRecord, ...]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError("evidence JSON must be a list of row records")
    output = []
    for row in raw:
        output.append(
            DataEvidenceRecord(
                canonical_security_id=row["canonical_security_id"],
                session_date=_parse_date(row["session_date"]),
                source_fingerprint=row["source_fingerprint"],
                price_basis=row["price_basis"],
                qa_status=row["qa_status"],
                point_in_time_membership=bool(row["point_in_time_membership"]),
                corporate_action_status=row["corporate_action_status"],
                benchmark_available=bool(row["benchmark_available"]),
                observed_at=_parse_datetime(row["observed_at"]),
                published_at=(
                    _parse_datetime(row["published_at"])
                    if row.get("published_at")
                    else None
                ),
                quarantine_id=row.get("quarantine_id"),
                source=row.get("source"),
                source_vintage=row.get("source_vintage"),
            )
        )
    return tuple(output)


def load_security_master_json(path: str | Path) -> tuple[SecurityMasterRecord, ...]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError("security-master JSON must be a list of records")
    output = []
    for row in raw:
        output.append(
            SecurityMasterRecord(
                canonical_security_id=row["canonical_security_id"],
                symbol=row["symbol"],
                effective_from=_parse_date(row["effective_from"]),
                effective_to=(
                    _parse_date(row["effective_to"])
                    if row.get("effective_to")
                    else None
                ),
                published_at=_parse_datetime(row["published_at"]),
                source=row["source"],
                mapping_confidence=row["mapping_confidence"],
                sector=row.get("sector"),
                sector_effective_from=(
                    _parse_date(row["sector_effective_from"])
                    if row.get("sector_effective_from")
                    else None
                ),
                sector_published_at=(
                    _parse_datetime(row["sector_published_at"])
                    if row.get("sector_published_at")
                    else None
                ),
            )
        )
    return tuple(output)


def dump_json(path: str | Path, payload: object) -> None:
    Path(path).write_text(
        json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n",
        encoding="utf-8",
    )
