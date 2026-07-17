# ADR-0013: Raw-staging-canonical pipeline

- Status: Accepted as architecture; production storage deferred
- Date: 2026-07-13
- Revised: 2026-07-17

Provider → immutable raw evidence where licensed → provider staging → schema validation → semantic validation → identity resolution → PIT normalization → reconciliation → quality/quarantine → canonical publication → manifest. Task 2 implements contracts and synthetic evaluation, not orchestration or adapters.

Provider envelopes bind provider/product/version, policy, agreement version, immutable policy snapshot, purpose and schema, and are validated against the exact received payload bytes. Termination/deletion disposition is an authoritative registry gate; post-termination evidence retention does not authorize new ingestion.

Hard-gate evaluation emits a deterministic content-addressed audit artifact binding capability, policy, lifecycle, scorecard and request snapshots, cutoff, reasons and score. Publication reruns the complete hard-gate evaluator from the bound inputs, derives the authoritative result without using the supplied artifact's claims, and compares every artifact field before canonical entry. Content addressing supports integrity and reproduction; it is not authentication.
