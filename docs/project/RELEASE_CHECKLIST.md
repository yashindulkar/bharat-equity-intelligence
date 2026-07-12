# Release Checklist

## Phase 1 Task 1 evidence (2026-07-11)

- [x] Synthetic-only domain, PIT, provider, manifest and CLI foundation exists.
- [x] Independent identity, PIT, corporate-action and data/security reviews ran (four agents total).
- [x] Unit/property-style/leakage/integration/security tests run offline.
- [x] Cross-record identity validators and adversarial corporate-action fixtures pass locally.
- [x] Atomic create-only evidence writes and hash-verified reads pass locally.
- [x] Frozen uv lock, local dependency vulnerability scan and immutable CI action pins pass locally.
- [x] Draft PR #2 targets aligned `main` and remains unmerged.
- [x] Four remediation re-reviews report no critical finding in their assigned local scopes.
- [x] Local full suite passes (61 tests); isolated sdist/wheel build, wheel install and installed CLI pass.
- [x] Local dependency audit and Gitleaks history/directory scans pass.
- [ ] Updated GitHub Actions run is green after the remediation push.

**Release decision: FAIL pending updated GitHub Actions and final independent re-review.** Local evidence alone does not close remote release gates.

## Phase 0

- [x] `MASTER_SPEC.md` read fully and preserved as authority
- [x] Repository/environment assessed without exposing credentials
- [x] Six skeptical specialist workstreams reviewed by three independent subagent runs; method and
      limitation recorded in `docs/agent-reviews/`
- [x] Required documents, ADRs, structure and offline check created
- [x] Facts/assumptions/proposals/open questions distinguished
- [x] MVP/V1/later boundaries and Phase 1 criteria defined
- [x] No data, backtest, recommendation, profit claim or broker order code created
- [ ] Human confirms proposed phase interpretation and deferred legal/data/license decisions
- [ ] Independent human/legal review of regulatory and licensing conclusions

The Phase 0 custom placeholder assertion is not a secret scanner. CI runs Gitleaks separately.
Dependency-vulnerability scanning and a hashed cross-platform lock are Phase 1 release-blocking tasks.

## Every later phase

- [ ] Acceptance tests, docs, reproduction and rollback/recovery pass
- [ ] No critical security, data-quality, licensing or leakage finding is open
- [ ] Lineage and known limitations are complete
- [ ] Independent reviewer signs off; no author self-validates critical work
- [ ] No unsupported performance or compliance claim appears
- [ ] Release decision and evidence are recorded

**Phase 0 decision: CONDITIONAL PASS.** Conditions are the unchecked human/legal items; Phase 1 real-data work is blocked until its data entry gate passes.
