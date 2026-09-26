import tempfile
import unittest
from pathlib import Path

from egx_quant.evidence_io import fingerprint_evidence, load_evidence_csv


HEADER = (
    "canonical_security_id,session_date,price_source,source_vintage,"
    "source_sha256,price_basis,ohlc_qa_status,quarantine_status,"
    "quarantine_reason,point_in_time_membership_status,"
    "corporate_action_status,benchmark_status,observed_at,"
    "publication_cutoff_ok,evidence_complete\n"
)


class EvidenceIOTests(unittest.TestCase):
    def test_csv_loader_and_fingerprint_are_deterministic(self):
        row = (
            "EGX:TEST,2026-01-15,fixture,v1,"
            + "a" * 64
            + ",raw,passed,clear,,passed,not_applicable,passed,"
            "2026-01-15T16:00:00Z,true,true\n"
        )
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "evidence.csv"
            path.write_text(HEADER + row, encoding="utf-8")
            records = load_evidence_csv(path)
        self.assertEqual(len(records), 1)
        self.assertEqual(
            fingerprint_evidence(records),
            fingerprint_evidence(records),
        )

    def test_csv_missing_required_columns_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "bad.csv"
            path.write_text("canonical_security_id\nEGX:TEST\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                load_evidence_csv(path)


if __name__ == "__main__":
    unittest.main()
