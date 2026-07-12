# ADR-0002: Phase 1 Python toolchain

- Status: Accepted for Phase 1 Task 1
- Date: 2026-07-11

## Decision

Target Python 3.12 with a `src` layout. Bootstrap pinned uv 0.8.3 from `requirements-dev.txt`; `uv.lock` is the dependency authority. The Phase 1 toolchain includes Ruff 0.11.0, mypy 1.15.0, pytest 9.0.3, Hypothesis 6.135.20, build 1.2.2.post1 and pip-audit 2.9.0. The build backend is pinned to setuptools 75.8.0. Add no dataframe library until a concrete benchmarked need exists.

## Consequences

The structural checker remains standard-library-only. Tool availability is not inferred from the host: contributors and CI install the declared versions before running `make check`. Host-specific observations are recorded separately in `docs/project/ENVIRONMENT_ASSESSMENT.md`.
