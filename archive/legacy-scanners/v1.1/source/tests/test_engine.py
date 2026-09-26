from datetime import date

from egx_scanner.config import Settings
from egx_scanner.engine import Scanner
from egx_scanner.ingestion import load_catalysts, load_portfolio, load_universe


def test_scan_respects_fresh_capital_and_no_fake_history():
    settings = Settings()
    securities = load_universe(settings.data_dir / "universe.csv")
    holdings = load_portfolio(settings.data_dir / "portfolio.csv")
    catalysts = load_catalysts(settings.data_dir / "disclosures.json")
    scanner = Scanner(settings)
    cards, histories = scanner.score(securities, holdings, catalysts, date(2026,8,28))
    recs = scanner.recommend(securities, holdings, cards, histories, 20_000)
    assert len(recs) == len(securities)
    assert sum(r.allocation_egp for r in recs) <= 17_000.01
    assert all(r.stop < r.price for r in recs)
    # Bundled V1 contains no real price CSVs, so it must not create ACTIVE buys from synthetic data.
    assert all(not c.has_real_history for c in cards)
    assert all(r.strategy.value == "CORE" for r in recs)


def test_sector_cap_is_enforced():
    settings = Settings(max_sector_pct=.35)
    securities = load_universe(settings.data_dir / "universe.csv")
    holdings = load_portfolio(settings.data_dir / "portfolio.csv")
    catalysts = load_catalysts(settings.data_dir / "disclosures.json")
    scanner = Scanner(settings)
    cards, histories = scanner.score(securities, holdings, catalysts, date(2026,8,28))
    recs = scanner.recommend(securities, holdings, cards, histories, 20_000)
    assert sum(r.allocation_egp for r in recs if r.ticker in {"QNBE","ADIB","CIEB"}) <= 20_000
