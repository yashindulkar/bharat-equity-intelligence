# ADR-0013: Raw-staging-canonical pipeline

- Status: Accepted as architecture; production storage deferred
- Date: 2026-07-13
- Revised: 2026-07-16

Provider → immutable raw evidence where licensed → provider staging → schema validation → semantic validation → identity resolution → PIT normalization → reconciliation → quality/quarantine → canonical publication → manifest. Task 2 implements contracts and synthetic evaluation, not orchestration or adapters.

Provider envelopes bind provider/product/version/policy/purpose/schema and are validated against actual payload bytes. Termination/deletion disposition is a separate lifecycle gate; post-termination evidence retention does not authorize new ingestion.
