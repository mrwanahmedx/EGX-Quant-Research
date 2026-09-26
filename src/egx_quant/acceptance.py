from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Any


@dataclass(frozen=True)
class AcceptanceThresholds:
    min_mean_rank_ic: float | None
    min_positive_ic_fraction: float | None
    max_one_way_turnover: float | None
    min_net_return: float | None
    max_drawdown_abs: float | None
    multiple_testing_method: str | None
    trial_registry_required: bool

    @property
    def frozen(self) -> bool:
        return all(
            value is not None
            for value in (
                self.min_mean_rank_ic,
                self.min_positive_ic_fraction,
                self.max_one_way_turnover,
                self.min_net_return,
                self.max_drawdown_abs,
                self.multiple_testing_method,
            )
        )


@dataclass(frozen=True)
class AcceptanceDecision:
    status: str
    passed: bool
    failures: tuple[str, ...]


def load_acceptance_thresholds(
    path: str | Path,
) -> AcceptanceThresholds:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    thresholds = raw["thresholds"]
    return AcceptanceThresholds(
        min_mean_rank_ic=thresholds.get("min_mean_rank_ic"),
        min_positive_ic_fraction=thresholds.get("min_positive_ic_fraction"),
        max_one_way_turnover=thresholds.get("max_one_way_turnover"),
        min_net_return=thresholds.get("min_net_return"),
        max_drawdown_abs=thresholds.get("max_drawdown_abs"),
        multiple_testing_method=raw.get("multiple_testing_method"),
        trial_registry_required=bool(raw.get("trial_registry_required", True)),
    )


def evaluate_acceptance(
    metrics: Mapping[str, Any],
    thresholds: AcceptanceThresholds,
    *,
    trial_registry_present: bool,
) -> AcceptanceDecision:
    if not thresholds.frozen:
        return AcceptanceDecision(
            status="thresholds_not_frozen",
            passed=False,
            failures=("acceptance thresholds are not frozen",),
        )

    failures: list[str] = []

    checks = (
        (
            metrics["mean_rank_ic"] >= thresholds.min_mean_rank_ic,
            "mean Rank IC below threshold",
        ),
        (
            metrics["positive_ic_fraction"]
            >= thresholds.min_positive_ic_fraction,
            "positive IC fraction below threshold",
        ),
        (
            metrics["one_way_turnover"]
            <= thresholds.max_one_way_turnover,
            "turnover above threshold",
        ),
        (
            metrics["net_return"] >= thresholds.min_net_return,
            "net return below threshold",
        ),
        (
            abs(metrics["max_drawdown"])
            <= thresholds.max_drawdown_abs,
            "drawdown exceeds threshold",
        ),
    )

    for passed, message in checks:
        if not passed:
            failures.append(message)

    if thresholds.trial_registry_required and not trial_registry_present:
        failures.append("trial registry missing")

    return AcceptanceDecision(
        status="evaluated",
        passed=not failures,
        failures=tuple(failures),
    )
