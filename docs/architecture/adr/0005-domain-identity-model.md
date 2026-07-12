# ADR-0005: Stable domain identity

- Status: Accepted
- Date: 2026-07-11

## Decision

Use opaque immutable IDs and the graph legal entity (`Company`) -> `Security` -> `ExchangeListing`. Names, symbols, ISINs, provider identifiers, classifications and memberships are effective-dated attributes, never permanent keys. Intervals are UTC half-open `[effective_at, effective_until)`.

## Consequences

Ticker/name changes do not create entities; delistings remain historically queryable. Cross-record overlap/uniqueness validation remains deliberately incomplete in Task 1 and is release-blocking before real data.
