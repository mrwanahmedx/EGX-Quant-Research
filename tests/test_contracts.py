import unittest
from datetime import date, datetime, timezone

from egx_quant.contracts import Bar, ContractError, assert_unique, validate_bar


class ContractTests(unittest.TestCase):
    def valid_bar(self):
        return Bar(
            canonical_security_id="EGX:TEST",
            trading_date=date(2026, 1, 5),
            open=10.0,
            high=11.0,
            low=9.5,
            close=10.5,
            volume=1000.0,
            source="fixture",
            observed_at=datetime(2026, 1, 5, 16, tzinfo=timezone.utc),
        )

    def test_valid_bar_passes(self):
        validate_bar(self.valid_bar())

    def test_impossible_ohlc_fails(self):
        bar = self.valid_bar()
        broken = Bar(**{**bar.__dict__, "high": 9.0})
        with self.assertRaises(ContractError):
            validate_bar(broken)

    def test_duplicate_grain_fails(self):
        rows = [
            {"security_id": "A", "date": "2026-01-01", "source": "x"},
            {"security_id": "A", "date": "2026-01-01", "source": "x"},
        ]
        with self.assertRaises(ContractError):
            assert_unique(rows, ["security_id", "date", "source"])


if __name__ == "__main__":
    unittest.main()
