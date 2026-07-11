# Domain Model

**Verified (2026-07-11):** Task 1 implements frozen typed contracts for Company/legal entity, Security, ExchangeListing, identifier/ISIN/symbol/classification/index histories, TradingCalendarSession, EndOfDayPriceBar, FinancialReportingPeriod, FinancialFiling, FinancialFact, CorporateAction, SourceRecord, DataProvenance, ValidationResult, DatasetManifest, AnalysisCutoff, ResearchEligibilityResult and AbstentionReason.

All persisted contracts use schema `1.0.0`; time is aware UTC; monetary, price, ratio, quantity and share values use `Decimal` and serialize as strings. Required fields reject absence where implemented. Raw and derived bars are distinguishable; adjustment lineage is attached to `AdjustedSeries`.

**Limitation:** model-specific nonblank, finite-decimal and cross-record overlap/uniqueness validators are incomplete. Rights, mergers and demergers are typed unsupported actions and fail closed. No production-grade price adjustment is claimed.
