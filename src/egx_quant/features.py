from __future__ import annotations

from math import log, sqrt
from statistics import pstdev
from typing import Sequence


def simple_return(current: float, previous: float) -> float:
    if previous <= 0 or current < 0:
        raise ValueError("invalid prices")
    return current / previous - 1.0


def lagged_return(prices: Sequence[float], lag: int) -> float:
    """Return the most recent lag return using only the supplied history."""
    if lag <= 0:
        raise ValueError("lag must be positive")
    if len(prices) <= lag:
        raise ValueError("insufficient history")
    return simple_return(prices[-1], prices[-1 - lag])


def log_return(current: float, previous: float) -> float:
    if current <= 0 or previous <= 0:
        raise ValueError("log return requires positive prices")
    return log(current / previous)


def rolling_volatility(prices: Sequence[float], window: int) -> float:
    """Population stdev of historical one-period log returns."""
    if window < 2:
        raise ValueError("window must be at least 2")
    if len(prices) < window + 1:
        raise ValueError("insufficient history")
    tail = prices[-(window + 1):]
    returns = [log_return(tail[i], tail[i - 1]) for i in range(1, len(tail))]
    return pstdev(returns)


def zscore(value: float, mean: float, std: float) -> float:
    if std <= 0:
        raise ValueError("std must be positive")
    return (value - mean) / std
