import unittest
from datetime import date, datetime, timezone

from egx_quant.evidence import (
    EvidenceRecord,
    assert_unique_evidence_grain,
    evidence_is_model_eligible,
)
from egx_quant.panel import PanelRow, build_model_panel


class EvidencePanelTests(unittest.TestCase):
    def complete_evidence(self):
        return EvidenceRecord(
            canonical_security_id="EGX:TEST",
            session_date=date(2026, 1, 15),
            price_source="fixture",
            source_vintage="fixture-v1",
            price_basis="raw",
            ohlc_qa_status="passed",
            quarantine_status="clear",
            point_in_time_membership_status="passed",
            corporate_action_status="not_applicable",
            benchmark_status="passed",
            observed_at=datetime(2026, 1, 15, 16, tzinfo=timezone.utc),
            publication_cutoff_ok=True,
            evidence_complete=True,
            source_sha256="a" * 64,
        )

    def test_complete_evidence_is_eligible(self):
        self.assertTrue(evidence_is_model_eligible(self.complete_evidence()))

    def test_quarantine_blocks_model_eligibility(self):
        good = self.complete_evidence()
        blocked = EvidenceRecord(
            **{
                **good.__dict__,
                "quarantine_status": "quarantined",
                "quarantine_reason": "source conflict",
            }
        )
        self.assertFalse(evidence_is_model_eligible(blocked))

    def test_unknown_price_basis_blocks_model_eligibility(self):
        good = self.complete_evidence()
        blocked = EvidenceRecord(**{**good.__dict__, "price_basis": "unknown"})
        self.assertFalse(evidence_is_model_eligible(blocked))

    def test_duplicate_evidence_grain_fails(self):
        record = self.complete_evidence()
        with self.assertRaises(ValueError):
            assert_unique_evidence_grain([record, record])

    def test_panel_fails_closed_when_evidence_missing(self):
        row = PanelRow("EGX:TEST", date(2026, 1, 15), 10.0)
        with self.assertRaises(RuntimeError):
            build_model_panel([row], [])

    def test_panel_builds_when_evidence_complete(self):
        row = PanelRow("EGX:TEST", date(2026, 1, 15), 10.0)
        result = build_model_panel([row], [self.complete_evidence()])
        self.assertEqual(result, (row,))


if __name__ == "__main__":
    unittest.main()
