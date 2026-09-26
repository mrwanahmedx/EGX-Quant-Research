from __future__ import annotations

from math import sqrt
from typing import Sequence


def _average_ranks(values: Sequence[float]) -> list[float]:
    indexed = sorted(enumerate(values), key=lambda x: x[1])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(indexed):
        j = i + 1
        while j < len(indexed) and indexed[j][1] == indexed[i][1]:
            j += 1
        rank = (i + 1 + j) / 2.0
        for k in range(i, j):
            ranks[indexed[k][0]] = rank
        i = j
    return ranks


def pearson(x: Sequence[float], y: Sequence[float]) -> float:
    if len(x) != len(y) or len(x) < 2:
        raise ValueError("series must have equal length >= 2")
    mx = sum(x) / len(x)
    my = sum(y) / len(y)
    dx = [v - mx for v in x]
    dy = [v - my for v in y]
    denom = sqrt(sum(v * v for v in dx) * sum(v * v for v in dy))
    if denom == 0:
        raise ValueError("correlation undefined for constant series")
    return sum(a * b for a, b in zip(dx, dy)) / denom


def rank_ic(scores: Sequence[float], outcomes: Sequence[float]) -> float:
    """Spearman rank correlation with average ranks for ties."""
    return pearson(_average_ranks(scores), _average_ranks(outcomes))
