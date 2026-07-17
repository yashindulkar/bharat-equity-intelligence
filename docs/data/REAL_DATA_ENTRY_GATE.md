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

**Verified — implementation commit `f03797d`, 2026-07-17.** The synthetic harness binds the exact provider, product, product version, policy, agreement version and policy snapshot; approved user, purpose and typed processing geography; capability and scorecard evidence; requested EOD history interval; identity state; authoritative lifecycle registry; and provider envelope. Unknown or prohibited permission, unapproved/expired agreements, ambiguous identity, unsupported PIT/revisions/delistings, insufficient relevant history, payload-hash mismatch, disallowed schema, future scorecard evidence, or invalid snapshot binding fails closed.

For EOD history, `EvaluationRequest.latest_required_session` is the caller-supplied latest completed session. It is not wall-clock evaluation time. Intraday, weekend, and holiday-style evaluations compare coverage with that supplied cutoff. **Proposal:** production exchange-calendar resolution remains deferred; Task 2 validates but does not derive the completed-session cutoff.

History-gap intervals are closed at both endpoints. Domain, venue and time disjointness may exclude a gap. Security/universe disjointness requires effective-dated membership evidence available by the request cutoff. Unknown membership, incomplete non-membership coverage, a membership change into the affected universe, or an empty/ambiguous request scope fails closed. Current membership is never substituted for historical evidence.

## Termination and deletion lifecycle

`EvaluationRequest` cannot supply lifecycle state. An authoritative `TerminationLifecycleRegistry` is evaluated against the governing policy. At the exact termination instant, new ingestion is rejected and an exact lifecycle record becomes mandatory. Missing records produce `TERMINATION_LIFECYCLE_MISSING`; provider/product/policy/agreement/event or termination-time substitution produces `TERMINATION_LIFECYCLE_MISMATCH`. Agreement expiry is never evidence that deletion completed.

Each immutable lifecycle binds provider, product, policy ID, agreement version, lifecycle schema/version, stable lifecycle ID and termination-event ID. Raw data, backups, fixtures, derived data and audit evidence each have an independent typed disposition: contractual permission, deadline, `NOT_DUE`/`DUE`/`COMPLETED`/`OVERDUE`/`RETAINED` state, category-bound evidence, verifier and record version. `COMPLETED` requires evidence for that category. `RETAINED` is distinct from deletion and requires explicit category permission. Prohibited retention after its deadline produces `TERMINATION_DELETION_OVERDUE`.

## Geography, envelopes, scorecards and publication authorization

Approved policies require either an evidence-backed nonempty jurisdiction grant or an explicit evidence-backed `WORLDWIDE` grant. Jurisdiction identifiers are canonical uppercase strings. Empty/unknown rights deny processing; permitted/restricted overlap and worldwide-plus-restrictions fail construction.

Provider envelopes bind provider, product, product version, policy ID, agreement version, immutable policy snapshot, purpose, request/source IDs, publication/retrieval times, schema, content type, and the SHA-256 of the exact received bytes. Validation never hashes normalized or reserialized content.

Provider scorecards bind provider/product/product version and policy/agreement snapshot. Every score and weight is a finite `Decimal`; dimensions are exact and unique; weights are within 0–1 and total exactly 1. Entry evidence must be available by its entry assessment; scorecard-level evidence must be available by the scorecard assessment; entry assessments cannot follow the scorecard assessment. All evidence and assessments must also be at or before the evaluation cutoff. The proposed weighted total uses deterministic Decimal arithmetic and `ROUND_HALF_EVEN` to two decimal places. No score is calculated until all hard gates pass.

`evaluate_hard_gates()` produces a deterministic, content-addressed `EvaluationArtifact` for audit and reproduction. It binds capability, policy, lifecycle-registry/lifecycle, scorecard and request snapshots, cutoff, reasons, score and schema version. Before publication, the complete evaluator reruns from the supplied immutable inputs and its authoritative artifact is compared field-for-field with the supplied artifact. The hash proves content consistency, not that the evaluator executed. Forged result claims, removed reasons, altered scores/versions, stale inputs or changed snapshots reject with `EVALUATION_ARTIFACT_INVALID`.

The pipeline boundary remains: provider → immutable raw evidence, only where permitted → provider staging → schema validation → semantic validation → identity resolution → PIT normalization → reconciliation → data-quality/quarantine gate → canonical publication → dataset manifest. Task 2 models and tests this boundary; it does not orchestrate or ingest real data.

**Verified:** zero providers evaluated and zero providers approved.
