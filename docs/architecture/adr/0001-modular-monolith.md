# ADR-0001: Modular monolith

- Status: Accepted
- Date: 2026-07-11

## Decision

Use one typed Python codebase with domain/application boundaries and separately executable CLI jobs. Provider implementations depend on ports; domain code depends on neither infrastructure nor frameworks.

## Consequences

Simpler deployment, tests and transactions for one user; future extraction remains possible. Microservices are rejected until measured scaling or isolation needs justify them.
