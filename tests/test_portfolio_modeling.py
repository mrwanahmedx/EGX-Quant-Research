import unittest

from egx_quant.gates import DataEvidence
from egx_quant.modeling import ModelSpec, authorize_training
from egx_quant.portfolio import RankedSecurity, dropout_rebalance, one_way_turnover, top_k


class PortfolioModelingTests(unittest.TestCase):
    def setUp(self):
        self.ranked = [
            RankedSecurity("B", 0.7),
            RankedSecurity("A", 0.9),
            RankedSecurity("C", 0.5),
            RankedSecurity("D", 0.4),
        ]

    def test_top_k_is_deterministic(self):
        self.assertEqual(top_k(self.ranked, 2), ("A", "B"))

    def test_dropout_keeps_buffered_incumbent(self):
        self.assertEqual(
            dropout_rebalance(["B", "C"], self.ranked, k=2, drop_buffer=1),
            ("B", "C"),
        )

    def test_turnover_counts_new_names(self):
        self.assertAlmostEqual(one_way_turnover(["A", "B"], ["B", "C"]), 0.5)

    def test_model_training_fails_closed_without_evidence(self):
        spec = ModelSpec(
            family="linear",
            target="residual_return_20d",
            feature_set="alpha158-egx-v1",
            params={},
        )
        blocked = DataEvidence(True, True, False, False, True, False)
        with self.assertRaises(RuntimeError):
            authorize_training(spec, blocked)


if __name__ == "__main__":
    unittest.main()
