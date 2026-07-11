# ADR-0003: Evidence, analytical storage and time

- Status: Proposed
- Date: 2026-07-11

## Decision

Subject to provider rights, retain content-hashed raw evidence and versioned Parquet analytical snapshots queried with DuckDB. Defer PostgreSQL to operational application state; do not dual-write in Phase 1. Store UTC timestamps and define effective/publication/observation/ingestion/validation/usable/supersession times.

## Consequences

PIT behavior and reproduction are explicit; retention may be constrained by contracts. Append-only/hash manifests do not justify a “tamper-proof” claim. Backup, object locking and PostgreSQL need later ADRs.
