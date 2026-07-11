# Identity Model

Stable graph: `Company` (legal entity) -> one or more `Security` records -> one or more `ExchangeListing` records. Display name, exchange symbol and ISIN are separate effective-dated values. A symbol change closes one half-open history interval and opens another; it does not create a company. Delisting closes listing activity but preserves history.

**Assumption:** opaque `SYNTHETIC-*` identifiers stand in for a future stable-ID issuing service. Symbols are unique only within venue/series/time; ISINs and provider IDs are not trusted as permanent internal IDs.
