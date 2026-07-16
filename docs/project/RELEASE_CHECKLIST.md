# Release Checklist

## Phase 1 Task 2 remediation evidence (2026-07-16)

- [x] Scope remains provider-entry architecture and synthetic evaluation only.
- [x] Typed termination/deletion lifecycle replaces boolean completion state.
- [x] EOD coverage uses explicit latest required completed session; calendar adapter is deferred.
- [x] Typed history gaps block only relevant open critical intersections.
- [x] Provider envelope binds provider/product/version/policy/purpose/schema and verifies payload bytes.
- [x] Reconciliation types/invariants and policy-driven publication transitions are tested.
- [x] Data-usage policy invalid states fail at construction.
- [x] Evidence-bound, versioned scorecard replaces raw score dictionaries.
- [x] Direct Python socket denial is accurately documented; subprocess network isolation is not claimed.
- [x] Historical five-agent review records state scope, files, commands, findings, remediation, limitations, and decision.
- [x] **Verified 2026-07-16:** structure/link, compilation, Ruff format/lint, strict mypy, full tests (99), property tests (17), git diff validation, offline sdist/wheel build, installed-wheel CLI smoke, frozen dependency audit, and Gitleaks passed locally.
- [ ] Draft PR #4 CI run and all job conclusions recorded after push.

**Current release decision: CONDITIONAL PASS pending the remediation commit's GitHub Actions result.** The decision applies only to the provider-entry architecture and synthetic evaluation harness. Zero providers and zero real datasets are approved.

## Phase 1 Task 1 evidence (2026-07-11)

- [x] Synthetic-only domain, PIT, provider, manifest and CLI foundation exists.
- [x] Independent identity, PIT, corporate-action and data/security reviews ran (four agents total).
- [x] Unit/property-style/leakage/integration/security tests run offline.
- [x] Cross-record identity validators and adversarial corporate-action fixtures pass locally.
- [x] Atomic create-only evidence writes and hash-verified reads pass locally.
- [x] Frozen uv lock, local dependency vulnerability scan and immutable CI action pins pass locally.
- [x] **Verified (2026-07-13):** PR #2 passed review and CI and was squash-merged into `main` as commit `9a0c68a`.
- [x] Four remediation re-reviews report no critical finding in their assigned local scopes.
- [x] Local full suite passes (61 tests); isolated sdist/wheel build, wheel install and installed CLI pass.
- [x] Local dependency audit and Gitleaks history/directory scans pass.
- [x] GitHub Actions run 29210718504 is green: quality, dependency-audit and secret-scan succeeded.
- [x] PR #2 title, description, review evidence and explicit release decision are complete.

**Release decision: PASS for the Phase 1 Task 1 synthetic foundation, with documented limitations.** This decision does not establish production, licensed-real-data, recommendation, backtest or later-phase readiness. Complex corporate actions, multi-action adjustment economics, multiprocess storage fault injection and explicit correction predecessor graphs remain outside this Task 1 foundation.

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
Phase 1 Task 1 now has a frozen cross-platform uv lock, dependency-vulnerability scanning and immutable CI action pins. These controls must remain green for later changes.

## Every later phase

- [ ] Acceptance tests, docs, reproduction and rollback/recovery pass
- [ ] No critical security, data-quality, licensing or leakage finding is open
- [ ] Lineage and known limitations are complete
- [ ] Independent reviewer signs off; no author self-validates critical work
- [ ] No unsupported performance or compliance claim appears
- [ ] Each later phase records its own release decision and evidence; Phase 1 Task 1 evidence does not satisfy later gates

**Phase 0 decision: CONDITIONAL PASS.** Conditions are the unchecked human/legal items; Phase 1 real-data work is blocked until its data entry gate passes.
