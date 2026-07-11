# Security, Privacy and Regulatory-Boundary Review

- Reviewer method: independent subagent run `product_and_security`; paired with product review.
- Evidence: complete specification review plus official SEBI, MeitY, CERT-In and NSE sources.
- Independence limitation: no separate security subagent and no legal opinion.

## Principal findings

- A disclaimer and private-family intent do not establish an IA/RA exemption. Exact facts require
  Indian securities counsel before personalized, external, paid or broker-connected use.
- Portfolio and suitability data create account-takeover, shared-device, backup, telemetry and AI
  exfiltration risks even for a single household.
- Immutable audit needs reconciliation with correction, retention and erasure duties.
- Provider documents are hostile input and may contain prompt-injection content.
- Personal financial data must not reach external AI without an explicit privacy architecture.

Release view: conditional pass; legal classification and personal-data architecture remain gates.
