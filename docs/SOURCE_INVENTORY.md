# Public Source Inventory

Updated: 2026-09-26

This inventory separates **source discovery** from **source authorization**. A useful dataset can still be prohibited from a specific historical research role.

The machine-readable policy lives in `config/source_catalog.json`.

## 1. Egyptian Exchange official index pages

Official source:
https://beta.egx.com.eg/en/market/indices/overview?index=CASE30

Observed capabilities:
- official EGX30 description and methodology,
- official EGX70 EWI description / methodology,
- "since inception" index pages with an Excel export control,
- official disclosures and listing news linked from the exchange site.

Research role:
- preferred benchmark / methodology reference,
- preferred public reference for corporate actions and exchange notices.

Important limitation:
- the current constituent view is not automatically historical constituent evidence.
- point-in-time membership still needs dated review records or another auditable historical source.

## 2. Eyad Shaban — EGX Stock data (Kaggle)

Source:
https://www.kaggle.com/datasets/eyadshaban/egx-stock-data

Dataset card describes daily EGX stock-price data from 2000-2023 where applicable.

The dataset card also warns that the data likely still contains errors.

Research role:
- raw price candidate,
- overlap / conflict discovery.

Not authorized as:
- canonical price truth without QA,
- historical constituent membership.

The observed dataset page reports the license as unknown, so redistribution rights must be verified before copying source data into any public artifact.

## 3. Mahmoud Al-Refaey — EGX Egyptian Stocks Historical Data (Kaggle)

Source:
https://www.kaggle.com/datasets/mahmoudalrefaey/egx-egyptian-stocks-2021-2026

The dataset describes historical prices for EGX-listed companies and the dataset title identifies 2021-2026 coverage.

Research role:
- independent raw price candidate,
- overlap / source-arbitration input.

Not authorized as:
- canonical price truth before QA,
- historical membership.

License / redistribution terms should be verified from the live dataset page before any third-party rows are committed.

## 4. kjhq — Egypt Stock Symbols & Company Metadata (Hugging Face)

Source:
https://huggingface.co/datasets/kjhq/Egypt-Stock-Symbols-and-Metadata

Observed snapshot:
- 251 rows,
- fields include company name, ticker, market and sector,
- CC0-1.0 license,
- dataset card describes it as updated weekly when changes exist.

Research role:
- current security-master reconciliation candidate,
- symbol / name matching,
- current sector cross-check.

Critical limitation:
a current weekly-updated snapshot is **not** point-in-time historical membership or sector evidence. It must never be projected backward as though the values were known historically.

## 5. Yahoo market data

Source:
https://finance.yahoo.com/

Research role:
- secondary market-data candidate where EGX history exists,
- direct arbitration against conflicting source rows,
- continuity / spot checks.

Limitation:
ticker coverage and freshness are not assumed complete. Yahoo is not the sole source of canonical truth for this project.

## Source hierarchy for this project

For a disputed observation, prefer evidence in this order when applicable:

1. official EGX / issuer dated disclosure,
2. official index / listing publication,
3. independently corroborated market-data sources,
4. community datasets after overlap QA,
5. current metadata sources for mapping assistance only.

This hierarchy does not mean every official page provides every required historical field. Missing point-in-time evidence remains missing.

## Next source-research target

The highest-value unresolved source problem is **historical index / eligibility membership with dated evidence**.

Until that is solved or the research universe is redefined around a different defensible historical eligibility rule, current constituents must not be backfilled into past dates.
