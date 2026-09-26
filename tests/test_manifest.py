import unittest

from egx_quant.manifest import build_manifest, fingerprint_records


class ManifestTests(unittest.TestCase):
    def test_fingerprint_is_deterministic(self):
        rows = [{"id": "A", "close": 10.0}, {"id": "B", "close": 20.0}]
        self.assertEqual(fingerprint_records(rows), fingerprint_records(rows))
        self.assertNotEqual(
            fingerprint_records(rows),
            fingerprint_records(list(reversed(rows))),
        )

    def test_manifest_records_research_identity(self):
        fp = fingerprint_records([{"id": 1}])
        manifest = build_manifest(
            experiment_id="exp-001",
            code_ref="abc123",
            data_fingerprint=fp,
            feature_set="alpha158-egx-v1",
            target="residual_return_20d",
            split="development-fold-1",
            model="linear",
            seed=20260926,
            cost_model={"one_way_bps": 25},
            created_at="2026-09-26T00:00:00Z",
        )
        self.assertEqual(manifest["data_fingerprint"], fp)
        self.assertEqual(manifest["seed"], 20260926)


if __name__ == "__main__":
    unittest.main()
