import unittest
from datetime import date, datetime, timezone

from egx_quant.evidence import (
    DataEvidenceRecord,
    QuarantineRange,
    evidence_fingerprint,
    evidence_is_model_eligible,
)
from egx_quant.evidence_manifest import (
    freeze_preholdout_evidence_manifest,
    require_frozen_manifest_authorized,
)
from egx_quant.panel import PanelRow, build_development_panel


UTC = timezone.utc


class EvidenceTests(unittest.TestCase):
    def record(self, **overrides):
        values = dict(
            canonical_security_id="EGX:A",
            session_date=date(2026, 1, 5),
            source_fingerprint="a" * 64,
            price_basis="raw",
            qa_status="pass",
            point_in_time_membership=True,
            corporate_action_status="not_applicable",
            benchmark_available=True,
            observed_at=datetime(2026, 1, 5, 15, tzinfo=UTC),
            published_at=datetime(2026, 1, 5, 15, tzinfo=UTC),
            source="fixture",
            source_vintage="v1",
        )
        values.update(overrides)
        return DataEvidenceRecord(**values)

    def test_quarantine_blocks_otherwise_clean_record(self):
        record = self.record()
        quarantine = QuarantineRange(
            quarantine_id="q-001",
            canonical_security_id="EGX:A",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 10),
            conflict_class="source_corruption",
            disposition="quarantine",
            evidence_ref="audit.csv#1",
        )
        self.assertFalse(
            evidence_is_model_eligible(
                record,
                decision_time=datetime(2026, 1, 6, tzinfo=UTC),
                quarantines=[quarantine],
            )
        )

    def test_future_publication_blocks_record(self):
        record = self.record(
            published_at=datetime(2026, 1, 7, tzinfo=UTC)
        )
        self.assertFalse(
            evidence_is_model_eligible(
                record,
                decision_time=datetime(2026, 1, 6, tzinfo=UTC),
            )
        )

    def test_evidence_fingerprint_is_order_independent(self):
        first = self.record()
        second = self.record(
            canonical_security_id="EGX:B",
            source_fingerprint="b" * 64,
        )
        self.assertEqual(
            evidence_fingerprint([first, second]),
            evidence_fingerprint([second, first]),
        )

    def test_frozen_manifest_authorizes_only_all_clean_rows(self):
        record = self.record()
        manifest = freeze_preholdout_evidence_manifest(
            [record],
            decision_time=datetime(2026, 1, 6, tzinfo=UTC),
            code_ref="abc123",
            source_snapshot_fingerprint="s" * 64,
        )
        self.assertTrue(manifest["modeling_authorized"])
        require_frozen_manifest_authorized(manifest)

        blocked = freeze_preholdout_evidence_manifest(
            [self.record(benchmark_available=False)],
            decision_time=datetime(2026, 1, 6, tzinfo=UTC),
            code_ref="abc123",
            source_snapshot_fingerprint="s" * 64,
        )
        self.assertFalse(blocked["modeling_authorized"])
        with self.assertRaises(RuntimeError):
            require_frozen_manifest_authorized(blocked)

    def test_development_panel_cannot_include_quarantined_row(self):
        row = PanelRow("EGX:A", date(2026, 1, 5), {"close": 10.0})
        quarantine = QuarantineRange(
            quarantine_id="q-001",
            canonical_security_id="EGX:A",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 10),
            conflict_class="source_corruption",
            disposition="quarantine",
            evidence_ref="audit.csv#1",
        )
        panel = build_development_panel(
            [row],
            [self.record()],
            decision_time=datetime(2026, 1, 6, tzinfo=UTC),
            quarantines=[quarantine],
        )
        self.assertEqual(panel, ())

    def test_development_panel_fails_when_evidence_missing(self):
        row = PanelRow("EGX:A", date(2026, 1, 5), {"close": 10.0})
        with self.assertRaises(RuntimeError):
            build_development_panel(
                [row],
                [],
                decision_time=datetime(2026, 1, 6, tzinfo=UTC),
            )


if __name__ == "__main__":
    unittest.main()
