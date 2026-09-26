import unittest

from egx_quant.features import lagged_return, rolling_volatility
from egx_quant.metrics import rank_ic


class FeatureMetricTests(unittest.TestCase):
    def test_lagged_return_uses_only_history_supplied(self):
        prices = [10.0, 11.0, 12.0, 13.0]
        self.assertAlmostEqual(lagged_return(prices, 2), 13 / 11 - 1)

    def test_volatility_requires_enough_history(self):
        with self.assertRaises(ValueError):
            rolling_volatility([10, 11], 2)

    def test_rank_ic_orders_monotonic_series(self):
        self.assertAlmostEqual(rank_ic([1, 2, 3], [10, 20, 30]), 1.0)
        self.assertAlmostEqual(rank_ic([1, 2, 3], [30, 20, 10]), -1.0)


if __name__ == "__main__":
    unittest.main()
