# ADR-0012: Capability and license registries

- Status: Accepted for Task 2
- Date: 2026-07-13
- Revised: 2026-07-16

Version typed provider capabilities and data-usage policies separately. Every capability and purpose is explicit; unknown/unverified values fail applicable gates. Approval binds exact provider, product, agreement, dates, versioned evidence, reviewer, user and purpose.

The Task 2 remediation is a breaking provider-policy contract change and therefore uses semantic schema version `2.0.0`. It replaces string history gaps with domain/interval/venue/scope/severity/evidence/resolution records; adds separate post-termination permissions and typed deletion lifecycle state; and replaces raw score dictionaries with an evidence-bound, versioned scorecard. EOD coverage compares with the caller's explicit latest required completed session, not evaluation wall-clock time. Quality scoring follows hard gates only.
