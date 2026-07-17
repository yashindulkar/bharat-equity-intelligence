# ADR-0015: Quarantine and publication gates

- Status: Accepted for Task 2
- Date: 2026-07-13
- Revised: 2026-07-17

Use `ACCEPTED`, `ACCEPTED_WITH_WARNINGS`, `QUARANTINED`, and `REJECTED` with structured reasons and preserved typed conflict evidence. Missing critical data quarantines; stale, unapproved or artifact-invalid data rejects.

Reconciliation review and remediation execution are separate. Unresolved critical conflicts quarantine; invalid/non-remediable conflicts reject; unresolved warnings publish with warnings; reviewer-approved conflicts quarantine until every required correction and republication has action-specific completion evidence; fully remediated conflicts publish with warnings. Multiple conflicts take the strictest result. Conflict existence alone is not a quarantine rule.
