from __future__ import annotations

import csv
import hashlib
import json
from datetime import date, datetime
from pathlib import Path
from typing import Iterable

from .evidence import EvidenceRecord, validate_evidence_record


FIELDNAMES = [
    "canonical_security_id",
    "session_date",
    "price_source",
    "source_vintage",
    "source_sha256",
    "price_basis",
    "ohlc_qa_status",
    "quarantine_status",
    "quarantine_reason",
    "point_in_time_membership_status",
    "corporate_action_status",
    "benchmark_status",
    "observed_at",
    "publication_cutoff_ok",
    "evidence_complete",
]


def _as_bool(value: str) -> bool:
    value = value.strip().lower()
    if value in {"true", "1", "yes"}:
        return True
    if value in {"false", "0", "no"}:
        return False
    raise ValueError(f"invalid boolean value: {value!r}")


def load_evidence_csv(path: str | Path) -> tuple[EvidenceRecord, ...]:
    records: list[EvidenceRecord] = []
    with Path(path).open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        missing = set(FIELDNAMES) - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"evidence CSV missing fields: {sorted(missing)}")
        for row in reader:
            record = EvidenceRecord(
                canonical_security_id=row["canonical_security_id"],
                session_date=date.fromisoformat(row["session_date"]),
                price_source=row["price_source"],
                source_vintage=row["source_vintage"],
                source_sha256=row["source_sha256"] or None,
                price_basis=row["price_basis"],
                ohlc_qa_status=row["ohlc_qa_status"],
                quarantine_status=row["quarantine_status"],
                quarantine_reason=row["quarantine_reason"] or None,
                point_in_time_membership_status=row[
                    "point_in_time_membership_status"
                ],
                corporate_action_status=row["corporate_action_status"],
                benchmark_status=row["benchmark_status"],
                observed_at=datetime.fromisoformat(
                    row["observed_at"].replace("Z", "+00:00")
                ),
                publication_cutoff_ok=_as_bool(row["publication_cutoff_ok"]),
                evidence_complete=_as_bool(row["evidence_complete"]),
            )
            validate_evidence_record(record)
            records.append(record)
    return tuple(records)


def fingerprint_evidence(records: Iterable[EvidenceRecord]) -> str:
    payload = []
    for record in records:
        validate_evidence_record(record)
        payload.append(
            {
                key: (
                    value.isoformat()
                    if hasattr(value, "isoformat")
                    else value
                )
                for key, value in record.__dict__.items()
            }
        )
    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()
