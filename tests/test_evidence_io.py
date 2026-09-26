import tempfile
import unittest
from pathlib import Path

from egx_quant.evidence_io import fingerprint_evidence_csv, load_evidence_csv


HEADER = (
    "canonical_security_id,session_date,source_fingerprint,price_basis,"
    "qa_status,point_in_time_membership,corporate_action_status,"
    "benchmark_available,observed_at,published_at,quarantine_id,"
    "source,source_vintage\n"
)


class EvidenceIOTests(unittest.TestCase):
    def test_csv_loader_matches_canonical_evidence_contract(self):
        row = (
            "EGX:TEST,2026-01-15,"
            + "a" * 64
            + ",raw,pass,true,not_applicable,true,"
            "2026-01-15T15:00:00Z,2026-01-15T15:00:00Z,,fixture,v1\n"
        )
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "evidence.csv"
            path.write_text(HEADER + row, encoding="utf-8")
            records = load_evidence_csv(path)
            fingerprint = fingerprint_evidence_csv(path)

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].canonical_security_id, "EGX:TEST")
        self.assertEqual(records[0].qa_status, "pass")
        self.assertTrue(records[0].point_in_time_membership)
        self.assertEqual(len(fingerprint), 64)

    def test_csv_missing_required_columns_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "bad.csv"
            path.write_text("canonical_security_id\nEGX:TEST\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                load_evidence_csv(path)

    def test_invalid_boolean_fails(self):
        row = (
            "EGX:TEST,2026-01-15,"
            + "a" * 64
            + ",raw,pass,maybe,not_applicable,true,"
            "2026-01-15T15:00:00Z,2026-01-15T15:00:00Z,,fixture,v1\n"
        )
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "bad_bool.csv"
            path.write_text(HEADER + row, encoding="utf-8")
            with self.assertRaises(ValueError):
                load_evidence_csv(path)


if __name__ == "__main__":
    unittest.main()
