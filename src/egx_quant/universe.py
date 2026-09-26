from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime


@dataclass(frozen=True)
class MembershipRecord:
    canonical_security_id: str
    effective_from: date
    effective_to: date | None
    published_at: datetime
    source: str


def membership_is_usable(
    record: MembershipRecord,
    *,
    session_date: date,
    decision_time: datetime,
) -> bool:
    """Return True only if membership was valid and known at decision time."""
    if record.published_at > decision_time:
        return False
    if session_date < record.effective_from:
        return False
    if record.effective_to is not None and session_date > record.effective_to:
        return False
    return True


def require_point_in_time_membership(
    record: MembershipRecord | None,
    *,
    session_date: date,
    decision_time: datetime,
) -> None:
    if record is None or not membership_is_usable(
        record,
        session_date=session_date,
        decision_time=decision_time,
    ):
        raise RuntimeError("point-in-time membership evidence is unavailable")
