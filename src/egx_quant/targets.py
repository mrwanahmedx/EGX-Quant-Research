from __future__ import annotations

from math import isfinite


def forward_return(entry_price: float, exit_price: float) -> float:
    if not isfinite(entry_price) or not isfinite(exit_price):
        raise ValueError("prices must be finite")
    if entry_price <= 0 or exit_price < 0:
        raise ValueError("invalid price")
    return exit_price / entry_price - 1.0


def residual_return(asset_return: float, benchmark_return: float) -> float:
    if not isfinite(asset_return) or not isfinite(benchmark_return):
        raise ValueError("returns must be finite")
    return asset_return - benchmark_return
