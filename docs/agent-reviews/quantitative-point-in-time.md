# Quantitative and Point-in-Time Methodology Review

- Reviewer method: independent subagent run `quant_and_risk`; paired with portfolio-risk review.
- Evidence: complete specification review; no market data, experiment or backtest was run.
- Independence limitation: no independent quantitative reproduction was possible because no model or
  dataset exists.

## Principal findings

- Every historical fact needs effective, publication, observation, ingestion, validation, usable and
  supersession times; period end alone is insufficient.
- Decision cutoff and earliest executable session must be explicit and India-calendar-aware.
- Add adversarial tests for restatements, late filings, future membership/actions, delistings,
  duplicate adjustment, quarterly semantics and timezone errors.
- Research must be preregistered and use purging, horizon-derived embargoes, walk-forward validation,
  dependence-aware uncertainty, costs and independent reproduction.
- Phase 1 acceptance should test correctness, lineage and abstention—not performance.

Release view: conditional pass; data coverage, benchmark, horizon and inference remain unresolved.
