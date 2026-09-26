import unittest

from egx_quant.gates import (
    DataEvidence,
    evaluate_data_evidence,
    require_modeling_allowed,
)


class GateTests(unittest.TestCase):
    def test_missing_evidence_blocks_modeling(self):
        evidence = DataEvidence(
            security_master=True,
            ohlc_qa=False,
            corporate_actions=False,
            point_in_time_universe=False,
            publication_timestamps=True,
            benchmark_provenance=False,
        )
        decision = evaluate_data_evidence(evidence)
        self.assertFalse(decision.passed)
        self.assertIn("OHLC QA unresolved", decision.blockers)
        with self.assertRaises(RuntimeError):
            require_modeling_allowed(evidence)

    def test_complete_evidence_allows_next_stage(self):
        evidence = DataEvidence(True, True, True, True, True, True)
        self.assertTrue(evaluate_data_evidence(evidence).passed)


if __name__ == "__main__":
    unittest.main()
