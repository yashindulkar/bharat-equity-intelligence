# ADR-0003: Evidence, analytical storage and time

- Status: Partially Accepted
- Date: 2026-07-11

## Decision

For synthetic Task 1, retain content-hashed raw evidence as canonical JSON and defer Parquet/DuckDB until justified. Defer PostgreSQL; do not dual-write. Store UTC timestamps and define effective/publication/observation/ingestion/validation/usable/supersession times.

## Consequences

PIT behavior and reproduction are explicit; retention may be constrained by contracts. Append-only/hash manifests do not justify a “tamper-proof” claim. Backup, object locking and PostgreSQL need later ADRs.
