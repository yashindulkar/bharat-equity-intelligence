# Indian Data and Licensing Review

- Reviewer method: independent subagent run `data_and_architecture`; paired with architecture review.
- Evidence: complete specification review plus official NSE, NSE Indices, BSE, SEBI, RBI and MCA sources.
- Independence limitation: no legal opinion or provider contract was available.

## Principal findings

- Public exchange pages and convenience libraries do not establish rights to retain, backtest,
  display, derive from or redistribute data.
- No provider is proven to supply required PIT security history, revisions, delistings, constituent
  history, financial publication times and corporate-action semantics.
- Raw immutability may conflict with contractual caching, retention or deletion limits.
- Current constituent files must never be used retrospectively.
- Dual listings require separate entity, security and listing identities plus venue reconciliation.

Release view: conditional pass; field-level licensing and PIT feasibility block real Phase 1 ingestion.
