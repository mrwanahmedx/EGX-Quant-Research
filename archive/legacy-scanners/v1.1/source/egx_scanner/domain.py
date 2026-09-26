from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum


class Strategy(str, Enum):
    CORE = "CORE"
    ACTIVE = "ACTIVE"


class Action(str, Enum):
    BUY = "BUY"
    ADD = "ADD"
    HOLD = "HOLD"
    TRIM = "TRIM"
    SELL = "SELL"
    ROTATE = "ROTATE"
    WATCH = "WATCH"


@dataclass(frozen=True)
class Bar:
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass(frozen=True)
class Security:
    ticker: str
    name: str
    sector: str
    price: float
    pe: float | None
    pb: float | None
    roe: float | None
    earnings_growth: float | None
    revenue_growth: float | None
    dividend_yield: float | None
    debt_to_equity: float | None
    sector_metrics: dict[str, float] = field(default_factory=dict)
    asset_type: str = "STOCK"
    data_as_of: date | None = None


@dataclass(frozen=True)
class Holding:
    ticker: str
    quantity: float
    avg_cost: float
    market_value: float
    bucket: Strategy


@dataclass(frozen=True)
class Catalyst:
    ticker: str
    published: date
    headline: str
    text: str
    source: str = "manual"


@dataclass
class ScoreCard:
    ticker: str
    fundamental: float
    valuation: float
    technical_daily: float
    technical_weekly: float
    catalyst: float
    portfolio_fit: float
    liquidity: float
    core: float = 0
    active: float = 0
    data_quality: float = 0
    has_real_history: bool = False
    reasons: list[str] = field(default_factory=list)


@dataclass
class Recommendation:
    ticker: str
    strategy: Strategy
    action: Action
    score: float
    confidence: float
    price: float
    entry_low: float
    entry_high: float
    stop: float
    target_1: float
    target_2: float
    allocation_egp: float
    shares: int
    reasons: list[str]
    data_quality: float = 0
    rotate_to: str | None = None
