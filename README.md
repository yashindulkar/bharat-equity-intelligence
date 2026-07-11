# Bharat Long-Term Equity Intelligence

Private, research-only decision support for long-term Indian equity analysis. It is not a promise of returns, investment advice, or an order-execution system. Equity investments can lose capital; outputs may be wrong.

## Status

Phase 0 governance and architecture only. No data pipeline, ranking, backtest, stock recommendation, or broker order placement exists. See [master plan](docs/project/MASTER_PLAN.md) and [open questions](docs/project/OPEN_QUESTIONS.md).

## Intended boundaries

- **MVP / Phase 1:** offline deterministic CLI research pipeline for a small approved universe using a legally acceptable provider path, point-in-time records, quality gates, explainable scores, and abstention.
- **V1 / Phases 2–4:** independently validated backtesting, suitability/portfolio controls, then a secured mobile-first application. Broker interaction remains manual.
- **Later:** ML challenger, paper/shadow operation, and separately approved read-only broker synchronization. Live orders are outside the approved scope.

## Repository map

`docs/` contains product, architecture, data, compliance, security, research, risk, and project governance. `src/bharat_equity/` and `tests/` are intentionally minimal Phase 1 boundaries. `data/` must never contain licensed or personal data in Git.

## Development

Prerequisites proposed for Phase 1: Python 3.12+, `uv`, GNU Make-compatible command runner, and Git. The current machine has Python 3.12.4 but not `uv` or Ruff. Dependency installation is intentionally deferred until ADR approval.

```sh
make check
```

This currently validates repository structure and documentation invariants without installing dependencies.

## Authority and safety

Read `MASTER_SPEC.md`, then `AGENTS.md`. Material decisions belong in the decision log. See the regulatory boundary and licensing matrix before using any source.
