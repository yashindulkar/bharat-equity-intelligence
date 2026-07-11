# ADR-0009: Synthetic fixture policy

- Status: Accepted
- Date: 2026-07-11

## Decision

Committed fixtures use impossible `SYNTHETIC-*` namespaces, impossible company names/currencies/jurisdictions, fixed IDs and prominent non-investment provenance. No realistic ISIN, exchange code, vendor payload or random ID is allowed.

## Consequences

Tests remain offline and licensing-independent. Repository scanning is a guard, not proof that future fixtures are synthetic.
