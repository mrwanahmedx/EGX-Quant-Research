import unittest
from datetime import date, timedelta

from egx_quant.liquidity_universe import (
    LiquidityObservation,
    LiquidityUniversePolicy,
    select_lagged_liquidity_universe,
)


class LiquidityUniverseTests(unittest.TestCase):
    def test_future_and_decision_day_observations_are_ignored(self):
        decision = date(2025, 2, 1)
        observations = [
            LiquidityObservation("A", decision - timedelta(days=2), 100),
            LiquidityObservation("A", decision - timedelta(days=1), 100),
            LiquidityObservation("B", decision - timedelta(days=2), 90),
            LiquidityObservation("B", decision - timedelta(days=1), 90),
            LiquidityObservation("B", decision, 1000000),
            LiquidityObservation("B", decision + timedelta(days=1), 1000000),
        ]
        policy = LiquidityUniversePolicy(
            lookback_observations=2,
            min_observations=2,
            top_n=1,
        )
        self.assertEqual(
            select_lagged_liquidity_universe(
                observations,
                decision_date=decision,
                policy=policy,
            ),
            ("A",),
        )

    def test_insufficient_history_excludes_security(self):
        decision = date(2025, 2, 1)
        observations = [
            LiquidityObservation("A", decision - timedelta(days=1), 1000),
            LiquidityObservation("B", decision - timedelta(days=2), 100),
            LiquidityObservation("B", decision - timedelta(days=1), 100),
        ]
        policy = LiquidityUniversePolicy(
            lookback_observations=2,
            min_observations=2,
            top_n=2,
        )
        self.assertEqual(
            select_lagged_liquidity_universe(
                observations,
                decision_date=decision,
                policy=policy,
            ),
            ("B",),
        )

    def test_ties_are_deterministic(self):
        decision = date(2025, 2, 1)
        observations = [
            LiquidityObservation("B", decision - timedelta(days=1), 100),
            LiquidityObservation("A", decision - timedelta(days=1), 100),
        ]
        policy = LiquidityUniversePolicy(1, 1, 2)
        self.assertEqual(
            select_lagged_liquidity_universe(
                observations,
                decision_date=decision,
                policy=policy,
            ),
            ("A", "B"),
        )


if __name__ == "__main__":
    unittest.main()
