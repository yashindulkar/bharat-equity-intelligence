# ADR-0002: Phase 1 Python toolchain

- Status: Accepted for Phase 1 Task 1
- Date: 2026-07-11

## Decision

Target Python 3.12 with a `src` layout. Use exact resolved pins in `requirements-dev.txt`, Ruff 0.11.0, mypy 1.15.0 and pytest 8.3.5. `uv` is preferred when available, but was not installed in the reviewed environment; adopting it and generating a hashed cross-platform lock remains a release item. Add no dataframe library until a concrete benchmarked need exists.

## Consequences

The structural checker remains standard-library-only. Tool availability is not inferred from the host: contributors and CI install the declared versions before running `make check`. Host-specific observations are recorded separately in `docs/project/ENVIRONMENT_ASSESSMENT.md`.
