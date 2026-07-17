# Error Taxonomy

Stable codes: `DATA_STALE`, `CRITICAL_FIELD_MISSING`, `PROVIDER_CONFLICT`, `FUTURE_INFORMATION_REJECTED`, `UNSUPPORTED_CORPORATE_ACTION`, `DUPLICATE_CORPORATE_ACTION`, `INVALID_PRICE_BAR`, `INVALID_TIMESTAMP`, `IDENTITY_CONFLICT`, `INSUFFICIENT_HISTORY`, `DATA_BLOCKED`, `NO_SUITABLE_CANDIDATE`, `DUPLICATE_SOURCE_RECORD`, and `EVIDENCE_INTEGRITY_FAILURE`.

Task 2 adds distinct hard failures for missing/mismatched lifecycle records, category deletion evidence/overdue deletion, unknown geography, envelope agreement/policy snapshots, scorecard policy/future assessment/future evidence, pending/invalid reconciliation remediation, disallowed schemas and invalid evaluation artifacts. The enum in `domain/errors.py` is authoritative and the validation test requires every code to have an explicit severity classification.

`EVALUATION_ARTIFACT_INVALID` includes any mismatch between a supplied audit artifact and the independently recomputed hard-gate artifact, including result fields, ordered reasons, score/version, snapshots, cutoff, schema or artifact ID. Intrinsically false score chronology fails contract construction; cutoff-future assessment/evidence continues to use the existing typed scorecard reasons.

Programs branch on codes, never human text. Unknown codes require schema negotiation. Critical codes produce fail-closed research eligibility, not recommendations or portfolio actions.
