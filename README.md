# Bharat Long-Term Equity Intelligence

Phase 1 Task 1 provides an offline, synthetic-only foundation for stable identity, point-in-time records, selected corporate-action invariants, deterministic manifests, typed abstention and narrow provider ports. It contains no real market ingestion, recommendation, backtest, allocation, UI, ML, broker operation or profitability claim.

Run the demo with `PYTHONPATH=src python -m bharat_equity.cli --json`. All fixture names and identifiers are deliberately impossible and marked `SYNTHETIC`.

Phase 1 development uses pinned `uv==0.8.3` as the bootstrap and committed `uv.lock` as the cross-platform dependency authority:

```text
python3 -m pip install -r requirements-dev.txt
uv sync --frozen --extra dev
uv run --frozen --extra dev make check
uv run --frozen --extra dev python -m build
```

Private, research-only decision support for long-term Indian equity analysis. It is not a promise of returns, investment advice, or an order-execution system. Equity investments can lose capital; outputs may be wrong.

## Status

**Verified — 2026-07-24:** Phase 0 governance is merged; Phase 1 Task 1's synthetic-only core data-contract and point-in-time foundation has a PASS decision with documented limitations; and Phase 1 Task 2's provider-entry architecture and synthetic evaluation harness was completed and merged on 2026-07-17 as commit `a953fd4ba910906c250e94b1f419d04b55087993`. Task 2 evaluated and approved zero providers. No real-data pipeline, provider adapter, ranking, backtest, stock recommendation, portfolio allocation, UI, ML, or broker order placement exists.

**Proposal — next planned task:** Phase 1 Task 3 — Provider Selection and RFI. Task 3 has not been implemented and requires a separate architecture/planning review before implementation. Real-data operation remains blocked until an exact provider/product/agreement passes the gate. See [release checklist](docs/project/RELEASE_CHECKLIST.md), [master plan](docs/project/MASTER_PLAN.md), and [open questions](docs/project/OPEN_QUESTIONS.md).

## Intended boundaries

- **MVP / Phase 1:** offline deterministic CLI research pipeline for a small approved universe using a legally acceptable provider path, point-in-time records, quality gates, explainable scores, and abstention.
- **V1 / Phases 2–4:** independently validated backtesting, suitability/portfolio controls, then a secured mobile-first application. Broker interaction remains manual.
- **Later:** ML challenger, paper/shadow operation, and separately approved read-only broker synchronization. Live orders are outside the approved scope.

## Repository map

`docs/` contains product, architecture, data, compliance, security, research, risk, and project governance. `src/bharat_equity/` and `tests/` are intentionally minimal Phase 1 boundaries. `data/` must never contain licensed or personal data in Git.

## Development

Use Python 3.12. The current Phase 1 development environment uses pinned `uv==0.8.3` as the
bootstrap and the committed `uv.lock` as the locked dependency environment. To keep an isolated
bootstrap while preserving the existing uv-based workflow:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
PATH="$PWD/.venv/bin:$PATH" uv sync --frozen --extra dev
PATH="$PWD/.venv/bin:$PATH" uv run --frozen --extra dev make check
```

`make check` runs the repository structural/link checks, Python compilation, Ruff linting, strict
mypy typing, and pytest. Historical environment observations from Phase 0 are recorded in the
[environment assessment](docs/project/ENVIRONMENT_ASSESSMENT.md), not treated as permanent prerequisites.

## Authority and safety

Read `MASTER_SPEC.md`, then `AGENTS.md`. Material decisions belong in the decision log. See the regulatory boundary and licensing matrix before using any source.
