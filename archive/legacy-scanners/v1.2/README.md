# EGX Scanner V1.2 — archived

**Status: DISCONTINUED — NOT ELIGIBLE FOR DEPLOYMENT**

This directory contains the recoverable V1.2 source snapshot from 2026-08-29.

- Source/tests are preserved under `source/`.
- The recovered test suite was rerun during archival: **5 passed**.
- V1.2 added real daily EGX OHLCV ingestion, provider-symbol mapping and freshness checks.
- User-specific `data/portfolio.csv` is intentionally excluded; its SHA-256 hash is retained.
- Fundamentals/catalysts were still manually refreshed normalized inputs, so this version did not establish point-in-time historical validity or reproducible alpha.

Retained as research lineage only.
