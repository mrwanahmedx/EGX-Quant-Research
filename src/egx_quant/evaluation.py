from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from math import sqrt
from statistics import mean, pstdev
from typing import Iterable

from .metrics import rank_ic


@dataclass(frozen=True)
class PredictionObservation:
    session_date: date
    canonical_security_id: str
    score: float
    realized_target: float


@dataclass(frozen=True)
class RankICSummary:
    dates_evaluated: int
    mean_rank_ic: float
    std_rank_ic: float
    ic_ir: float | None
    positive_fraction: float


def rank_ic_by_session(
    rows: Iterable[PredictionObservation],
) -> dict[date, float]:
    grouped: dict[date, list[PredictionObservation]] = {}
    for row in rows:
        grouped.setdefault(row.session_date, []).append(row)

    result: dict[date, float] = {}
    for session_date, observations in sorted(grouped.items()):
        if len(observations) < 2:
            continue
        scores = [row.score for row in observations]
        targets = [row.realized_target for row in observations]
        try:
            result[session_date] = rank_ic(scores, targets)
        except ValueError:
            continue
    return result


def summarize_rank_ic(
    values: Iterable[float],
) -> RankICSummary:
    values = tuple(values)
    if not values:
        raise ValueError("at least one Rank IC value is required")
    avg = mean(values)
    std = pstdev(values)
    return RankICSummary(
        dates_evaluated=len(values),
        mean_rank_ic=avg,
        std_rank_ic=std,
        ic_ir=(avg / std if std > 0 else None),
        positive_fraction=sum(value > 0 for value in values) / len(values),
    )


def annualized_sharpe(
    periodic_returns: Iterable[float],
    *,
    periods_per_year: int,
) -> float:
    values = tuple(periodic_returns)
    if len(values) < 2:
        raise ValueError("at least two returns are required")
    if periods_per_year <= 0:
        raise ValueError("periods_per_year must be positive")
    std = pstdev(values)
    if std == 0:
        raise ValueError("Sharpe is undefined for zero-volatility returns")
    return mean(values) / std * sqrt(periods_per_year)


def max_drawdown(equity_curve: Iterable[float]) -> float:
    values = tuple(equity_curve)
    if not values:
        raise ValueError("equity curve cannot be empty")
    peak = values[0]
    if peak <= 0:
        raise ValueError("equity values must be positive")
    worst = 0.0
    for value in values:
        if value <= 0:
            raise ValueError("equity values must be positive")
        peak = max(peak, value)
        drawdown = value / peak - 1.0
        worst = min(worst, drawdown)
    return worst
