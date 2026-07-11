# Repository Instructions

`MASTER_SPEC.md` is authoritative. Read it completely before material changes. Work only in the current phase and record scope corrections in `docs/project/DECISION_LOG.md`.

- Label claims as **Verified**, **Assumption**, **Proposal**, or **Open question**. Current claims need primary sources and access dates.
- Preserve point-in-time truth: publication/availability timestamps, immutable raw records, revisions, lineage, stable security IDs, delistings, and effective-dated classifications.
- Never fabricate market data, results, licensing rights, recommendations, or profitability. Missing critical evidence must cause exclusion or abstention.
- Keep research ranking separate from suitability and portfolio action. No live-order implementation.
- Do not commit secrets, licensed data, portfolio/suitability data, or generated credentials. Synthetic fixtures must be unmistakably synthetic.
- Prefer a typed Python modular monolith with domain code independent of providers/frameworks. Add dependencies only through an ADR.
- Financial logic requires golden, property, leakage, and independent-review evidence. Use UTC internally and Asia/Kolkata for investor display.
- Before handoff run available format, lint, type, test, link, and secret checks; report actual outcomes and limitations.
