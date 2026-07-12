# Contributing

1. Read `MASTER_SPEC.md`, `AGENTS.md`, the decision log, and relevant ADRs.
2. Link work to one phase acceptance criterion; keep changes small and non-overlapping.
3. Record factual sources, assumptions, failure behavior, and point-in-time semantics.
4. Add tests before financial or risk logic: unit, golden, property, leakage, and contract tests as applicable.
5. Run `make check`. Do not merge with critical security/data-quality findings, unsupported claims, or unresolved licensed-data use.

The Phase 1 development environment uses pinned `uv==0.8.3` from `requirements-dev.txt` as its
bootstrap and the committed `uv.lock` as its cross-platform dependency authority. It includes Ruff
lint, strict mypy, pytest, build, dependency-audit and test dependencies.
Use a 100-character line target, Python 3.12, explicit timezone-aware datetimes, and `Decimal`
for money. This locked environment supports the current synthetic-only foundation; it is not a
production environment or approval for real-data use.

Reviews must challenge methodology. Authors cannot be the sole validators of financial calculations, backtests, or critical security findings.
