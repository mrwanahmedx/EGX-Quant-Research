# Model and Trial Registry

Every empirical model must be traceable to a trial and experiment manifest.

## Trial fields

Minimum trial identity:
- trial ID,
- model family,
- parameter set,
- data fingerprint,
- feature-set ID,
- target definition.

Trial count matters because extensive search increases selection bias.

## Model status

Allowed states:
- `candidate`
- `rejected`
- `accepted-development`
- `holdout-evaluated`
- `shadow`

A model cannot skip from `candidate` to `holdout-evaluated`.

## Evidence state

Separately record:
- `blocked`
- `partial`
- `passed`

Model status and data-evidence status are deliberately distinct. A technically good model trained on weak data is still blocked.

## Comparison discipline

Baselines and challengers should use:
- the same frozen data panel,
- the same target,
- the same folds,
- the same cost assumptions,
- the same portfolio construction rules where relevant.

A new model family does not receive a different benchmark simply because it is more complex.
