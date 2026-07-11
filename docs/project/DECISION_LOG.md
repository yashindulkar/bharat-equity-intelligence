# Decision Log

| ID | Status | Type | Decision / proposed correction | Rationale / confirmation needed |
|---|---|---|---|---|
| D-001 | Accepted Phase 0 | Proposal | MVP=Phase 1 offline CLI; V1=Phases 1–4; later=5–7 | Resolves §40 versus §42; human confirms before Phase 1 |
| D-002 | Accepted Phase 0 | Proposal | §42 is a V1/pre-production gate, not Phase 1 acceptance | Phase 1 cannot contain UI, portfolio and backup gates |
| D-003 | Accepted Phase 0 | Proposal | Phase 1 emits deterministic research status, not return probability, allocation or accumulation ranges | Methods and suitability do not yet exist |
| D-004 | Accepted Phase 0 | Proposal | Separate actionability state from attention items | Candidate and holding reviews may coexist; partial outages exist |
| D-005 | Accepted Phase 0 | Proposal | Critical-field gates dominate aggregate data-quality score | 95–99% completeness may omit a material fact |
| D-006 | Proposed | Architecture | Typed Python modular monolith; Parquet/DuckDB locally; PostgreSQL later; provider ports | ADR-0001/0002; benchmark before adopting workflow/UI frameworks |
| D-007 | Accepted Phase 0 | Proposal | Use bitemporal-plus-availability records; raw records immutable | Prevents restatement/look-ahead leakage and preserves lineage |
| D-008 | Deferred | Human/legal | Code license | Keep private/all-rights-reserved pending intent and counsel |
| D-009 | Deferred | Human/legal | Data providers, budget, use rights, benchmark rights | Hard Phase 1 entry gate |
| D-010 | Deferred | Human/legal | IA/RA classification, operator/investor roles, consideration/publication | Private-tool assumption is not a legal conclusion |
| D-011 | Deferred | Investor | Suitability and numerical portfolio limits | Financially consequential; Phase 3 gate |
| D-012 | Accepted Phase 0 | Scope | No live orders; read-only broker sync remains later and separately approved | Capital protection and regulatory boundary |

No entry silently amends `MASTER_SPEC.md`; proposed corrections interpret ambiguous phase/release language and require human confirmation where noted.
