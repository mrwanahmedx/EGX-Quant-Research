import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from .domain import Recommendation


SCHEMA = """
CREATE TABLE IF NOT EXISTS scan_runs(id INTEGER PRIMARY KEY, created_at TEXT NOT NULL, as_of TEXT NOT NULL, fresh_capital REAL NOT NULL);
CREATE TABLE IF NOT EXISTS signals(id INTEGER PRIMARY KEY, run_id INTEGER NOT NULL, ticker TEXT NOT NULL, strategy TEXT NOT NULL, action TEXT NOT NULL, score REAL NOT NULL, allocation_egp REAL NOT NULL, payload TEXT NOT NULL, FOREIGN KEY(run_id) REFERENCES scan_runs(id));
CREATE TABLE IF NOT EXISTS trades(id INTEGER PRIMARY KEY, ticker TEXT NOT NULL, side TEXT NOT NULL, quantity REAL NOT NULL, price REAL NOT NULL, traded_at TEXT NOT NULL, strategy TEXT, signal_id INTEGER);
CREATE TABLE IF NOT EXISTS backtest_results(id INTEGER PRIMARY KEY, ticker TEXT NOT NULL, strategy TEXT NOT NULL, started TEXT NOT NULL, ended TEXT NOT NULL, return_pct REAL NOT NULL, max_drawdown_pct REAL NOT NULL, trades INTEGER NOT NULL, created_at TEXT NOT NULL);
"""


class Store:
    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path

    def initialize(self):
        with sqlite3.connect(self.path) as db: db.executescript(SCHEMA)

    def save_scan(self, as_of: str, capital: float, recs: list[Recommendation]) -> int:
        self.initialize()
        with sqlite3.connect(self.path) as db:
            cur = db.execute("INSERT INTO scan_runs(created_at,as_of,fresh_capital) VALUES(?,?,?)", (datetime.now(timezone.utc).isoformat(), as_of, capital))
            run_id = cur.lastrowid
            for r in recs:
                payload = json.dumps({"entry":[r.entry_low,r.entry_high],"stop":r.stop,"targets":[r.target_1,r.target_2],"reasons":r.reasons})
                db.execute("INSERT INTO signals(run_id,ticker,strategy,action,score,allocation_egp,payload) VALUES(?,?,?,?,?,?,?)", (run_id,r.ticker,r.strategy.value,r.action.value,r.score,r.allocation_egp,payload))
            return int(run_id)
