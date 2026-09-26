from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Iterator


DEVELOPMENT_END = date(2026, 1, 31)
HOLDOUT_START = date(2026, 2, 1)
HOLDOUT_END = date(2026, 6, 30)
SHADOW_START = date(2026, 9, 1)


def classify_date(value: date) -> str:
    if value <= DEVELOPMENT_END:
        return "development"
    if HOLDOUT_START <= value <= HOLDOUT_END:
        return "holdout"
    if value >= SHADOW_START:
        return "shadow"
    return "gap"


def assert_publication_available(
    as_of: datetime,
    published_at: datetime,
) -> None:
    if published_at > as_of:
        raise ValueError(
            f"future information: published {published_at.isoformat()} "
            f"after as-of {as_of.isoformat()}"
        )


@dataclass(frozen=True)
class WalkForwardFold:
    train_start: date
    train_end: date
    validation_start: date
    validation_end: date


def purged_walk_forward(
    start: date,
    end: date,
    train_days: int,
    validation_days: int,
    purge_days: int,
) -> Iterator[WalkForwardFold]:
    """Generate deterministic calendar-day folds with a purge gap."""
    if min(train_days, validation_days) <= 0 or purge_days < 0:
        raise ValueError("invalid fold lengths")
    train_start = start
    while True:
        train_end = train_start + timedelta(days=train_days - 1)
        validation_start = train_end + timedelta(days=purge_days + 1)
        validation_end = validation_start + timedelta(days=validation_days - 1)
        if validation_end > end:
            break
        yield WalkForwardFold(
            train_start=train_start,
            train_end=train_end,
            validation_start=validation_start,
            validation_end=validation_end,
        )
        train_start = validation_start
