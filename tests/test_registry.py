import unittest

from egx_quant.registry import Trial, TrialRegistry


class RegistryTests(unittest.TestCase):
    def test_registry_tracks_trials_and_rejects_duplicate_ids(self):
        registry = TrialRegistry()
        trial = Trial(
            trial_id="t-001",
            family="linear",
            params={"alpha": 0.0},
            data_fingerprint="a" * 64,
            feature_set="alpha158-egx-v1",
            target="residual_return_20d",
        )
        registry.add(trial)
        self.assertEqual(registry.count_by_family(), {"linear": 1})
        with self.assertRaises(ValueError):
            registry.add(trial)


if __name__ == "__main__":
    unittest.main()
