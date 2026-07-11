# Contributing

1. Read `MASTER_SPEC.md`, `AGENTS.md`, the decision log, and relevant ADRs.
2. Link work to one phase acceptance criterion; keep changes small and non-overlapping.
3. Record factual sources, assumptions, failure behavior, and point-in-time semantics.
4. Add tests before financial or risk logic: unit, golden, property, leakage, and contract tests as applicable.
5. Run `make check`. Do not merge with critical security/data-quality findings, unsupported claims, or unresolved licensed-data use.

Formatting/linting/type proposal for Phase 1: Ruff format + lint, mypy strict, pytest, 100-character line target, Python 3.12, explicit timezone-aware datetimes, `Decimal` for money. These conventions become binding only after ADR-0002 is accepted and the lockfile exists.

Reviews must challenge methodology. Authors cannot be the sole validators of financial calculations, backtests, or critical security findings.
