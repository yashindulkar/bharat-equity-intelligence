# Risk Register

| ID | Risk | Likelihood / impact | Mitigation and release trigger | Owner |
|---|---|---|---|---|
| R-01 | No licensed PIT dataset meets required scope | High / Critical | Field-level contract proof before ingestion | Owner + counsel/data lead |
| R-02 | Personalized output crosses IA/RA boundary | Medium / Critical | Counsel classification; no third-party/paid/public use | Owner + counsel |
| R-03 | Survivorship/restatement/index leakage | High / Critical | Availability-time schema and adversarial tests | Data + independent quant |
| R-04 | Corporate actions adjusted incorrectly/twice | High / Critical | Event-specific ledger and verified golden cases | Data + reviewer |
| R-05 | Critical missing fact hidden by quality score | High / High | Critical-field hard gates | Data quality |
| R-06 | False precision/misleading UX | Medium / High | Suppress unsupported fields; explanations show evidence/limits | Product |
| R-07 | Suitability limits guessed | Medium / Critical | No personalized allocation until signed profile | Risk + owner |
| R-08 | Personal/portfolio data leakage | Medium / Critical | Minimize, encrypt, isolate, redact; no external AI by default | Security |
| R-09 | Provider/document prompt injection | Medium / High | Treat content as hostile data; deterministic rules retain authority | Security |
| R-10 | Overfit backtest/performance claim | High / Critical | Preregister, holdout, costs, dependence-aware uncertainty, reproduction | Quant validator |
| R-11 | Toolchain dependency/supply-chain exposure | Medium / High | Minimal pinned deps, hashes, SBOM/scans | Architecture/security |
| R-12 | Scope inflation delays usable evidence | High / Medium | Phase-specific boundaries and gates | Product/orchestrator |
| R-13 | Immutable audit conflicts with correction/erasure | Medium / High | Pseudonymous append-only facts; separate mutable identity; counsel | Security/privacy |
| R-14 | Empty repo/history alignment mistakes | Medium / Medium | Confirm branch tracking/commit policy before publishing | Maintainer |
| R-15 | Cross-record identity/interval conflicts recur as schemas expand | Medium / Critical | Task 1 typed overlap, uniqueness, recycled-identifier and listing validators pass; extend and independently review before real ingestion | Domain + independent reviewer |
| R-16 | Synthetic evidence-store guarantees are mistaken for production durability | Medium / High | Task 1 atomic create-only writes and hash-verified reads pass; require multiprocess race, directory-fsync fault and production-store review before non-demo use | Data/security |
| R-17 | Dependency or CI supply-chain controls drift | Medium / High | Task 1 frozen uv lock, clean audit and immutable action pins pass; keep automated audit/secret scan required and review lock changes | Architecture/security |
| R-18 | Corporate-action support mistaken for production-grade | High / Critical | Prominent limitation; only synthetic split/bonus invariant demo; unsupported/conflicting events block | Data + reviewer |
| R-19 | Capability marketing is mistaken for contractual evidence | High / Critical | Tri-state registry; unknown fails; clause/sample evidence and reviewer required | Licensing reviewer |
| R-20 | Licensed raw data leaks through AI, cloud, backup or fixtures | Medium / Critical | Purpose-specific policy gates; default deny; credentials and payloads excluded from Git/logs/AI | Security + owner |
| R-21 | Provider score overrides a legal/PIT hard gate | Medium / Critical | Score is `None` on any gate failure; adversarial tests | Architecture + validation |
| R-22 | Source precedence silently destroys conflicting evidence | Medium / Critical | Append competing values; structured conflict; quarantine and human escalation | Data quality |
| R-23 | Contract termination leaves prohibited raw/backup/fixture copies | Medium / Critical | Typed deletion deadline and per-category state; overdue prohibited retention hard-blocks; verification evidence required | Owner + licensing/security |
| R-24 | Wall-clock time is mistaken for latest completed EOD session | High / Critical | Caller supplies explicit latest required session; production market-calendar resolution deferred and separately reviewed | Data platform + PIT reviewer |
| R-25 | Broad or irrelevant provider history gaps block valid use, or relevant gaps pass | Medium / Critical | Typed domain/venue/scope intervals; only intersecting open critical gaps block; property tests | Data quality |
| R-26 | Provider envelope is replayed or rebound to another product/policy/purpose | Medium / Critical | Exact binding, allowed-schema gate, agreement dates, and payload-byte SHA-256 verification | Security + provider architecture |
| R-27 | Subjective provider score lacks evidence or masks a hard failure | Medium / High | Exact versioned dimensions, evidence/assessor/method/confidence, weights=1, score only after hard gates | Architecture + independent reviewer |
| R-28 | Terminated agreement omits or substitutes lifecycle state | Medium / Critical | Authoritative registry; exact agreement/event binding; missing/mismatch reasons; boundary/property tests | Licensing + security |
| R-29 | One deletion certificate is reused across governed categories | Medium / Critical | Independent immutable dispositions and category-bound evidence/verifier/version | Licensing + security |
| R-30 | Empty or ambiguous geography is interpreted as unrestricted | Medium / Critical | Typed jurisdiction/worldwide grant; canonical IDs; overlap construction checks; unknown denies | Licensing + security |
| R-31 | Envelope or scorecard is rebound to an earlier agreement/policy snapshot | Medium / Critical | Exact agreement version and content-addressed policy binding | Provider architecture |
| R-32 | Reviewer approval is mistaken for completed correction/republication | Medium / Critical | Separate remediation execution state/evidence; incomplete work quarantines | Data quality |
| R-33 | Future or post-assessment score evidence creates false PIT chronology | Medium / Critical | Evidence must exist by its claimed entry/scorecard assessment; all evidence and assessments must also precede the request cutoff | PIT reviewer |
| R-34 | Ambiguous historical universe membership hides a relevant gap | High / Critical | Closed intervals; effective-dated evidence; unknown/incomplete coverage blocks | PIT + data quality |
| R-35 | Caller fabricates publication approval with an internally consistent artifact | Medium / Critical | Publication independently recomputes the complete hard-gate result and compares every audit-artifact result/snapshot field; content hash is not authentication | Architecture + security |
| R-36 | Test network control is mistaken for OS isolation | Medium / High | Exact wording: common direct Python socket APIs only; no subprocess/native/container/OS sandbox claim | Security |
| R-37 | Task 3 provider selection starts without a separately approved architecture/planning review | Medium / Critical | Keep Task 3 as a status boundary until its scope, evidence standard, reviewers and legal/licensing gates are separately reviewed and approved | Orchestrator + owner + licensing reviewer |

Critical risks block the applicable release until evidence is attached; “accepted risk” requires a named human and expiry date. Phase 1 Task 1 PASS applies only to its synthetic foundation. Phase 1 Task 2 PASS applies only to the provider-entry architecture and synthetic evaluation harness. Neither closes the real-data, provider-selection, regulatory or production triggers above.
