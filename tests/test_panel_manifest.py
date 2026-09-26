import unittest
from datetime import date

from egx_quant.panel import PanelRow
from egx_quant.panel_manifest import (
    freeze_development_panel_manifest,
    require_panel_matches_evidence,
    validate_frozen_development_panel_manifest,
)


class PanelManifestTests(unittest.TestCase):
    def evidence(self, **overrides):
        value = {
            "kind": "preholdout-data-evidence-manifest",
            "decision_time": "2026-01-31T23:59:59+02:00",
            "code_ref": "evidence123",
            "record_count": 2,
            "eligible_record_count": 2,
            "blocked_record_count": 0,
            "data_evidence_fingerprint": "e" * 64,
            "modeling_authorized": True,
        }
        value.update(overrides)
        return value

    def rows(self):
        return [
            PanelRow("EGX:A", date(2026, 1, 29), {"close": 10.0, "volume": 100}),
            PanelRow("EGX:B", date(2026, 1, 29), {"close": 20.0, "volume": 200}),
            PanelRow("EGX:A", date(2026, 1, 30), {"close": 10.5, "volume": 110}),
        ]

    def test_authorized_evidence_can_freeze_panel(self):
        manifest = freeze_development_panel_manifest(
            self.rows(),
            frozen_evidence_manifest=self.evidence(),
            code_ref="panel123",
            created_at="2026-09-26T00:00:00Z",
        )
        self.assertTrue(manifest["authorized_for_model_development"])
        self.assertEqual(manifest["row_count"], 3)
        self.assertEqual(manifest["security_count"], 2)
        self.assertEqual(manifest["evidence_fingerprint"], "e" * 64)
        validate_frozen_development_panel_manifest(manifest)

    def test_blocked_evidence_cannot_freeze_panel(self):
        with self.assertRaises(RuntimeError):
            freeze_development_panel_manifest(
                self.rows(),
                frozen_evidence_manifest=self.evidence(
                    eligible_record_count=1,
                    blocked_record_count=1,
                    modeling_authorized=False,
                ),
                code_ref="panel123",
            )

    def test_holdout_row_cannot_enter_development_panel(self):
        rows = self.rows() + [
            PanelRow("EGX:A", date(2026, 2, 1), {"close": 11.0})
        ]
        with self.assertRaises(RuntimeError):
            freeze_development_panel_manifest(
                rows,
                frozen_evidence_manifest=self.evidence(),
                code_ref="panel123",
            )

    def test_panel_must_match_evidence_generation(self):
        panel = freeze_development_panel_manifest(
            self.rows(),
            frozen_evidence_manifest=self.evidence(),
            code_ref="panel123",
            created_at="2026-09-26T00:00:00Z",
        )
        with self.assertRaises(RuntimeError):
            require_panel_matches_evidence(
                panel,
                self.evidence(data_evidence_fingerprint="x" * 64),
            )


if __name__ == "__main__":
    unittest.main()
