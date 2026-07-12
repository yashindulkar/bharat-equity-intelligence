# ADR-0008: Immutable synthetic evidence and manifests

- Status: Accepted for synthetic Task 1 only
- Date: 2026-07-11

## Decision

Use standard-library content-addressed JSON files and deterministic manifests for Phase 1 Task 1. Defer Parquet/DuckDB until scale or query evidence justifies dependencies. Raw evidence is create-once; normalized versions append.

## Consequences

This does not claim tamper-proof storage or licensed retention rights. Synthetic evidence and adjusted-result records are published from fsynced temporary files with exclusive no-overwrite semantics; verified reads recompute the requested digest and reject corruption. Production durability, remote locking and licensed-data retention remain later decisions.
