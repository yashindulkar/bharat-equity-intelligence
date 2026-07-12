# Real-data entry gate

**Verified — human statement, 2026-07-13.** Operator: Yash. Investor and final investment decision-maker: Yash's mother. Use is private household research only, with no public distribution, paid service, third-party sharing, social publishing, or portfolio data in this task. Primary venue is NSE, intended initial universe is Nifty 200, frequency is EOD, and hosting is local-first on Yash's Mac. BSE reconciliation is deferred. Licensed raw data must not be sent to an external AI service unless its agreement explicitly permits that transfer.

**Open questions.** Exact viewers (beyond operator and investor), hosting country, retention duration, backup policy, cloud storage, specific AI-provider access, annual budget, provider/product, benchmark total-return product, agreement evidence, and reviewer approval are not confirmed.

## Human-confirmation checklist

| Decision | Evidence/status |
|---|---|
| Operator | **Verified:** Yash; human statement 2026-07-13 |
| Investor/final decision-maker | **Verified:** Yash's mother; human statement 2026-07-13 |
| Viewers | **Open question:** operator and investor are named, but the exclusive viewer list is not explicit |
| Household-only use | **Verified:** human statement 2026-07-13 |
| Public/paid distribution prohibited | **Verified:** includes third-party sharing and social publishing |
| Hosting country | **Open question:** local Mac does not establish country/location |
| Retention period | **Open question** |
| Backup policy | **Open question** |
| Cloud storage | **Open question** |
| AI-provider access | **Verified constraint:** default denied for licensed raw data; **Open question:** any agreement-specific exception |
| Data budget | **Open question:** decide through RFI/scorecards |

## Executable gate

The `ProviderCapabilityRegistry` and `DataUsagePolicy` must both be complete and approved for the exact provider product, agreement version, user, purpose, geography, date, storage behavior, and intended processing. `UNKNOWN`, missing evidence, expiration, prohibited purpose, unavailable PIT/history/delistings, ambiguous identity, forbidden required raw retention, or unknown revision behavior fails. Scores cannot override failures. A passing provider is architecture-eligible only; records must still pass schema, semantic, identity, PIT, reconciliation, freshness, and publication gates.

The pipeline boundary is: provider → immutable raw evidence (only when permitted) → provider staging → schema validation → semantic validation → identity resolution → PIT normalization → reconciliation → data-quality/quarantine gate → canonical publication → dataset manifest. Task 2 models this boundary; it does not orchestrate or ingest real data.
