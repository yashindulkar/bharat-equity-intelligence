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
| D-013 | Accepted Phase 1 | Scope | Task 1 uses impossible synthetic data and provider ports only | Real ingestion remains blocked by D-009; synthetic contracts do not require market-data rights |
| D-014 | Accepted Phase 1 | Architecture | Stable entity -> security -> listing identity with effective-dated attributes | Tickers, ISINs and names are not permanent identity; ADR-0005 |
| D-015 | Accepted Phase 1 | Architecture | Explicit PIT views and UTC availability gates | Prevent future/restatement leakage; ADR-0006 |
| D-016 | Accepted Phase 1 | Architecture | Standard-library canonical JSON evidence for Task 1; defer DuckDB/Parquet | Minimum sufficient offline boundary; ADR-0008 |
| D-017 | Accepted Phase 1 | Tooling | Use pinned uv 0.8.3 with committed `uv.lock`; bootstrap only from `requirements-dev.txt` | Frozen sync/export provides cross-platform hashes; CI audits the frozen export |
| D-018 | Superseded Phase 1 | Repository | Initial branch was based on a Phase 0 foundation tip while local/remote state was inconsistent | Repository reconciliation confirmed Phase 0 on `origin/main`; the Phase 1 branch was rebuilt/pushed against the reconciled history, so the initial condition no longer applies |
| D-019 | Accepted Phase 1 | Storage | Publish immutable objects via flushed temp file plus exclusive atomic hard link | Standard-library atomic no-overwrite semantics; verified reads detect corruption |
| D-020 | Accepted Phase 1 | Corporate actions | Multiplicative actions are listing-scoped and ledger identity binds canonical action, source series and method | Prevents cross-security application and duplicate adjustment after restart |
| D-021 | Verified Phase 1 | Release | PASS Phase 1 Task 1 synthetic foundation at commit `ad622f6dd6f2e24d7f774134fdec68a90b0d2caf` | Four remediation re-reviews passed their scopes; 61 local tests and build/install checks passed; GitHub Actions run 29210718504 reports quality, dependency-audit and secret-scan success. Known limitations remain documented; this is not production, real-data, recommendation or later-phase readiness |

No entry silently amends `MASTER_SPEC.md`; proposed corrections interpret ambiguous phase/release language and require human confirmation where noted.
