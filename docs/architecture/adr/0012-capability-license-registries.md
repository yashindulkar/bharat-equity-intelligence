# ADR-0012: Capability and license registries

- Status: Accepted for Task 2
- Date: 2026-07-13
- Revised: 2026-07-17

Version typed provider capabilities and data-usage policies separately. Every capability and purpose is explicit; unknown/unverified values fail applicable gates. Approval binds exact provider, product, agreement, dates, versioned evidence, reviewer, user, purpose and typed processing geography. Empty geography rights deny processing; worldwide permission must be explicit and evidenced.

Termination is not request-supplied. An authoritative registry binds lifecycle records to provider, product, policy, agreement version, termination event and timestamp. Each governed category carries an independent immutable disposition and category-bound evidence. Missing/mismatched lifecycle state and overdue prohibited retention have distinct hard-failure reasons.

The latest breaking contract revision uses provider-policy schema `3.0.0`. Capability and policy mappings are defensively copied and read-only. Scorecards bind the exact policy/agreement snapshot and enforce evidence availability at the evaluation cutoff. Quality scoring follows hard gates only.
