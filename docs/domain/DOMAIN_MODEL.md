# Domain Model

**Verified (2026-07-11):** Task 1 implements frozen typed contracts for Company/legal entity, Security, ExchangeListing, identifier/ISIN/symbol/classification/index histories, TradingCalendarSession, EndOfDayPriceBar, FinancialReportingPeriod, FinancialFiling, FinancialFact, CorporateAction, SourceRecord, DataProvenance, ValidationResult, DatasetManifest, AnalysisCutoff, ResearchEligibilityResult and AbstentionReason.

All persisted contracts use schema `1.0.0`; time is aware UTC; monetary, price, ratio, quantity and share values use finite `Decimal` values and serialize as strings. Required identity fields reject empty and whitespace-only strings. Raw and back-adjusted price bases are explicit; adjustment lineage, source series, method version and cutoff are attached to `AdjustedSeries`.

Cross-record validators return typed half-open interval conflicts for symbol, ISIN, classification, membership, identifier and listing histories. Rights, mergers and demergers remain typed unsupported actions and fail closed. Split/bonus support is a synthetic invariant foundation, not a production-grade total-return adjustment claim.
