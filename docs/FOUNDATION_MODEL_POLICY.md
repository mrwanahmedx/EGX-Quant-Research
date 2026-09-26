# Foundation-Model Challenger Policy

Public model hubs such as Hugging Face can be useful for discovering representation-learning and time-series models. They are challengers, not shortcuts around the research protocol.

## When a foundation model is worth testing

A model is eligible for research only if:

1. its input representation can be constructed from EGX data available at the historical decision timestamp,
2. preprocessing and inference are reproducible,
3. its license permits the intended research use,
4. its weights / version are pinned,
5. the same frozen development panel is used as the transparent baselines,
6. it uses the same 20d / 63d target contract,
7. portfolio evaluation uses the same execution and cost assumptions,
8. the February-June 2026 holdout remains untouched during development.

## What it must beat

At minimum, compare against:
- simple cross-sectional momentum,
- linear baseline,
- Lasso baseline,
- tree challengers when those are validly available.

A complex pretrained model that does not beat a simple baseline after costs is not useful merely because it is more sophisticated.

## Leakage risks specific to pretrained models

Pretrained financial models can create hidden timing problems.

Before use, investigate:
- training-data cutoff where disclosed,
- whether EGX or post-freeze data may have appeared in pretraining,
- normalization fitted on future data,
- cross-asset information unavailable at the decision time,
- hidden revised fundamentals,
- benchmark leakage,
- token / feature construction using full-series statistics.

If the training corpus or cutoff is unknown, the model may still be usable as a research challenger, but the uncertainty must be documented and it cannot be presented as a clean historical causal test.

## Evaluation

Foundation-model experiments must still register:
- model identifier and exact revision,
- feature / input mapping,
- data fingerprint,
- target,
- seed where applicable,
- inference parameters,
- trial count,
- compute environment,
- cost model,
- development metrics.

They receive no special treatment in the holdout.

## Current priority

The bottleneck is still the EGX data-evidence layer, not model sophistication.

The next useful foundation-model test begins only after the real pre-holdout research panel is trustworthy enough that a model comparison means something.
