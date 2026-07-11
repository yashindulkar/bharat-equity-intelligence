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
| R-15 | Incomplete cross-record identity/interval validation | High / Critical | Add overlap, uniqueness, recycled-symbol and ambiguity validators before real ingestion | Domain + independent reviewer |
| R-16 | Synthetic evidence store lacks atomic verified reads | Medium / High | Atomic create-only writes and hash-on-read before non-demo use | Data/security |
| R-17 | Dependency lock and vulnerability evidence incomplete | Medium / High | Adopt uv/hash lock and run dependency audit; release remains FAIL | Architecture/security |
| R-18 | Corporate-action support mistaken for production-grade | High / Critical | Prominent limitation; only synthetic split/bonus invariant demo; unsupported/conflicting events block | Data + reviewer |

Critical risks block the applicable release until evidence is attached; “accepted risk” requires a named human and expiry date.
