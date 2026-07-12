# ADR-0010: Validation and error taxonomy

- Status: Accepted
- Date: 2026-07-11

## Decision

Use stable `ReasonCode` values and `DomainError`; human detail is supplemental. Critical identity, staleness, provider conflict and unsupported-action failures dominate completeness and force `DATA_BLOCKED`.

## Consequences

Callers do not branch on message text. Some infrastructure integrity failures still require conversion from generic exceptions before release.
