# System Architecture

## Status

**Proposal.** Phase 0 defines contracts and boundaries; it does not claim a deployed system.

## Style and dependency direction

A modular monolith with separately executable, idempotent batch jobs. Domain rules have no provider, database, web or model-SDK dependencies.

`domain <- application <- ports <- infrastructure/adapters <- CLI/API/jobs`

Research ranking, investor suitability and portfolio action are separate modules and records.

## Data authority by layer

1. **Raw evidence:** exact payload + content hash, append-only subject to provider retention rights.
2. **Staging:** provider semantics and parser version.
3. **Canonical:** stable entity/security/listing IDs and versioned facts.
4. **PIT analytical:** as-of records with `effective_at`, `published_at`, `observed_at`, `ingested_at`, `validated_at`, `usable_from`, `superseded_at`.
5. **Features:** versioned formulas/configuration and applicability.
6. **Research:** exclusions, scores, explanations and abstention.
7. **Portfolio/audit:** later operational state and immutable decision evidence.

Historical queries require `usable_from <= decision_cutoff`; superseded vintages remain queryable. `usable_from` is derived conservatively from publication, ingestion and validation completion. UTC is stored; exchange sessions use an approved India calendar; investor display uses Asia/Kolkata.

## Point-in-time and corporate actions

Entity, security and exchange listing are distinct. ISIN/symbol are effective-dated identifiers, not permanent identity. Corporate actions use event-specific entitlements; raw and analytical price series coexist. Adjustments are keyed/versioned to prevent duplication. Unknown or conflicting events block analysis.

## Technology proposal

Python 3.12; stdlib domain objects; Pydantic at I/O boundaries when justified; Parquet analytical snapshots and DuckDB local queries. Phase 1 development uses pinned `uv==0.8.3` as the bootstrap and committed `uv.lock` as the cross-platform dependency authority for the synthetic-only foundation. PostgreSQL, FastAPI, Next.js, workflow engines, Docker services and OpenTelemetry are deferred until their phase/use case.

## Failure behavior and explainability

Every job is idempotent, creates a quality/lineage report and fails closed on material error. Outputs carry cutoff, source references, feature/scoring/config versions and reason codes. A scalar confidence score never overrides hard exclusions. No LLM controls eligibility or scores.

The Task 2 real-data boundary evaluates immutable capability, policy, lifecycle-registry, scorecard and request snapshots. It emits a deterministic, content-addressed evaluation artifact for audit and reproduction. Before canonical publication, the complete hard-gate result is independently recomputed from those inputs and every result and snapshot field is compared with the supplied artifact. The content hash proves internal consistency, not evaluator execution or caller authenticity. Provider envelopes bind exact agreement and policy snapshots to exact received bytes.

Termination disposition is registry-owned and agreement-bound. Geography is an explicit typed grant. Historical gap exclusion requires trustworthy effective-dated non-membership evidence; ambiguity is blocking. Reconciliation review and remediation execution are distinct state machines, so pending correction/republication quarantines data.

## Security boundaries

Provider payloads and filings are hostile input. The pytest harness denies common direct Python socket connection and datagram APIs. It does not provide subprocess, native-extension, container or operating-system-level network isolation. Secrets and licensed/personal records stay outside Git. Personal records and external AI are prohibited until explicit privacy architecture approval.
