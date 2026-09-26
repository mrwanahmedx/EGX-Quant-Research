from __future__ import annotations

from datetime import date

from .config import Settings
from .domain import Action, Catalyst, Holding, Recommendation, ScoreCard, Security, Strategy
from .ingestion import load_prices
from .models import (atr, catalyst_score, data_quality_score, fundamental_scores,
                     liquidity_score, portfolio_fit, technical_score)


class Scanner:
    def __init__(self, settings: Settings):
        self.settings = settings

    def score(self, securities: list[Security], holdings: list[Holding], catalysts: list[Catalyst],
              as_of: date) -> tuple[list[ScoreCard], dict[str, list]]:
        index = {s.ticker: s for s in securities}
        cards, histories = [], {}
        for s in securities:
            bars = [b for b in load_prices(self.settings.data_dir / "prices", s.ticker) if b.date <= as_of]
            histories[s.ticker] = bars
            fundamental, valuation, why_f = fundamental_scores(s)
            daily, weekly, why_t = technical_score(bars)
            relevant = [c for c in catalysts if c.ticker == s.ticker]
            catalyst, why_c = catalyst_score(relevant, as_of)
            fit = portfolio_fit(s, holdings, index)
            liquid = liquidity_score(bars)
            quality = data_quality_score(s, bars, relevant, as_of)

            # Core tolerates missing technical history; Active does not.
            core = .38*fundamental + .25*valuation + .10*weekly + .06*daily + .08*catalyst + .09*fit + .04*liquid
            active = .08*fundamental + .05*valuation + .34*daily + .18*weekly + .17*catalyst + .08*fit + .10*liquid
            if len(bars) < 20:
                active = min(active, 49)
            reasons = (why_f + why_t + why_c)[:5]
            if quality < self.settings.min_data_quality_for_buy:
                reasons = [f"data quality {quality:.0f}/100"] + reasons
            cards.append(ScoreCard(s.ticker, fundamental, valuation, daily, weekly, catalyst, fit,
                                   liquid, core, active, quality, len(bars) >= 20, reasons))
        return cards, histories

    def recommend(self, securities: list[Security], holdings: list[Holding], cards: list[ScoreCard],
                  histories: dict[str, list], fresh_capital: float) -> list[Recommendation]:
        sec = {s.ticker: s for s in securities}
        held = {h.ticker: h for h in holdings}
        total = sum(h.market_value for h in holdings) + fresh_capital
        candidates: list[Recommendation] = []

        for card in cards:
            # ACTIVE is only eligible with real history. Otherwise use CORE.
            strategy = Strategy.ACTIVE if card.has_real_history and card.active > card.core else Strategy.CORE
            score = card.active if strategy == Strategy.ACTIVE else card.core
            exists = card.ticker in held
            quality_ok = card.data_quality >= self.settings.min_data_quality_for_buy

            if exists:
                if score >= self.settings.min_add_score and card.portfolio_fit >= 35 and quality_ok:
                    action = Action.ADD
                elif score < 40 and card.data_quality >= 45:
                    action = Action.SELL
                elif score < 50 and card.data_quality >= 45:
                    action = Action.TRIM
                else:
                    action = Action.HOLD
            else:
                action = Action.BUY if (score >= self.settings.min_buy_score and card.portfolio_fit >= 45 and quality_ok) else Action.WATCH

            bars = histories[card.ticker]
            price = bars[-1].close if bars else sec[card.ticker].price
            vol = atr(bars)
            if vol <= 0:
                vol = price * .05
            mult = 1.8 if strategy == Strategy.ACTIVE else 2.5
            stop_distance = max(vol * mult, price * (.04 if strategy == Strategy.ACTIVE else .07))
            stop = max(.01, price - stop_distance)

            current_value = held.get(card.ticker).market_value if exists else 0
            max_position_room = max(0, total * self.settings.max_position_pct - current_value)
            if strategy == Strategy.ACTIVE:
                risk_budget = total * self.settings.risk_per_trade_pct
                proposed = risk_budget / stop_distance * price
            else:
                # Core sizing should depend on conviction, not a tight trading stop.
                conviction = max(0, min(1, (score - 55) / 35))
                proposed = total * self.settings.max_position_pct * (0.35 + 0.65 * conviction)
            allocation = min(proposed, max_position_room) if action in {Action.BUY, Action.ADD} else 0

            confidence = min(.95, max(.20, .25 + (abs(score - 50) / 100) + card.data_quality / 250))
            candidates.append(Recommendation(
                card.ticker, strategy, action, round(score, 1), round(confidence, 2), price,
                max(.01, price-vol*.25), price+vol*.25, stop,
                price+stop_distance*1.5, price+stop_distance*2.5,
                allocation, int(allocation // price), card.reasons, round(card.data_quality, 1)
            ))
        return self._allocate(candidates, holdings, sec, fresh_capital)

    def _allocate(self, recs: list[Recommendation], holdings: list[Holding],
                  universe: dict[str, Security], capital: float) -> list[Recommendation]:
        deployable = capital * (1 - self.settings.reserve_pct)
        active_budget = deployable * self.settings.active_capital_pct
        core_budget = deployable - active_budget
        used = {Strategy.ACTIVE: 0.0, Strategy.CORE: 0.0}

        existing_total = sum(h.market_value for h in holdings)
        sector_values: dict[str, float] = {}
        for h in holdings:
            s = universe.get(h.ticker)
            if s:
                sector_values[s.sector] = sector_values.get(s.sector, 0) + h.market_value
        projected_total = existing_total + deployable

        buys = sorted((r for r in recs if r.action in {Action.BUY, Action.ADD}),
                      key=lambda r: (r.score, r.data_quality), reverse=True)
        for r in buys:
            bucket_cap = active_budget if r.strategy == Strategy.ACTIVE else core_budget
            remaining_bucket = bucket_cap - used[r.strategy]
            s = universe[r.ticker]
            sector_room = max(0, projected_total * self.settings.max_sector_pct - sector_values.get(s.sector, 0))
            r.allocation_egp = max(0, min(r.allocation_egp, remaining_bucket, sector_room))
            if r.allocation_egp < self.settings.minimum_order_egp:
                r.allocation_egp, r.shares = 0, 0
                if r.action == Action.BUY:
                    r.action = Action.WATCH
                    r.reasons = ["allocation blocked by reserve/sector/size rule"] + r.reasons
            else:
                r.shares = int(r.allocation_egp // r.price)
                r.allocation_egp = r.shares * r.price
                used[r.strategy] += r.allocation_egp
                sector_values[s.sector] = sector_values.get(s.sector, 0) + r.allocation_egp

        # Rotation is advisory only: never assumes an automatic sale.
        viable_buys = [r for r in buys if r.allocation_egp >= self.settings.minimum_order_egp]
        weak = sorted((r for r in recs if r.action in {Action.TRIM, Action.SELL}), key=lambda r: r.score)
        if weak and viable_buys and weak[0].score + 18 < viable_buys[0].score:
            weak[0].action = Action.ROTATE
            weak[0].rotate_to = viable_buys[0].ticker
            weak[0].reasons = [f"consider rotating capital to {viable_buys[0].ticker}"] + weak[0].reasons

        priority = {Action.BUY: 0, Action.ADD: 0, Action.ROTATE: 1, Action.TRIM: 1,
                    Action.SELL: 1, Action.HOLD: 2, Action.WATCH: 3}
        return sorted(recs, key=lambda r: (priority[r.action], -r.score))
