# ADR-0002: Phase 1 Python toolchain

- Status: Proposed
- Date: 2026-07-11

## Decision

Target Python 3.12 with a `src` layout. Phase 0 selects Ruff 0.11.0 for linting, mypy 1.15.0 in strict mode, and pytest 8.3.5, with exact Python 3.12 resolved pins in `requirements-dev.txt`. A package manager and hashed cross-platform application lock remain proposed Phase 1 decisions. Add no dataframe library until a concrete benchmarked need exists.

## Consequences

The structural checker remains standard-library-only. Tool availability is not inferred from the host: contributors and CI install the declared versions before running `make check`. Host-specific observations are recorded separately in `docs/project/ENVIRONMENT_ASSESSMENT.md`.
