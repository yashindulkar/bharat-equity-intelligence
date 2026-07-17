# Reconciliation policy

**Proposal.** Normalize neither units nor identities until source semantics are retained in staging. Compare like field, security/listing, session/period, scope, currency, unit, basis, and vintage. Exact-match and numeric-tolerance rules must be field-specific and versioned. BSE reconciliation remains deferred.

**Verified — implementation commit `f03797d`, 2026-07-17.** A conflict preserves at least two distinct competing text values with unique source-record IDs, semantic basis, versioned evidence, and typed confidence. It also records field, severity, tolerance rule/version, measured difference, typed review-resolution status, explicit correction/republication requirement, separate correction/republication execution states, completion evidence/times/verifiers, and reviewer evidence/time.

- `UNRESOLVED` cannot carry completed-review evidence and must name a remediation action.
- `RESOLVED_APPROVED` proves review only. Required correction and republication remain independently `PENDING`, `COMPLETED`, or `INVALID`.
- `COMPLETED` execution requires action-specific evidence, UTC completion time and verifier. Approval of a plan is not completion.
- `INVALID_NON_REMEDIABLE` requires reviewer evidence and UTC `reviewed_at`, and cannot claim a remediation path.
- Nonrequired actions must be `NOT_REQUIRED`; required actions cannot be `NOT_REQUIRED`.

Publication behavior is policy-driven: invalid/non-remediable → `REJECTED`; unresolved critical → `QUARANTINED`; unresolved warning → `ACCEPTED_WITH_WARNINGS`; reviewed but incomplete/invalid required correction or republication → `QUARANTINED`; fully reviewed and fully remediated → `ACCEPTED_WITH_WARNINGS`; no findings → normal path. Multiple conflicts use the strictest result. No last-write-wins behavior is permitted.

Before these reconciliation transitions are considered publishable, publication independently recomputes the provider hard-gate result and requires exact equality with the supplied content-addressed audit artifact. Reconciliation status cannot compensate for an invalid or mismatched evaluation artifact.
