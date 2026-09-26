from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from statistics import median
from typing import Iterable


@dataclass(frozen=True)
class LiquidityObservation:
    canonical_security_id: str
    session_date: date
    traded_value: float

    def __post_init__(self) -> None:
        if self.traded_value < 0:
            raise ValueError("traded value cannot be negative")


@dataclass(frozen=True)
class LiquidityUniversePolicy:
    lookback_observations: int
    min_observations: int
    top_n: int

    def __post_init__(self) -> None:
        if self.lookback_observations <= 0:
            raise ValueError("lookback must be positive")
        if self.min_observations <= 0:
            raise ValueError("minimum observations must be positive")
        if self.min_observations > self.lookback_observations:
            raise ValueError("minimum observations cannot exceed lookback")
        if self.top_n <= 0:
            raise ValueError("top_n must be positive")


def select_lagged_liquidity_universe(
    observations: Iterable[LiquidityObservation],
    *,
    decision_date: date,
    policy: LiquidityUniversePolicy,
) -> tuple[str, ...]:
    """Rank securities using only observations strictly before decision_date."""
    grouped: dict[str, list[LiquidityObservation]] = {}
    for obs in observations:
        if obs.session_date >= decision_date:
            continue
        grouped.setdefault(obs.canonical_security_id, []).append(obs)

    scored: list[tuple[str, float]] = []
    for security_id, rows in grouped.items():
        rows.sort(key=lambda row: row.session_date)
        tail = rows[-policy.lookback_observations :]
        if len(tail) < policy.min_observations:
            continue
        score = median(row.traded_value for row in tail)
        scored.append((security_id, score))

    scored.sort(key=lambda item: (-item[1], item[0]))
    return tuple(security_id for security_id, _ in scored[: policy.top_n])
