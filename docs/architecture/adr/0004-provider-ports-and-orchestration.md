# ADR-0004: Provider ports and simple orchestration

- Status: Accepted
- Date: 2026-07-11

## Decision

Define narrow provider ports and versioned contract fixtures. Begin with plain idempotent CLI orchestration. Defer Prefect/Dagster and vendor SDK choices until retry, concurrency and operational evidence exists.

## Consequences

Provider replacement and offline tests stay feasible. Contract/licensing approval is an entry gate; convenience libraries are never authority.
