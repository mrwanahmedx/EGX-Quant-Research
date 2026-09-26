from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime


@dataclass(frozen=True)
class ShadowPrediction:
    prediction_id: str
    model_id: str
    canonical_security_id: str
    decision_time: datetime
    target_horizon: int
    score: float
    rank: int
    source_vintage: str
    data_fingerprint: str
    execution_convention: str
    hypothetical_entry_time: datetime | None = None
    hypothetical_entry_price: float | None = None
    realized_target: float | None = None
    outcome_observed_at: datetime | None = None
    notes: str = ""

    def __post_init__(self) -> None:
        if self.target_horizon not in {20, 63}:
            raise ValueError("target horizon must be 20 or 63 sessions")
        if self.rank <= 0:
            raise ValueError("rank must be positive")
        if len(self.data_fingerprint) < 16:
            raise ValueError("data fingerprint is too short")
        if self.hypothetical_entry_price is not None and self.hypothetical_entry_price <= 0:
            raise ValueError("entry price must be positive")
        if self.hypothetical_entry_time is not None:
            if self.hypothetical_entry_time < self.decision_time:
                raise ValueError("entry cannot precede the prediction decision")
        if self.realized_target is None and self.outcome_observed_at is not None:
            raise ValueError("outcome timestamp supplied without realized outcome")
        if self.realized_target is not None:
            if self.outcome_observed_at is None:
                raise ValueError("realized outcome requires observation timestamp")
            if self.outcome_observed_at <= self.decision_time:
                raise ValueError("outcome cannot be known at decision time")


def attach_realized_outcome(
    prediction: ShadowPrediction,
    *,
    realized_target: float,
    observed_at: datetime,
) -> ShadowPrediction:
    if prediction.realized_target is not None:
        raise RuntimeError("prediction outcome is already recorded")
    if observed_at <= prediction.decision_time:
        raise ValueError("outcome observation must follow decision time")
    return replace(
        prediction,
        realized_target=realized_target,
        outcome_observed_at=observed_at,
    )
