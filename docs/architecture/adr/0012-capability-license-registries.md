# ADR-0012: Capability and license registries

- Status: Accepted for Task 2
- Date: 2026-07-13
- Revised: 2026-07-17

Version typed provider capabilities and data-usage policies separately. Every capability and purpose is explicit; unknown/unverified values fail applicable gates. Approval binds exact provider, product, agreement, dates, versioned evidence, reviewer, user, purpose and typed processing geography. Empty geography rights deny processing; worldwide permission must be explicit and evidenced.

Termination is not request-supplied. An authoritative registry binds lifecycle records to provider, product, policy, agreement version, termination event and timestamp. Each governed category carries an independent immutable disposition and category-bound evidence. Missing/mismatched lifecycle state and overdue prohibited retention have distinct hard-failure reasons.

Provider-policy schema `3.1.0` retains the `3.0.0` fields and adds intrinsic chronology invariants. Capability and policy mappings are defensively copied and read-only. Scorecards bind the exact policy/agreement snapshot. Entry evidence must exist by the entry assessment, scorecard-level evidence by the scorecard assessment, entries cannot postdate the scorecard, and every assessment/evidence instant must also be at or before the evaluation cutoff. Quality scoring follows hard gates only.
