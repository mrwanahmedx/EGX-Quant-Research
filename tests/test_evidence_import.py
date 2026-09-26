import csv
import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from egx_quant.evidence_import import (
    import_exact_quarantine_register,
    import_preholdout_security_master,
    validate_exact_quarantine_register,
    validate_preholdout_security_master,
)


class EvidenceImportTests(unittest.TestCase):
    def write_quarantine(self, path, rows):
        fields = [
            "quarantine_id",
            "canonical_security_id",
            "source_symbol",
            "start_date",
            "end_date",
            "conflict_class",
            "disposition",
            "accepted_source",
            "source_vintage",
            "evidence_ref",
        ]
        with Path(path).open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)

    def quarantine_row(self, **overrides):
        row = {
            "quarantine_id": "q-001",
            "canonical_security_id": "EGX:A",
            "source_symbol": "A",
            "start_date": "2025-01-01",
            "end_date": "2025-01-31",
            "conflict_class": "source_corruption",
            "disposition": "quarantine",
            "accepted_source": "",
            "source_vintage": "v1",
            "evidence_ref": "audit.csv#1",
        }
        row.update(overrides)
        return row

    def security_row(self, **overrides):
        row = {
            "canonical_security_id": "EGX:A",
            "symbol": "A",
            "effective_from": "2025-01-01",
            "effective_to": None,
            "published_at": "2025-01-01T08:00:00+02:00",
            "source": "dated-review",
            "mapping_confidence": "verified",
            "sector": "Banks",
            "sector_effective_from": "2025-01-01",
            "sector_published_at": "2025-01-01T08:00:00+02:00",
        }
        row.update(overrides)
        return row

    def test_exact_quarantine_count_is_enforced(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "q.csv"
            self.write_quarantine(path, [self.quarantine_row()])
            with self.assertRaises(ValueError):
                validate_exact_quarantine_register(path, expected_count=47)

    def test_holdout_quarantine_range_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "q.csv"
            self.write_quarantine(
                path,
                [self.quarantine_row(end_date="2026-02-02")],
            )
            with self.assertRaises(ValueError):
                validate_exact_quarantine_register(path, expected_count=1)

    def test_quarantine_import_revalidates_destination(self):
        with tempfile.TemporaryDirectory() as d:
            source = Path(d) / "source.csv"
            destination = Path(d) / "evidence" / "q.csv"
            self.write_quarantine(source, [self.quarantine_row()])
            rows = import_exact_quarantine_register(
                source,
                destination,
                expected_count=1,
            )
            self.assertEqual(len(rows), 1)
            self.assertTrue(destination.exists())

    def test_future_security_master_publication_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "master.json"
            path.write_text(
                json.dumps([
                    self.security_row(
                        published_at="2026-02-01T00:00:00+02:00"
                    )
                ]),
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                validate_preholdout_security_master(
                    path,
                    decision_time=datetime.fromisoformat(
                        "2026-01-31T23:59:59+02:00"
                    ),
                )

    def test_security_master_import_is_canonicalized(self):
        with tempfile.TemporaryDirectory() as d:
            source = Path(d) / "source.json"
            destination = Path(d) / "evidence" / "security_master.json"
            source.write_text(
                json.dumps([self.security_row()]),
                encoding="utf-8",
            )
            rows = import_preholdout_security_master(
                source,
                destination,
                decision_time=datetime.fromisoformat(
                    "2026-01-31T23:59:59+02:00"
                ),
            )
            self.assertEqual(len(rows), 1)
            self.assertTrue(destination.exists())


if __name__ == "__main__":
    unittest.main()
