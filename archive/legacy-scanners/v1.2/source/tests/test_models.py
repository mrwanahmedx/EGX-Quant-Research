from datetime import date, timedelta

from egx_scanner.domain import Bar
from egx_scanner.models import atr, rsi, technical_score


def bars(n=70):
    return [Bar(date(2026,1,1)+timedelta(days=i), 99+i, 101+i, 98+i, 100+i, 1000+i*10) for i in range(n)]


def test_indicators_on_uptrend():
    sample = bars()
    assert rsi([b.close for b in sample]) == 100
    assert atr(sample) > 0
    daily, weekly, reasons = technical_score(sample)
    assert daily > 60
    assert weekly > 50
    assert reasons
