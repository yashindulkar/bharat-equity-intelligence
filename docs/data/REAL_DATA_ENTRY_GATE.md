# Real-data entry gate

**Verified — human statement, 2026-07-13.** Operator: Yash. Investor and final investment decision-maker: Yash's mother. Use is private household research only, with no public distribution, paid service, third-party sharing, social publishing, or portfolio data in this task. Primary venue is NSE, intended initial universe is Nifty 200, frequency is EOD, and hosting is local-first on Yash's Mac. BSE reconciliation is deferred. Licensed raw data must not be sent to an external AI service unless its agreement explicitly permits that transfer.

**Open questions.** Exact viewers, hosting country, retention duration, backup/cloud policy, named AI-provider permission, annual budget, provider/product, benchmark total-return product, agreement evidence, and qualified legal/licensing approval remain unconfirmed.

## Human-confirmation checklist

| Decision | Evidence/status |
|---|---|
| Operator | **Verified:** Yash; human statement 2026-07-13 |
| Investor/final decision-maker | **Verified:** Yash's mother; human statement 2026-07-13 |
| Viewers | **Open question:** operator and investor are named, but the exclusive viewer list is not explicit |
| Household-only use | **Verified:** human statement 2026-07-13 |
| Public/paid distribution prohibited | **Verified:** includes third-party sharing and social publishing |
| Hosting country | **Open question:** local Mac does not establish country/location |
| Retention period | **Open question** |
| Backup policy | **Open question** |
| Cloud storage | **Open question** |
| AI-provider access | **Verified constraint:** default denied for licensed raw data; **Open question:** any agreement-specific exception |
| Data budget | **Open question:** decide through RFI and scorecards |

## Executable entry conditions

**Verified — implementation, 2026-07-16.** The synthetic harness binds the exact provider, product, product version, policy, agreement interval, user, purpose, geography, capability evidence, scorecard evidence, requested EOD history interval, identity status, retention behavior, and provider envelope. Unknown or prohibited permission, unapproved/expired agreements, ambiguous identity, unsupported PIT/revisions/delistings, insufficient relevant history, payload-hash mismatch, or disallowed schema fails closed.

For EOD history, `EvaluationRequest.latest_required_session` is the caller-supplied latest completed session required by the use case. It is not the wall-clock evaluation time. Intraday, weekend, and holiday evaluations therefore compare coverage with the supplied completed session. **Proposal:** production exchange-calendar resolution remains deferred to a later provider/calendar adapter; Task 2 trusts but validates the explicit UTC cutoff supplied by the caller.

History gaps are typed by data domain, UTC interval, venue, affected securities/universe, severity, evidence, and resolution. Only an open, critical gap intersecting the requested domain, venue, scope, and history interval blocks entry.

## Termination and deletion lifecycle

**Verified — implementation, 2026-07-16.** A termination record carries termination time, deletion deadline, raw/backup/fixture/derived/audit-evidence states (`NOT_DUE`, `DUE`, `COMPLETED`, `OVERDUE`), derived/audit retention permissions, and deletion-verification evidence. New entry after termination always fails. After the contract-specific deadline, any prohibited retained category not verified `COMPLETED` adds a deletion-overdue hard failure. Contract-permitted derived data or audit-hash evidence may remain without an overdue finding, but does not authorize new retrieval.

## Envelope and scorecard

The provider envelope separately binds provider, product, product version, policy ID, purpose, request/source IDs, publication/retrieval times, schema, content type, and SHA-256. Validation recomputes SHA-256 from actual payload bytes and checks allowed schemas and agreement dates.

The provider scorecard is typed and versioned. Every proposed dimension contains a finite 0–100 score, exact weight, evidence, assessor, UTC assessment time, method version, explanation, and confidence. Exact dimensions and weights summing to 1 are construction invariants. A weighted score is produced only after every hard gate passes.

The pipeline boundary remains: provider → immutable raw evidence, only where permitted → provider staging → schema validation → semantic validation → identity resolution → PIT normalization → reconciliation → data-quality/quarantine gate → canonical publication → dataset manifest. Task 2 models and tests this boundary; it does not orchestrate or ingest real data.

**Verified:** zero providers evaluated and zero providers approved.
