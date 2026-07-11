# Architecture and Developer-Experience Review

- Reviewer method: independent subagent run `data_and_architecture`; paired with data/licensing review.
- Evidence: complete specification and local environment inspection; no repository edits.
- Independence limitation: no separate architecture subagent or clean-machine reproduction.

## Principal findings

- Prefer a modular monolith with provider ports and separately executable idempotent jobs.
- Avoid simultaneous PostgreSQL, DuckDB and Parquet authorities: Phase 1 should use raw evidence,
  versioned analytical files and DuckDB; operational PostgreSQL comes later.
- Defer web, API, workflow and container dependencies until their phases.
- Use one truthful command surface for structure, compilation, lint, strict typing and tests.
- Environment-specific tool availability must not appear as a permanent project requirement.

Release view: conditional pass pending reproducible tooling and bounded Phase 1 contracts.
