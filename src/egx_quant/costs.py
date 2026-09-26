from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ExecutionCostModel:
    """Simple transparent bps-based execution-cost model."""

    commission_bps: float = 0.0
    slippage_bps: float = 0.0
    taxes_fees_bps: float = 0.0

    def __post_init__(self) -> None:
        if min(self.commission_bps, self.slippage_bps, self.taxes_fees_bps) < 0:
            raise ValueError("cost assumptions cannot be negative")

    @property
    def one_way_bps(self) -> float:
        return self.commission_bps + self.slippage_bps + self.taxes_fees_bps

    def apply_round_trip(self, gross_return: float) -> float:
        return gross_return - 2.0 * self.one_way_bps / 10_000.0

    def apply_one_way(self, gross_return: float) -> float:
        return gross_return - self.one_way_bps / 10_000.0
