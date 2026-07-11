# Security Policy

## Supported state

The project is pre-release. No production deployment is supported.

## Reporting

Do not file public issues containing vulnerabilities, credentials, portfolio data, suitability data, or provider payloads. Contact the repository owner privately through an agreed channel; a dedicated security address remains an open question. Include impact and reproduction steps with sensitive values removed.

## Handling rules

- Never commit secrets; use environment injection or an approved secret manager.
- Treat portfolio and suitability records as sensitive personal financial data.
- Keep licensed payloads outside Git and enforce retention/redistribution terms.
- Do not send personal financial data to external AI services without an approved privacy decision.
- A critical unresolved finding blocks release.

The Phase 0 threat model is at `docs/security/THREAT_MODEL.md`.
