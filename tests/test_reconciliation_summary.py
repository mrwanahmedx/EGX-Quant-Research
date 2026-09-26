import json
import unittest
from pathlib import Path


class ReconciliationSummaryTests(unittest.TestCase):
    def setUp(self):
        self.summary = json.loads(
            Path("evidence/reconciliation_summary.json").read_text(
                encoding="utf-8"
            )
        )

    def test_audit_counts_reconcile(self):
        classes = self.summary["conflict_classes"]
        self.assertEqual(
            classes["corporate_action_or_adjustment_basis"]
            + classes["source_corruption_or_non_comparable_ohlc"]
            + classes["unresolved"],
            self.summary["material_conflict_tickers_audited"],
        )
        q = self.summary["quarantine"]
        self.assertEqual(
            q["overlap_conflict_rows"] + q["invalid_row_quarantines"],
            q["execution_rows_2021_2023"],
        )

    def test_summary_cannot_masquerade_as_exact_register(self):
        self.assertFalse(self.summary["exact_quarantine_register_committed"])
        self.assertEqual(self.summary["universe"]["model_approved"], 0)


if __name__ == "__main__":
    unittest.main()
