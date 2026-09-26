import json
import tempfile
import unittest
from pathlib import Path

from egx_quant.io import (
    load_evidence_json,
    load_quarantine_csv,
    load_security_master_json,
)


class IOTests(unittest.TestCase):
    def test_load_quarantine_register(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "q.csv"
            path.write_text(
                "quarantine_id,canonical_security_id,start_date,end_date,"
                "conflict_class,disposition,evidence_ref\n"
                "q1,EGX:A,2025-01-01,2025-01-02,source_corruption,"
                "quarantine,audit.csv#1\n",
                encoding="utf-8",
            )
            rows = load_quarantine_csv(path)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0].canonical_security_id, "EGX:A")

    def test_quarantine_register_requires_columns(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "q.csv"
            path.write_text("quarantine_id\nq1\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                load_quarantine_csv(path)

    def test_load_evidence_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "e.json"
            path.write_text(
                json.dumps(
                    [
                        {
                            "canonical_security_id": "EGX:A",
                            "session_date": "2025-01-02",
                            "source_fingerprint": "a" * 64,
                            "price_basis": "raw",
                            "qa_status": "pass",
                            "point_in_time_membership": True,
                            "corporate_action_status": "not_applicable",
                            "benchmark_available": True,
                            "observed_at": "2025-01-02T15:00:00+02:00",
                            "published_at": None,
                        }
                    ]
                ),
                encoding="utf-8",
            )
            rows = load_evidence_json(path)
            self.assertEqual(rows[0].canonical_security_id, "EGX:A")

    def test_load_security_master_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "s.json"
            path.write_text(
                json.dumps(
                    [
                        {
                            "canonical_security_id": "EGX:A",
                            "symbol": "AAA",
                            "effective_from": "2024-01-01",
                            "effective_to": None,
                            "published_at": "2024-01-01T00:00:00+02:00",
                            "source": "fixture",
                            "mapping_confidence": "verified",
                            "sector": None,
                            "sector_effective_from": None,
                            "sector_published_at": None,
                        }
                    ]
                ),
                encoding="utf-8",
            )
            rows = load_security_master_json(path)
            self.assertEqual(rows[0].symbol, "AAA")


if __name__ == "__main__":
    unittest.main()
