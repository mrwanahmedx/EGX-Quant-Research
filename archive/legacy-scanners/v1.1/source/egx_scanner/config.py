from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Settings:
    data_dir: Path = ROOT / "data"
    db_path: Path = ROOT / "work" / "egx_scanner.sqlite3"
    reserve_pct: float = 0.15
    risk_per_trade_pct: float = 0.0075
    max_position_pct: float = 0.18
    max_sector_pct: float = 0.35
    active_capital_pct: float = 0.30
    minimum_order_egp: float = 750
    min_buy_score: float = 68
    min_add_score: float = 74
    min_data_quality_for_buy: float = 55
    transaction_cost_bps_each_side: float = 35

    def validate(self) -> None:
        for value in (self.reserve_pct, self.risk_per_trade_pct, self.max_position_pct,self.max_sector_pct, self.active_capital_pct):
            if not 0 <= value <= 1:
                raise ValueError("percentage settings must be between 0 and 1")
