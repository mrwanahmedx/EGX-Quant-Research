import unittest

from egx_quant.costs import ExecutionCostModel


class CostTests(unittest.TestCase):
    def test_round_trip_cost_is_applied_twice(self):
        model = ExecutionCostModel(
            commission_bps=10,
            slippage_bps=15,
            taxes_fees_bps=5,
        )
        self.assertAlmostEqual(model.one_way_bps, 30)
        self.assertAlmostEqual(model.apply_round_trip(0.10), 0.094)

    def test_negative_cost_rejected(self):
        with self.assertRaises(ValueError):
            ExecutionCostModel(slippage_bps=-1)


if __name__ == "__main__":
    unittest.main()
