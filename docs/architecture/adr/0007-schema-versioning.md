# ADR-0007: Schema and serialization versioning

- Status: Accepted
- Date: 2026-07-11
- Revised: 2026-07-17

## Decision

Every persisted contract carries semantic schema version `1.0.0`. Canonical JSON uses sorted keys, compact separators, RFC 3339 timestamps, enum codes, and Decimal strings. Breaking contract changes require a major version and migration; additive compatible fields require a minor version.

Task 2 provider-policy contracts are now `3.0.0`, deterministic evaluation reports are `2.0.0`, and evaluation artifacts begin at `1.0.0`. This major provider-policy revision reflects agreement-bound lifecycle, geography, envelope, remediation and scorecard contracts rather than silently reinterpreting `2.0.0` records.

## Consequences

Hashes are stable for canonical payloads. A formal deserializer/migration registry is deferred.
