from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from statistics import mean
from typing import Iterable

from .costs import ExecutionCostModel
from .metrics import rank_ic
from .portfolio import RankedSecurity, one_way_turnover, top_k
from .readiness import ReadinessReport


@dataclass(frozen=True)
class BaselineObservation:
    session_date: date
    canonical_security_id: str
    score: float
    target_return: float


@dataclass(frozen=True)
class BaselineResult:
    session_count: int
    observation_count: int
    mean_rank_ic: float
    positive_ic_fraction: float
    mean_one_way_turnover: float
    gross_mean_period_return: float
    net_mean_period_return: float


def require_readiness(report: ReadinessReport) -> None:
    if not report.modeling_authorized:
        blockers = ", ".join(check.check_id for check in report.blockers)
        raise RuntimeError(
            "real baseline execution blocked by repository readiness gates"
            + (f": {blockers}" if blockers else "")
        )


def evaluate_transparent_rank_baseline(
    observations: Iterable[BaselineObservation],
    *,
    k: int,
    cost_model: ExecutionCostModel,
) -> BaselineResult:
    rows = tuple(observations)
    if not rows:
        raise ValueError("baseline observations are empty")
    if k <= 0:
        raise ValueError("k must be positive")

    grouped: dict[date, list[BaselineObservation]] = {}
    seen: set[tuple[date, str]] = set()
    for row in rows:
        key = (row.session_date, row.canonical_security_id)
        if key in seen:
            raise ValueError(f"duplicate baseline observation grain: {key}")
        seen.add(key)
        grouped.setdefault(row.session_date, []).append(row)

    rank_ics: list[float] = []
    turnovers: list[float] = []
    gross_period_returns: list[float] = []
    net_period_returns: list[float] = []
    previous: tuple[str, ...] = ()

    for session in sorted(grouped):
        day = grouped[session]
        if len(day) < 2:
            raise ValueError(
                f"at least two cross-sectional observations required on {session}"
            )
        if len(day) < k:
            raise ValueError(
                f"top-k={k} exceeds available securities on {session}"
            )

        scores = [row.score for row in day]
        outcomes = [row.target_return for row in day]
        rank_ics.append(rank_ic(scores, outcomes))

        selected = top_k(
            (
                RankedSecurity(row.canonical_security_id, row.score)
                for row in day
            ),
            k,
        )
        selected_set = set(selected)
        gross = mean(
            row.target_return
            for row in day
            if row.canonical_security_id in selected_set
        )

        turnover = one_way_turnover(previous, selected) if previous else 1.0
        # Equal-weight rebalance approximation: turnover is the fraction of
        # names entering the portfolio. Each replacement implies one exit and
        # one entry, so apply two one-way cost legs.
        cost = 2.0 * turnover * cost_model.one_way_bps / 10_000.0

        turnovers.append(turnover)
        gross_period_returns.append(gross)
        net_period_returns.append(gross - cost)
        previous = selected

    return BaselineResult(
        session_count=len(grouped),
        observation_count=len(rows),
        mean_rank_ic=mean(rank_ics),
        positive_ic_fraction=sum(v > 0 for v in rank_ics) / len(rank_ics),
        mean_one_way_turnover=mean(turnovers),
        gross_mean_period_return=mean(gross_period_returns),
        net_mean_period_return=mean(net_period_returns),
    )
