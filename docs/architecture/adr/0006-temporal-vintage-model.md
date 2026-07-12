# ADR-0006: Temporal and vintage model

- Status: Accepted
- Date: 2026-07-11

## Decision

Persist business-effective time separately from publication, observation, ingestion, validation, usable and supersession time. Require explicit cutoffs and explicit `AS_KNOWN_THEN` or `LATEST_CORRECTED` views. `usable_from` is no earlier than all readiness gates.

## Consequences

Restatements append versions and never rewrite earlier knowledge. Historical queries reject future and late-ingested records.
