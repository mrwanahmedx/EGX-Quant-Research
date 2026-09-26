from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from math import isfinite
from typing import Iterable, Mapping, Sequence


class ContractError(ValueError):
    """Raised when research data violates an explicit contract."""


@dataclass(frozen=True)
class Bar:
    canonical_security_id: str
    trading_date: date
    open: float
    high: float
    low: float
    close: float
    volume: float
    source: str
    observed_at: datetime


def validate_bar(bar: Bar) -> None:
    values = (bar.open, bar.high, bar.low, bar.close, bar.volume)
    if not all(isfinite(v) for v in values):
        raise ContractError("bar contains non-finite values")
    if min(bar.open, bar.high, bar.low, bar.close) < 0:
        raise ContractError("price fields must be non-negative")
    if bar.volume < 0:
        raise ContractError("volume must be non-negative")
    if bar.low > min(bar.open, bar.close):
        raise ContractError("low exceeds open/close")
    if bar.high < max(bar.open, bar.close):
        raise ContractError("high is below open/close")
    if bar.low > bar.high:
        raise ContractError("low exceeds high")
    if not bar.canonical_security_id.strip():
        raise ContractError("canonical security id is required")
    if not bar.source.strip():
        raise ContractError("source is required")


def assert_unique(
    rows: Iterable[Mapping[str, object]],
    key_fields: Sequence[str],
) -> None:
    """Reject duplicate rows at the intended research grain."""
    seen: set[tuple[object, ...]] = set()
    for row in rows:
        key = tuple(row[field] for field in key_fields)
        if key in seen:
            raise ContractError(f"duplicate grain detected: {key}")
        seen.add(key)
