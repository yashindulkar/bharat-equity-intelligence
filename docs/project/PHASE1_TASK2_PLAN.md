# Phase 1 Task 2 plan

## Scope and acceptance

Define the real-data entry architecture, contracts, policies, synthetic evaluation harness, and offline tests. Exclude adapters, scraping, real-universe ingestion, factor/ranking/backtest/recommendation/UI/ML/portfolio/notifications/brokers.

1. Reconcile human statements with Task 1 and accepted ADRs.
2. Define field, capability, usage, envelope, pipeline, precedence, reconciliation and quarantine contracts.
3. Execute synthetic-only fail-closed gates and deterministic reports.
4. Obtain five independent read-only specialist reviews; remediate critical findings.
5. Run format, lint, strict type, tests, build/install smoke, dependency audit, links/structure and secret scan.
6. Release only the architecture/harness, never a provider or dataset approval.

## Evidence and release boundary

Success requires all requested gate tests, denial of common direct Python socket connection/datagram APIs, deterministic output, review records, clean checks, and a draft unmerged PR. This does not provide subprocess, native-extension, container or operating-system-level network isolation. Human/provider decisions remain visibly open. No score exists after a hard-gate failure.

**Verified — historical context:** the preceding draft/unmerged condition records the pre-merge release state and is intentionally preserved. PR #4 subsequently merged on 2026-07-17 as commit `a953fd4ba910906c250e94b1f419d04b55087993`.

## Final architecture-review remediation

**Verified — implementation commit `f03797d`, 2026-07-17.** The final pass adds authoritative agreement-bound lifecycle state, category-specific deletion evidence, typed processing geography, envelope policy snapshots, remediation execution gates, PIT-bound scorecards, ambiguity-denying historical-gap relevance, and content-addressed publication authorization. It expands deterministic unit/adversarial and Hypothesis tests without adding an adapter or any later-phase behavior.

## Latest two-finding remediation

**Verified — implementation commit `e767ee3`, 2026-07-17.** Publication no longer treats artifact construction or a content hash as proof that the evaluator executed. It independently recomputes the full hard-gate result from the bound inputs and compares all artifact fields. Provider-policy schema `3.1.0` also rejects evidence that postdates the assessment it claims to support. Scope remains synthetic provider-entry architecture only.

## Post-merge closeout

**Verified — 2026-07-24:** Task 2 is completed and merged. Its final release decision is PASS only for the provider-entry architecture and synthetic evaluation harness. Zero providers, products or agreements were evaluated or approved; no provider adapter or real market data was introduced; and real-data operation remains blocked.

**Proposal — next planned task:** Phase 1 Task 3 — Provider Selection and RFI. Provider selection and RFI evidence work belong to that separately approved task. Task 3 has not been implemented and requires a separate architecture/planning review before implementation.
