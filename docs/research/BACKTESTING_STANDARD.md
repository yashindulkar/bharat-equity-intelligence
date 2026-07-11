# Backtesting Standard

Backtests are simulations, not evidence of guaranteed or future profitability. Phase 1 builds correctness foundations; performance simulation begins in Phase 2 only after data rights and coverage gates pass.

## Pre-registration

Record hypothesis, universe construction, primary horizon/metric, benchmark, cutoff and execution clock, rebalance rule, costs, exclusions, missing outcomes, sample period, holdout, failure criterion and allowed sensitivities before viewing results. Register every trial to expose multiple testing.

## Point-in-time contract

Queries use effective-dated identities/universe and only records with `usable_from <= decision_cutoff`. Preserve originals, restatements and corrections. Include delisted/suspended securities and outcomes; otherwise constrain the claim or fail the study. Current constituents/classifications must never be backfilled.

Use Asia/Kolkata exchange sessions, UTC storage, an after-close decision cutoff and earliest next-session conservative execution. Never fill at the close that generated the signal without evidence. Model costs with effective dates and instrument applicability.

## Required adversarial tests

Future/restated filings; late/after-hours publication; future membership/classification/action; delisting; symbol change; duplicate adjustment; cumulative versus discrete quarter; consolidated versus standalone statement; timezone boundary; provider revision/conflict; cost monotonicity and rerun idempotency.

## Validation and reporting

Use expanding walk-forward splits, purge overlapping label intervals, derive embargo from maximum label horizon and keep an untouched holdout. Never random-shuffle primary time-series validation. Report gross/net performance, turnover, drawdowns, liquidity, delistings, benchmark, attribution, negative periods and dependence-aware uncertainty/effective sample size. Test costs, delays, universes, benchmarks, thresholds, dates, sector neutrality, feature ablation and removal of best years/securities.

The strategy author is not the sole validator. Reproduction uses code commit, lockfile, dataset/universe/feature/config versions, cutoff, seed, costs, benchmark and artifact hashes.
