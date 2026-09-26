# V1.2 status

**DISCONTINUED — NOT ELIGIBLE FOR DEPLOYMENT**

Recovered from the original generated V1.2 archive dated 2026-08-29.

What worked:
- added real daily EGX OHLCV ingestion through Yahoo's chart endpoint;
- provider-symbol mapping and atomic price writes;
- price freshness/history-depth checks;
- local unit tests currently pass: **5 passed**.

Why it was discontinued:
- fundamentals and catalysts still depended on manually refreshed normalized inputs;
- the package did not establish point-in-time historical validity or reproducible trading alpha;
- later scanner generations replaced it with broader coverage and stricter evidence controls.

This version is retained as research lineage only.
