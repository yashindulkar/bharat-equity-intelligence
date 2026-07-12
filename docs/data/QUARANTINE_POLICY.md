# Quarantine and publication policy

- `ACCEPTED`: all critical gates pass; no unresolved reasons.
- `ACCEPTED_WITH_WARNINGS`: critical gates pass; non-critical structured warnings remain visible.
- `QUARANTINED`: potentially remediable critical missingness, conflict, identity, action, schema, semantic, or PIT problem; no canonical publication.
- `REJECTED`: policy/provider disapproval, stale data, integrity failure, prohibited use, or non-remediable invalid input; no publication.

Reasons carry stable code, detail, field and source-record IDs. Quarantine preserves evidence subject to license rights, restricts downstream access, and requires explicit revalidation. Stale data and unapproved providers cannot reach canonical publication. A score never overrides a status.
