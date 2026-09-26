import unittest
from datetime import date

from egx_quant.source_snapshot import (
    SourceSnapshot,
    composite_source_fingerprint,
    freeze_source_snapshot_manifest,
    validate_frozen_source_snapshot_manifest,
)
from egx_quant.sources import SourceDefinition


class SourceSnapshotTests(unittest.TestCase):
    def source(self):
        return SourceDefinition(
            source_id="fixture_source",
            name="Fixture Source",
            source_url="https://example.com",
            authority="fixture",
            license_status="fixture-license",
            coverage_claim="fixture",
            approved_roles=("raw_price_candidate",),
            prohibited_roles=(),
            point_in_time_membership_proven=False,
        )

    def snapshot(self, **overrides):
        values = dict(
            source_id="fixture_source",
            source_version="v1",
            source_sha256="a" * 64,
            row_count=100,
            min_session=date(2025, 1, 1),
            max_session=date(2026, 1, 30),
            license_status="fixture-license",
            local_only=True,
            notes="fixture",
        )
        values.update(overrides)
        return SourceSnapshot(**values)

    def test_source_snapshot_fingerprint_is_deterministic(self):
        item = self.snapshot()
        self.assertEqual(
            composite_source_fingerprint([item]),
            composite_source_fingerprint([item]),
        )

    def test_snapshot_crossing_development_cutoff_fails(self):
        with self.assertRaises(ValueError):
            self.snapshot(max_session=date(2026, 2, 1))

    def test_license_status_must_match_source_catalog(self):
        with self.assertRaises(ValueError):
            freeze_source_snapshot_manifest(
                [self.snapshot(license_status="wrong")],
                source_catalog=[self.source()],
            )

    def test_frozen_manifest_round_trip_validates(self):
        manifest = freeze_source_snapshot_manifest(
            [self.snapshot()],
            source_catalog=[self.source()],
            created_at="2026-09-26T00:00:00Z",
        )
        validate_frozen_source_snapshot_manifest(
            manifest,
            source_catalog=[self.source()],
        )
        self.assertTrue(manifest["authorized_for_development"])

    def test_fingerprint_tampering_is_detected(self):
        manifest = freeze_source_snapshot_manifest(
            [self.snapshot()],
            source_catalog=[self.source()],
            created_at="2026-09-26T00:00:00Z",
        )
        manifest["composite_fingerprint"] = "b" * 64
        with self.assertRaises(ValueError):
            validate_frozen_source_snapshot_manifest(
                manifest,
                source_catalog=[self.source()],
            )


if __name__ == "__main__":
    unittest.main()
