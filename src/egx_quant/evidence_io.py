from __future__ import annotations

import csv
from datetime import date, datetime
from pathlib import Path

from .evidence import DataEvidenceRecord, evidence_fingerprint


FIELDNAMES = [
    "canonical_security_id",
    "session_date",
    "source_fingerprint",
    "price_basis",
    "qa_status",
    "point_in_time_membership",
    "corporate_action_status",
    "benchmark_available",
    "observed_at",
    "published_at",
    "quarantine_id",
    "source",
    "source_vintage",
]


def _parse_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes"}:
        return True
    if normalized in {"0", "false", "no"}:
        return False
    raise ValueError(f"invalid boolean value: {value!r}")


def _parse_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def load_evidence_csv(path: str | Path) -> tuple[DataEvidenceRecord, ...]:
    """Load evidence rows from CSV using the same contract as JSON evidence.

    CSV is useful for audited row-level evidence exported from spreadsheet or
    reconciliation tooling. It does not bypass the existing evidence model.
    """
    with Path(path).open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        missing = set(FIELDNAMES) - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"evidence CSV missing fields: {sorted(missing)}")

        output: list[DataEvidenceRecord] = []
        for row in reader:
            output.append(
                DataEvidenceRecord(
                    canonical_security_id=row["canonical_security_id"].strip(),
                    session_date=date.fromisoformat(row["session_date"].strip()),
                    source_fingerprint=row["source_fingerprint"].strip(),
                    price_basis=row["price_basis"].strip(),
                    qa_status=row["qa_status"].strip(),
                    point_in_time_membership=_parse_bool(
                        row["point_in_time_membership"]
                    ),
                    corporate_action_status=row[
                        "corporate_action_status"
                    ].strip(),
                    benchmark_available=_parse_bool(row["benchmark_available"]),
                    observed_at=_parse_datetime(row["observed_at"].strip()),
                    published_at=(
                        _parse_datetime(row["published_at"].strip())
                        if row["published_at"].strip()
                        else None
                    ),
                    quarantine_id=row["quarantine_id"].strip() or None,
                    source=row["source"].strip() or None,
                    source_vintage=row["source_vintage"].strip() or None,
                )
            )
    return tuple(output)


def fingerprint_evidence_csv(path: str | Path) -> str:
    """Return the canonical evidence fingerprint for a CSV export."""
    return evidence_fingerprint(load_evidence_csv(path))
