from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class RankedSecurity:
    security_id: str
    score: float


def top_k(ranked: Iterable[RankedSecurity], k: int) -> tuple[str, ...]:
    if k <= 0:
        raise ValueError("k must be positive")
    ordered = sorted(ranked, key=lambda x: (-x.score, x.security_id))
    return tuple(item.security_id for item in ordered[:k])


def one_way_turnover(previous: Iterable[str], current: Iterable[str]) -> float:
    prev = set(previous)
    curr = set(current)
    if not prev and not curr:
        return 0.0
    base = max(len(prev), len(curr), 1)
    return len(curr - prev) / base


def dropout_rebalance(
    previous: Iterable[str],
    ranked: Iterable[RankedSecurity],
    *,
    k: int,
    drop_buffer: int,
) -> tuple[str, ...]:
    """Keep incumbents unless they fall below rank k + drop_buffer."""
    if k <= 0 or drop_buffer < 0:
        raise ValueError("invalid portfolio parameters")
    ordered = sorted(ranked, key=lambda x: (-x.score, x.security_id))
    rank = {item.security_id: i + 1 for i, item in enumerate(ordered)}
    keep = [
        security_id
        for security_id in previous
        if rank.get(security_id, 10**9) <= k + drop_buffer
    ]
    selected = list(dict.fromkeys(keep))
    for item in ordered:
        if item.security_id not in selected:
            selected.append(item.security_id)
        if len(selected) == k:
            break
    return tuple(selected[:k])
