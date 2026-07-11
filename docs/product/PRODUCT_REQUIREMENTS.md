# Product Requirements

## Purpose and user

A private, single-household research tool that helps a retail investor review long-term Indian-equity candidates without promising returns or placing orders. **Assumption:** household-only use; the operator and actual decision-maker are unresolved.

## Product principles

Verified source evidence over coverage; capital preservation over opportunity capture; abstention over forced output; research ranking separate from suitability and portfolio action; facts separate from model opinions; historical decisions never rewritten.

## Phase boundaries

MVP/Phase 1 is an offline deterministic CLI foundation. V1 spans validated backtesting, suitability/risk and a secured mobile-first private app. ML, paper/shadow operation and broker sync are later. Live order placement is excluded.

## Core workflow

1. Display system actionability: `ACTIONABLE`, `DEGRADED`, or `BLOCKED`, with freshness and failures.
2. Show zero or more attention items: candidate review, holding review, or operational warning. This proposed correction replaces the spec’s false mutually exclusive “exactly one” presentation.
3. For each research candidate, show verified facts, cutoff, lineage, exclusions, decomposed deterministic score, confidence inputs, risks and invalidation conditions. Unsupported valuation/allocation/range/probability fields are absent.
4. Critical missing/stale/conflicting evidence yields reason-coded abstention.
5. Later, after suitability gates, the user can approve/reject/postpone a proposal; versioned evidence is journaled; any order is manually placed outside the system.

## Functional requirements for Phase 1

- Effective-dated universe/security identity and selected corporate actions.
- Immutable raw evidence, versioned canonical facts and as-of queries.
- Quality gates, provider conflicts, traceable transformations and data cutoff.
- Sector-applicable deterministic features and decomposable scoring.
- Human and JSON CLI reports with `NO_SUITABLE_CANDIDATE` and `DATA_BLOCKED` paths.
- No personal portfolio/suitability collection, UI, notification, ML or broker behavior.

## Non-functional requirements

Offline deterministic tests; idempotent ingestion; explicit UTC/Asia-Kolkata handling; accessibility deferred but designed into V1 contracts; least data/privilege; reproducible software independent of licensed-data entitlements.

## Acceptance

The objective Phase 1 contract in `docs/project/MASTER_PLAN.md` is normative. “Attractive returns” is not an acceptance criterion.
