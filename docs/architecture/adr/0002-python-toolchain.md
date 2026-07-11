# ADR-0002: Phase 1 Python toolchain

- Status: Proposed
- Date: 2026-07-11

## Decision

Target Python 3.12 with a `src` layout; propose `uv` locking, Ruff format/lint, one strict checker (mypy versus pyright unresolved), pytest and Hypothesis. Keep core/provider/dev groups separate. Add no dataframe library until a concrete benchmarked need exists.

## Consequences

The local machine has Python 3.12.4, mypy and pytest but lacks `uv` and Ruff. Phase 0 uses a standard-library structural check; Phase 1 must install, pin and verify the selected tools before this ADR becomes Accepted.
