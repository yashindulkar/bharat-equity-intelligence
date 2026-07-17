# Data Licensing Matrix

## Approval template

| Dataset | Contract/version | Internal research | Backtest | Raw retention/backup | Derived features/model | Household display | Redistribution | Test fixtures | Status/owner |
|---|---|---|---|---|---|---|---|---|---|
| NSE market/corporate | Not selected | ? | ? | ? | ? | ? | No unless agreed | ? | Blocked / owner+counsel |
| NSE index/benchmark | Not selected | ? | ? | ? | ? | ? | No unless agreed | ? | Blocked / owner+counsel |
| BSE market/corporate | Not selected | ? | ? | ? | ? | ? | ? | ? | Blocked / owner+counsel |
| RBI series | Per-series review | ? | ? | ? | ? | ? | ? | ? | Unresolved / data lead |
| Synthetic fixtures | Project-authored | Yes | Tests only | Yes | Tests only | Watermarked | Yes with code license | Yes | Proposed |

Primary evidence and access dates are in `docs/data/DATA_SOURCE_MATRIX.md`. A tariff or public download is not a license grant. “Official” describes provenance, not accuracy, economic correctness, PIT completeness or reuse rights.

Phase 1 cannot ingest real data until every used row has approval evidence for the exact use. News, forecasts, governance narratives and benchmark branding are excluded from MVP unless separately approved.

Task 2 adds the executable `DataUsagePolicy` registry. **Verified human scope (2026-07-13):** private household research, no public/paid/third-party/social distribution, and no external-AI transfer of licensed raw data absent explicit provider permission. This does not resolve any `?` above; no provider is approved.
