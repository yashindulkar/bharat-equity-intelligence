# Data Governance

## Classification

- Public metadata is not automatically licensed for all uses.
- Vendor/exchange payloads are licensed/restricted until a contract proves otherwise.
- Portfolio and suitability data are sensitive personal financial data.
- Synthetic data must use impossible identifiers and prominent `SYNTHETIC` provenance.

## Governance controls

Every field maps to source record, publication/effective/ingestion/revision timestamps, parser/transformation versions, confidence and validation state. Raw evidence is immutable only where retention rights permit. Corrections create new versions; historical-as-known and corrected views remain distinguishable.

Criticality, freshness and provider agreement are explicit. Missing critical governance, corporate-action, identity or filing facts block output regardless of aggregate completeness. Data owners approve schemas, retention, access, backups, fixtures, derived work and deletion.

Approved provider policies require evidence-backed typed processing geography. Empty jurisdiction rights are denial, not worldwide permission; `WORLDWIDE` must be explicit. Provider envelopes and scorecards bind exact agreement versions and immutable policy snapshots.

No licensed payload, credentials, personal portfolio/suitability record, PAN/account/bank identifier, or provider token enters Git, logs, test snapshots or external AI. Unit tests use synthetic records; retained contract fixtures require written permission.

Every pipeline emits a manifest: content hashes, dataset/schema versions, cutoff, counts, rejected records, conflicts, validation results and lineage. Restore/reproduction may require current entitlement and must say so.

Task 2 publication uses `ACCEPTED`, `ACCEPTED_WITH_WARNINGS`, `QUARANTINED`, and `REJECTED`. Policy/contract gates precede raw persistence. When raw retention is forbidden but processing might otherwise be allowed, persistent raw storage is blocked; the pipeline architecture must be configured to avoid retention and prove deletion before any such product is considered.

Termination state comes from an authoritative agreement-bound registry, never an optional request field. Raw, backup, fixture, derived and audit-evidence dispositions carry independent category-bound evidence. Historical universe-gap relevance is denied unless effective-dated evidence available at the cutoff proves disjointness. Canonical publication independently recomputes the complete hard-gate result and requires exact equality with the supplied content-addressed audit artifact; the hash is not authentication.
