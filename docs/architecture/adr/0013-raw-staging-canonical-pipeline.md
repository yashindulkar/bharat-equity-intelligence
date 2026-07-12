# ADR-0013: Raw-staging-canonical pipeline

- Status: Accepted as architecture; production storage deferred
- Date: 2026-07-13

Provider → immutable raw evidence where licensed → provider staging → schema validation → semantic validation → identity resolution → PIT normalization → reconciliation → quality/quarantine → canonical publication → manifest. Task 2 implements contracts and synthetic evaluation, not orchestration or adapters.
