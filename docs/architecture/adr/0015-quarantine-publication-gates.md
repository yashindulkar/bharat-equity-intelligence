# ADR-0015: Quarantine and publication gates

- Status: Accepted for Task 2
- Date: 2026-07-13
- Revised: 2026-07-16

Use `ACCEPTED`, `ACCEPTED_WITH_WARNINGS`, `QUARANTINED`, and `REJECTED` with structured reasons and preserved typed conflict evidence. Missing critical data quarantines; stale or unapproved data rejects. Reconciliation status is policy-driven: unresolved critical quarantines, invalid/non-remediable rejects, reviewer-approved resolved conflicts publish with warnings, and unresolved warning-severity conflicts publish with warnings. Conflict existence alone is not a quarantine rule.
