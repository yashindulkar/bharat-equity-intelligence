# Release Checklist

## Phase 1 Task 2 post-merge closeout (2026-07-24)

- [x] **Verified:** PR #4 merged into `main` on 2026-07-17 as commit `a953fd4ba910906c250e94b1f419d04b55087993`.
- [x] **Verified:** the final Task 2 scope is only the provider-entry architecture, real-data entry gate and synthetic evaluation harness.
- [x] **Verified historical evidence:** before merge, code/documentation head `ce4b771b9cb5d231de40704c855c6e523a73faf6` passed GitHub Actions run [29545604918](https://github.com/yashindulkar/bharat-equity-intelligence/actions/runs/29545604918); `quality`, `dependency-audit` and `secret-scan` concluded `success`.
- [x] **Verified historical evidence:** the final recorded pre-merge local validation passed `make check` with 169 tests, unit 125, property 26, focused provider-remediation 108, offline build/install smoke, frozen dependency audit, Gitleaks and `git diff --check`.
- [x] **Verified:** this closeout synchronizes post-merge documentation without changing the Task 2 architecture.
- [x] **Verified:** zero providers, products or agreements were evaluated or approved; no adapter, real data, scraping, ranking, factors, backtesting, recommendations, portfolio logic, UI, ML or broker integration was introduced.
- [x] **Verified:** real-data operation remains blocked. Provider selection and RFI work belongs to the next separately approved task.
- [x] **Verified locally 2026-07-24:** `uv run --frozen --extra dev make check` passed structure/local-link checks, compilation, Ruff format/lint, strict mypy and the full suite: 169 tests.
- [x] **Verified locally 2026-07-24:** unit 125, property 26, leakage 10, integration 7 and security 1 tests passed in the explicit category run.
- [x] **Verified locally 2026-07-24:** explicit-offline sdist/wheel build and clean installed-wheel CLI smoke passed; the frozen dependency audit reported `No known vulnerabilities found`.
- [x] **Verified locally 2026-07-24:** Gitleaks history scan covered 22 commits and the working-directory scan also completed; both reported `no leaks found`.
- [x] **Verified locally 2026-07-24:** `git diff --check` passed.
- [x] **Proposal — next planned task:** Phase 1 Task 3 — Provider Selection and RFI. Task 3 has not been implemented and requires a separate architecture/planning review before implementation.

**Release decision:** PASS only for the Phase 1 Task 2 provider-entry architecture and synthetic evaluation harness. The dated pre-merge sections below remain historical evidence; their draft/unmerged statements describe the state when written and are superseded only by this closeout.

**Closeout validation limitation:** no closeout-branch CI result is claimed before the draft PR runs its workflow. Local structure/link validation checks repository-local links only; it does not re-verify external URLs.

## Phase 1 Task 2 latest two-finding remediation (2026-07-17)

- [x] Publication independently recomputes the complete hard-gate result from current immutable inputs.
- [x] Artifact comparison covers schema/ID, pass state, ordered reasons, score/version, every capability/policy/lifecycle/scorecard/request snapshot, and evaluation cutoff.
- [x] An internally consistent forged artifact cannot turn a failing authoritative result into publication authorization.
- [x] Entry evidence cannot postdate its entry assessment; scorecard evidence cannot postdate its scorecard assessment; entries cannot postdate the scorecard.
- [x] Evaluation-cutoff checks remain independent and fail future assessment/evidence.
- [x] **Verified locally 2026-07-17:** `make check` passed structure/link, compilation, Ruff format/lint, strict mypy and the full suite: 169 tests.
- [x] **Verified locally 2026-07-17:** unit 125, property 26 and focused provider-remediation 108 tests passed; `git diff --check` passed.
- [x] **Verified locally 2026-07-17:** offline sdist/wheel build, clean installed-wheel CLI smoke, frozen dependency audit (`No known vulnerabilities found`) and Gitleaks history scan (`19 commits`, `no leaks found`) passed.
- [x] **Verified 2026-07-17:** code/documentation head `ce4b771b9cb5d231de40704c855c6e523a73faf6` passed GitHub Actions run [29545604918](https://github.com/yashindulkar/bharat-equity-intelligence/actions/runs/29545604918); `quality`, `dependency-audit` and `secret-scan` all concluded `success`.

**Boundary:** zero providers evaluated or approved. No real data, adapter, scraping, ranking, factors, backtesting, recommendations, portfolio logic, UI, ML or broker integration. The original specialist agents were not reactivated. PR #4 must remain draft and unmerged pending a new independent ChatGPT architecture review.

## Phase 1 Task 2 final architecture-review remediation (2026-07-17)

- [x] Scope remains provider-entry architecture and synthetic evaluation only.
- [x] Terminated agreements require an authoritative exact-agreement lifecycle record; omission and substitution fail with distinct reasons.
- [x] Raw, backup, fixture, derived and audit-evidence dispositions have category-bound evidence and distinct retained/deleted states.
- [x] Processing geography is a typed evidenced jurisdiction/worldwide grant; empty, unknown and overlapping rights fail closed.
- [x] Envelopes bind agreement version and policy snapshot while hashing the exact received bytes.
- [x] Reconciliation review is separate from correction/republication execution; incomplete remediation quarantines.
- [x] Scorecards bind policy/agreement snapshots and reject future assessments/evidence.
- [x] Ambiguous universe-gap relevance blocks unless cutoff-available effective-dated evidence proves disjointness.
- [x] Historical control: publication required a factory-controlled content-addressed artifact matching evaluated snapshots. **Superseded by the independently recomputed authorization in the newer section above.**
- [x] Common direct Python socket connection/datagram APIs are denied by pytest. This is not subprocess, native-extension, container or operating-system-level network isolation.
- [x] **Verified locally 2026-07-17:** structure/link checks, compilation, Ruff format/lint, strict mypy and full suite passed: 156 tests.
- [x] **Verified locally 2026-07-17:** unit 113, property 25, focused provider-remediation 95; deterministic Hypothesis profile retained.
- [x] **Verified locally 2026-07-17:** `git diff --check`, offline sdist/wheel build, installed-wheel CLI smoke, frozen dependency audit (`No known vulnerabilities found`) and Gitleaks history scan (`no leaks found`) passed.
- [x] **Verified 2026-07-17:** documentation head `171c38296046e219c34050352b0cc5e921118b3e` passed GitHub Actions run [29544526618](https://github.com/yashindulkar/bharat-equity-intelligence/actions/runs/29544526618); `quality`, `dependency-audit` and `secret-scan` all concluded `success`.

**Release boundary:** zero providers evaluated; zero providers approved; no real data, adapter, scraping, ranking, factors, backtesting, recommendations, portfolio logic, UI, ML or broker integration. All mandatory findings are fixed and CI succeeded. The architecture/harness remediation is ready for a new independent ChatGPT architecture review. No merge recommendation is made.

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
- [x] **Verified 2026-07-16:** draft PR #4 workflow run [29506071717](https://github.com/yashindulkar/bharat-equity-intelligence/actions/runs/29506071717) completed successfully for remediation commit `5935099`; jobs `quality`, `dependency-audit`, and `secret-scan` all concluded `success`.

**Release decision: PASS only for the provider-entry architecture and synthetic evaluation harness.** Zero providers, zero real datasets, zero rankings, zero backtests, and zero recommendations are approved. Production adapters, provider/calendar integrations, and real-data operation remain blocked.

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
