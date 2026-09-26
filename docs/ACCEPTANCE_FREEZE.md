# Acceptance Threshold Freeze

Acceptance criteria are part of the holdout contract.

They must be chosen from development reasoning **before** February-June 2026 holdout results are inspected.

## Why a template is currently committed

`config/acceptance.template.json` contains null thresholds on purpose.

That keeps the repository fail-closed while:
- the real development panel is unavailable,
- benchmark series are not approved,
- no real development metrics have been produced.

Choosing numeric gates now would create false precision.

## Freeze workflow

Once the real development panel exists and development-only evidence supports defensible thresholds, prepare a candidate JSON with all fields populated and run:

```bash
python scripts/freeze_acceptance_thresholds.py \
  --candidate /path/to/development_thresholds.json \
  --code-ref COMMIT_SHA \
  --development-evidence-ref DEVELOPMENT_EXPERIMENT_OR_PANEL_REF \
  --rationale "Explain why these thresholds were selected from development evidence before holdout." \
  --output config/acceptance.frozen.json
```

The freeze tool requires:
- complete numeric thresholds,
- valid probability / turnover / drawdown ranges,
- a named multiple-testing method,
- a development-evidence reference,
- a substantive rationale,
- an explicit unopened-holdout state.

## Current state

Do not commit a frozen threshold file merely to turn a readiness check green.

The correct state remains `template_not_frozen` until real development evidence exists.
