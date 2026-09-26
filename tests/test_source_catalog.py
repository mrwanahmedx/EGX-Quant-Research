import unittest

from egx_quant.sources import load_source_catalog, require_role


class SourceCatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = load_source_catalog("config/source_catalog.json")

    def test_catalog_has_unique_valid_sources(self):
        ids = [source.source_id for source in self.sources]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertGreaterEqual(len(ids), 5)

    def test_no_current_metadata_source_claims_historical_membership(self):
        hf = next(
            s for s in self.sources
            if s.source_id == "hf_kjhq_egypt_symbols"
        )
        self.assertFalse(hf.point_in_time_membership_proven)
        self.assertIn("historical_membership_source", hf.prohibited_roles)
        with self.assertRaises(RuntimeError):
            require_role(
                self.sources,
                "hf_kjhq_egypt_symbols",
                "historical_membership_source",
            )

    def test_eyad_is_raw_candidate_not_canonical_truth(self):
        eyad = require_role(
            self.sources,
            "kaggle_eyad_egx_stock_data",
            "raw_price_candidate",
        )
        self.assertIn("trusted_price_truth_without_qa", eyad.prohibited_roles)

    def test_official_egx_is_benchmark_reference(self):
        source = require_role(
            self.sources,
            "egx_official_indices",
            "benchmark_reference",
        )
        self.assertEqual(source.authority, "official_exchange")


if __name__ == "__main__":
    unittest.main()
