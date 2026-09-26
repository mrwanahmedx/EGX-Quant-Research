from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Iterable, Mapping

from .manifest import fingerprint_records
from .splits import DEVELOPMENT_END


@dataclass(frozen=True)
class QuarantineRange:
    quarantine_id: str
    canonical_security_id: str
    start_date: date
    end_date: date
    conflict_class: str
    disposition: str
    evidence_ref: str
    source_symbol: str | None = None
    accepted_source: str | None = None
    source_vintage: str | None = None

    def __post_init__(self) -> None:
        if self.end_date < self.start_date:
            raise ValueError("quarantine end date precedes start date")
        if self.disposition not in {
            "quarantine",
            "accepted_source_override",
            "resolved_no_quarantine",
        }:
            raise ValueError(f"unsupported quarantine disposition: {self.disposition}")

    def blocks(self, canonical_security_id: str, session_date: date) -> bool:
        return (
            self.disposition == "quarantine"
            and canonical_security_id == self.canonical_security_id
            and self.start_date <= session_date <= self.end_date
        )


@dataclass(frozen=True)
class DataEvidenceRecord:
    canonical_security_id: str
    session_date: date
    source_fingerprint: str
    price_basis: str
    qa_status: str
    point_in_time_membership: bool
    corporate_action_status: str
    benchmark_available: bool
    observed_at: datetime
    published_at: datetime | None = None
    quarantine_id: str | None = None
    source: str | None = None
    source_vintage: str | None = None

    def __post_init__(self) -> None:
        if len(self.source_fingerprint) < 16:
            raise ValueError("source fingerprint is too short")
        if self.qa_status not in {"pass", "quarantine", "rejected"}:
            raise ValueError(f"unsupported QA status: {self.qa_status}")
        if self.corporate_action_status not in {
            "not_applicable",
            "resolved",
            "unresolved",
        }:
            raise ValueError(
                f"unsupported corporate-action status: {self.corporate_action_status}"
            )
        if self.session_date > DEVELOPMENT_END:
            raise ValueError(
                "evidence record exceeds frozen development cutoff; "
                "holdout/shadow evidence belongs in a separate generation"
            )


def evidence_is_model_eligible(
    record: DataEvidenceRecord,
    *,
    decision_time: datetime,
    quarantines: Iterable[QuarantineRange] = (),
) -> bool:
    if record.qa_status != "pass":
        return False
    if not record.point_in_time_membership:
        return False
    if record.corporate_action_status == "unresolved":
        return False
    if not record.benchmark_available:
        return False
    if record.observed_at > decision_time:
        return False
    if record.published_at is not None and record.published_at > decision_time:
        return False
    return not any(
        q.blocks(record.canonical_security_id, record.session_date)
        for q in quarantines
    )


def assert_evidence_grain(records: Iterable[DataEvidenceRecord]) -> None:
    seen: set[tuple[str, date]] = set()
    for record in records:
        key = (record.canonical_security_id, record.session_date)
        if key in seen:
            raise ValueError(f"duplicate evidence grain: {key}")
        seen.add(key)


def evidence_fingerprint(records: Iterable[DataEvidenceRecord]) -> str:
    serialised: list[Mapping[str, object]] = []
    for r in sorted(records, key=lambda x: (x.canonical_security_id, x.session_date)):
        serialised.append(
            {
                "canonical_security_id": r.canonical_security_id,
                "session_date": r.session_date.isoformat(),
                "source_fingerprint": r.source_fingerprint,
                "price_basis": r.price_basis,
                "qa_status": r.qa_status,
                "point_in_time_membership": r.point_in_time_membership,
                "corporate_action_status": r.corporate_action_status,
                "benchmark_available": r.benchmark_available,
                "observed_at": r.observed_at.isoformat(),
                "published_at": (
                    r.published_at.isoformat() if r.published_at is not None else None
                ),
                "quarantine_id": r.quarantine_id,
                "source": r.source,
                "source_vintage": r.source_vintage,
            }
        )
    return fingerprint_records(serialised)
