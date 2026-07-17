# Phase 1 Task 2 independent reviews

## Method and independence

**Verified — orchestration record, 2026-07-13.** Five separate read-only specialist subagents reviewed the shared working tree. They did not author or edit files. They were independently prompted for distinct scopes, but they shared the same repository, model family, conversation context, and orchestrator; they are not independent human experts, legal counsel, an exchange, or a provider. Some reviewers could not execute the repository toolchain in their agent shell. The primary agent implemented remediations and ran the full local/CI verification.

**Verified — remediation scope, 2026-07-16.** The later PR #4 release-blocking findings were supplied by the human and remediated by the primary agent. No claim is made that the five 2026-07-13 agents independently reviewed the 2026-07-16 follow-up commit. Their historical records below are expanded without rewriting what they actually did.

## Review 1 — Indian market-data architecture

- Reviewer scope: provider-neutral Indian equity data architecture, venue/instrument boundaries, capability evidence, and field requirements.
- Files inspected: `src/bharat_equity/domain/provider_policy.py`, `src/bharat_equity/application/provider_evaluation.py`, `docs/data/REAL_DATA_ENTRY_GATE.md`, `docs/data/FIELD_REQUIREMENTS.md`, ADR-0011, ADR-0012, ADR-0016, and the Task 2 plan.
- Tests/commands run: read-only source/document inspection; no reviewer test command was reported.
- Initial findings:
  - **Critical:** capability registry and policy were not bound to the same provider/product/user/geography.
  - **High:** supported capabilities could lack capability-specific evidence.
  - **High:** field requirements used compound rows instead of atomic field declarations.
- Remediation examined: exact provider/product/user/geography checks, per-capability evidence map, and individually declared EOD/action/filing/universe/benchmark fields.
- Remaining limitations recorded by reviewer: none at critical/high severity; no production provider or calendar behavior was reviewed.
- Final decision: **PASS** for the assigned static architecture scope.

## Review 2 — PIT and historical universe

- Reviewer scope: point-in-time availability, historical universe/delistings, history range semantics, and UTC behavior.
- Files inspected: `provider_policy.py`, `provider_evaluation.py`, Task 1 temporal contracts, `docs/data/REAL_DATA_ENTRY_GATE.md`, ADR-0016, and temporal/provider tests.
- Tests/commands run: read-only inspection; no reviewer test command was reported.
- Initial findings:
  - **Critical:** policy/capability provider-product mismatch could pass.
  - **High:** historical depth, historical symbols, and stable identifiers were not mandatory.
  - **High:** historical coverage lacked explicit range/gap semantics.
  - **Medium:** evaluation timestamp validation and supersession-gap coverage needed improvement.
- Remediation examined: provider/product binding, mandatory PIT capability set, UTC history bounds, explicit coverage start/end, gap denial, and adversarial mismatch/gap tests.
- Remaining limitations recorded by reviewer: isolated range/capability test cases could be expanded; production market-calendar resolution remained outside scope.
- Final decision: **PASS** with no remaining critical/high finding in the assigned scope.

## Review 3 — licensing, retention, and derived-data rights

- Reviewer scope: agreement identity/dates, users, geography, purpose-specific use, retention, derived data, backup, fixtures, AI, citation, termination, and approval evidence.
- Files inspected: `provider_policy.py`, `provider_evaluation.py`, `DATA_USE_APPROVAL.md`, `REAL_DATA_ENTRY_GATE.md`, `DECISION_LOG.md`, and provider-gate tests.
- Tests/commands run: static inspection. The reviewer explicitly reported that `uv`/pytest was unavailable in its shell, so it did not execute tests.
- Initial findings:
  - **Critical:** purpose-specific permissions, provider/product binding, and permitted users were fail-open.
  - **High:** geography, AI/subprocessors, and deletion/retention lifecycle were not executable.
  - Later re-review found termination, geography semantics, future approval, and citation enforcement gaps.
- Remediation examined: exact identity/user/geography binding, explicit purpose/capability pairs, approval/review timing, unconditional new-entry block after termination, AI/citation/backup/derived controls, and adversarial tests.
- Remaining limitations recorded by reviewer: pass was static and depended on the primary agent/CI for execution evidence; no legal conclusion or contract approval.
- Final decision: **PASS** for the assigned static licensing-contract scope.

## Review 4 — data quality, reconciliation, and quarantine

- Reviewer scope: hard-gate/publication coupling, conflict preservation, decision invariants, warnings, quarantine, and rejection.
- Files inspected: `provider_policy.py`, `provider_evaluation.py`, `RECONCILIATION_POLICY.md`, `QUARANTINE_POLICY.md`, and provider-entry/interval tests.
- Tests/commands run: focused pytest runs reported first as 18/18, later 15/15 after remediation.
- Initial findings:
  - **High:** publication accepted a caller-supplied approval boolean rather than an invariant hard-gate result.
  - **High:** no typed competing-value reconciliation object was connected to publication.
  - **Medium:** publication decisions allowed inconsistent construction and warnings could be dropped.
  - Re-review found forgeable `GateResult` and incomplete conflict/publication association.
- Remediation examined: invariant `GateResult`, typed competing values and conflict review metadata, publication association, status invariants, and warning preservation.
- Remaining limitations recorded by reviewer: more direct serialization/invariant tests would improve coverage; none remained critical/high at final review.
- Final decision: **PASS** for the assigned scope.

## Review 5 — security and provider credentials

- Reviewer scope: credential lifecycle, licensed payload/AI/backup controls, envelope integrity, network-test boundary, secrets, and provider capability/permission pairing.
- Files inspected: `provider_policy.py`, `provider_evaluation.py`, `tests/conftest.py`, provider/security tests, `THREAT_MODEL.md`, `.env.example`, workflow/action pins, and provider contract checklist.
- Tests/commands run: focused tests reported as 16 passed and `git diff --check` passed. An earlier reviewer shell lacked pytest; the final focused run succeeded.
- Initial findings:
  - **High:** required capabilities did not pair with retention/backup/derived/display/fixture/model/backtest permissions.
  - **High:** network denial covered too few socket paths.
  - **High:** provider envelope schema/hash validation was incomplete.
  - **Medium:** approval-time and credential lifecycle controls were incomplete.
- Remediation examined: capability/permission pairs, expanded direct Python socket denial, strict qualified SHA-256/schema validation, approval timing, and keychain/scope/rotation/revocation/redaction documentation.
- Remaining limitations recorded by reviewer: future production adapters require credential-redaction and revocation failure tests. The pytest fixture is direct-Python-socket denial, not a subprocess/network namespace sandbox.
- Final decision: **PASS** with no remaining critical/high finding in the assigned scope.

## Historical conclusion

The five 2026-07-13 reviews ended with no reported critical/high blocker in their assigned scopes. This evidence supports only the provider-entry architecture and synthetic harness at the reviewed commit. It approves no provider, contract, real dataset, ranking, backtest, or recommendation.

## External architecture-review remediation — 2026-07-17

**Verified — provenance.** The latest external architecture review supplied the twelve findings covering authoritative lifecycle state, agreement identity, category deletion evidence, geography, envelope snapshots, reconciliation execution, scorecard PIT binding, historical-gap ambiguity, publication artifacts, property coverage, network wording and release evidence.

**Verified — implementation.** Primary-agent commit `f03797da08849e5e7062b74b579666b7fedc7153` implemented the code/test corrections. The primary agent inspected the final diff and ran the repository validation recorded in `RELEASE_CHECKLIST.md`.

**Limitation.** The original five specialist agents did not independently review this 2026-07-17 remediation. They were not reactivated, and no new independent agent review was run. This record does not rewrite their historical findings or decisions. A new independent ChatGPT architecture review remains required before any merge recommendation.
