from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Iterable


@dataclass(frozen=True)
class SecurityMasterRecord:
    canonical_security_id: str
    symbol: str
    effective_from: date
    effective_to: date | None
    published_at: datetime
    source: str
    mapping_confidence: str
    sector: str | None = None
    sector_effective_from: date | None = None
    sector_published_at: datetime | None = None

    def __post_init__(self) -> None:
        if self.effective_to is not None and self.effective_to < self.effective_from:
            raise ValueError("security-master effective range is invalid")
        if self.mapping_confidence not in {"verified", "probable", "unresolved"}:
            raise ValueError("unsupported mapping confidence")


def _usable(
    record: SecurityMasterRecord,
    *,
    symbol: str,
    session_date: date,
    decision_time: datetime,
) -> bool:
    if record.symbol != symbol:
        return False
    if record.mapping_confidence == "unresolved":
        return False
    if record.published_at > decision_time:
        return False
    if session_date < record.effective_from:
        return False
    if record.effective_to is not None and session_date > record.effective_to:
        return False
    return True


def resolve_symbol(
    records: Iterable[SecurityMasterRecord],
    *,
    symbol: str,
    session_date: date,
    decision_time: datetime,
) -> SecurityMasterRecord:
    matches = [
        record
        for record in records
        if _usable(
            record,
            symbol=symbol,
            session_date=session_date,
            decision_time=decision_time,
        )
    ]
    if not matches:
        raise RuntimeError(
            f"no point-in-time security-master evidence for {symbol} on {session_date}"
        )
    ids = {record.canonical_security_id for record in matches}
    if len(ids) != 1:
        raise RuntimeError(
            f"ambiguous point-in-time security identity for {symbol} on {session_date}"
        )
    return max(matches, key=lambda r: (r.effective_from, r.published_at))


def sector_as_of(
    record: SecurityMasterRecord,
    *,
    session_date: date,
    decision_time: datetime,
) -> str:
    if record.sector is None:
        raise RuntimeError("sector evidence unavailable")
    if record.sector_effective_from is None or record.sector_published_at is None:
        raise RuntimeError("sector effective/publication dates unavailable")
    if record.sector_effective_from > session_date:
        raise RuntimeError("sector classification not yet effective")
    if record.sector_published_at > decision_time:
        raise RuntimeError("sector classification was not yet published")
    return record.sector
