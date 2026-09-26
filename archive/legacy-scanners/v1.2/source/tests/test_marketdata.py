import json
from datetime import date
from pathlib import Path
from unittest.mock import patch

from egx_scanner.marketdata import YahooFinancePriceAdapter, write_price_history
from egx_scanner.domain import Bar


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload
    def __enter__(self): return self
    def __exit__(self, *args): return False
    def read(self, *args): return json.dumps(self.payload).encode()


def test_yahoo_normalizes_chart_payload():
    payload = {"chart": {"error": None, "result": [{
        "timestamp": [1787702400, 1787788800],
        "indicators": {"quote": [{
            "open": [10.0, 10.5], "high": [11.0, 11.2], "low": [9.8, 10.3],
            "close": [10.7, 11.0], "volume": [1000, 1500]
        }]}
    }]}}
    adapter = YahooFinancePriceAdapter()
    with patch("egx_scanner.marketdata.urlopen", return_value=FakeResponse(payload)):
        symbol, bars = adapter.fetch_daily("TEST", "TEST.CA", 90)
    assert symbol == "TEST.CA"
    assert len(bars) == 2
    assert bars[-1].close == 11.0
    assert bars[-1].volume == 1500


def test_atomic_history_and_metadata(tmp_path: Path):
    bars = [Bar(date(2026, 8, 25), 10, 11, 9.5, 10.5, 1000),
            Bar(date(2026, 8, 26), 10.5, 12, 10.2, 11.8, 2000)]
    result = write_price_history(tmp_path, "ABC", bars, "test", "ABC.CA")
    assert result.path.exists()
    meta = json.loads((tmp_path / "ABC.meta.json").read_text())
    assert meta["last_date"] == "2026-08-26"
    assert meta["provider"] == "test"
