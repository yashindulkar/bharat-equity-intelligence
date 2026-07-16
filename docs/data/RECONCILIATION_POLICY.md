# Reconciliation policy

**Proposal.** Normalize neither units nor identities until source semantics are retained in staging. Compare like field, security/listing, session/period, scope, currency, unit, basis, and vintage. Exact-match and numeric-tolerance rules must be field-specific and versioned. BSE reconciliation remains deferred.

**Verified — implementation, 2026-07-16.** A conflict preserves at least two distinct competing text values with unique source-record IDs, semantic basis, versioned evidence, and typed confidence. The conflict also records field, severity, tolerance rule/version, measured difference, typed resolution status, and an explicit correction/republication requirement.

- `UNRESOLVED` cannot carry completed-review evidence and must name a remediation action.
- `RESOLVED_APPROVED` requires reviewer evidence and UTC `reviewed_at`.
- `INVALID_NON_REMEDIABLE` requires reviewer evidence and UTC `reviewed_at`, and cannot claim a correction/republication path.

Publication behavior is policy-driven: unresolved critical → `QUARANTINED`; invalid/non-remediable → `REJECTED`; resolved approved → `ACCEPTED_WITH_WARNINGS`; unresolved warning → `ACCEPTED_WITH_WARNINGS`. No last-write-wins behavior is permitted.
