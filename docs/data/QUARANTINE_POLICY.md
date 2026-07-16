# Quarantine and publication policy

**Verified — implementation, 2026-07-16.**

- `ACCEPTED`: provider and record gates pass with no findings.
- `ACCEPTED_WITH_WARNINGS`: gates pass and findings are non-blocking. This includes a reviewer-approved resolved reconciliation conflict, or an unresolved warning-severity conflict, with complete competing evidence preserved.
- `QUARANTINED`: a remediable critical problem blocks canonical publication. An unresolved critical reconciliation conflict is quarantined.
- `REJECTED`: policy/provider failure, stale data, integrity failure, prohibited use, or an invalid/non-remediable reconciliation conflict prevents publication.

The mere presence of a reconciliation conflict is not a quarantine condition. Conflict severity and typed resolution status drive the transition. Publication decisions preserve the complete typed conflict objects plus structured reason codes; no source value is discarded. A score never overrides a gate or publication status.
