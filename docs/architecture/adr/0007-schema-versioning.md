# ADR-0007: Schema and serialization versioning

- Status: Accepted
- Date: 2026-07-11

## Decision

Every persisted contract carries semantic schema version `1.0.0`. Canonical JSON uses sorted keys, compact separators, RFC 3339 timestamps, enum codes, and Decimal strings. Breaking contract changes require a major version and migration; additive compatible fields require a minor version.

## Consequences

Hashes are stable for canonical payloads. A formal deserializer/migration registry is deferred.
