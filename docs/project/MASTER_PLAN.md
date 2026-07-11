# Master Plan

## Phase 0 outcome

Establish an actionable, reviewable foundation without production behavior. Exit is **conditional**, not evidence of data rights, regulatory classification, or investment efficacy.

## Boundaries

| Boundary | Included | Excluded |
|---|---|---|
| MVP / Phase 1 | Offline CLI; bounded approved universe; security master, EOD, selected corporate actions and filings; bitemporal records; data quality; deterministic explainable score; abstention | Performance claims, personalized allocation, UI, ML, orders |
| V1 / Phases 2–4 | Bias-safe independently reproduced backtest; suitability/risk; journal; secured mobile-first private app | Autonomous or live broker orders, public/paid distribution |
| Later / Phases 5–7 | ML challenger, shadow/paper operation, separately approved read-only broker sync | Live orders unless a new legal/security/product program is authorized |

## Milestones and gates

1. **P0 governance:** documents coherent; risks/open questions assigned; ADRs proposed; checks pass; independent reviews recorded.
2. **P1 deterministic foundation:** all criteria below pass. Entry requires approved field-level data rights and PIT feasibility.
3. **P2 backtesting:** historical universe/delistings/benchmark/cost rights proven; preregistered test; independent reproduction; uncertainty disclosed.
4. **P3 suitability and portfolio:** human-approved profile and constraints; privacy/security controls; invariant tests; no orders.
5. **P4 application:** authentication, recovery, observability, backups, mobile accessibility, actionability states, manual-order workflow.
6. **P5–P7:** each needs a separate go/no-go. ML must robustly beat the baseline after costs; shadow operation precedes any broker expansion.

## Objective Phase 1 acceptance criteria

- Clean offline setup and locked dependencies reproduce on a supported machine.
- Approved license evidence maps every ingested field, retention, fixture, display, derived-work and backup use.
- Effective-dated entity/security/listing identifiers include a symbol change or delisting fixture.
- Raw payloads are immutable/content-hashed; canonical facts retain effective, published, observed, validated, usable, superseded, and ingested times.
- Historical queries reject injected future filings, membership, classifications, and corporate actions.
- Independently verified split/bonus golden cases reconcile; no adjustment can apply twice. Complex rights/demergers are deferred unless semantics are proven.
- Financial features declare units, sector applicability, formula, availability, missing-data and revision behavior and pass manual golden tests.
- Deterministic score is decomposable and versioned; it reports no probability or performance claim.
- Critical missing, stale, conflicting or invalid inputs force exclusion/abstention; a scalar completeness score cannot override a hard gate.
- Reruns are idempotent; CLI output traces to source, transformation and configuration versions.
- Contract, unit, property, leakage, integration, secret, lint, format and strict-type checks pass.
- A second reviewer reproduces critical formulas and PIT queries. No recommendation/profit/order language appears.

## Operating assumptions

Private household use; no consideration, publication, third-party access, live broker connectivity, or personal data in Phase 1. These are assumptions, not legal conclusions.

## Exact next task

Phase 1 task 1: obtain human/legal approval for one bounded provider/use case, then write and independently review the security-master/EOD/corporate-action/filing data contracts and bitemporal schemas—plus synthetic adversarial fixtures and failing acceptance tests—before implementing an adapter.
