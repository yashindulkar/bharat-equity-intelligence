# Threat Model

## Scope and assets

Phase 1 protects source integrity, provider credentials, code/dependencies, research configuration, lineage and audit evidence. Later high-value assets include identity, suitability, portfolio, tax lots, sessions, backups and decision history.

## Trust boundaries and threats

| Boundary | Threat | Required control / failure behavior |
|---|---|---|
| Provider/file -> ingestion | Malformed data, replay, poisoning, document prompt injection | Size/schema/type/time validation, hashes, allowlisted parsers, content never executes; conflict/staleness blocks output |
| Dependency/build | Typosquat or compromised package | Minimal locked hashes, review, vulnerability scan, SBOM; no unreviewed install |
| Storage/query | Mutation, time-travel leakage, unauthorized copy | Append-only versions, as-of tests, least privilege, encryption where personal/licensed, redacted logs |
| User/session (later) | Account takeover/shared-device exposure | Strong auth, secure recovery/session expiry, role separation, audit, rate limiting |
| AI/telemetry (later) | Portfolio exfiltration, hallucination, prompt injection | No personal data by default; explicit vendor/privacy decision, minimization, citations; deterministic rules authoritative |
| Backup/export | Unencrypted leakage or unrecoverable state | Encrypted backups, entitlement-aware retention, restore tests, access logging |
| Publication | Stale/tampered/misleading output | Signed/hash-linked manifests, timestamps, health state, abstention, immutable journal evidence |

## Phase 1 security acceptance

No network in unit tests; empty secret placeholders; CI secret scanning; hostile fixtures; bounded parsing; no secrets/personal/licensed data in Git/logs; reason-coded fail-closed output; hashes and reproducible manifests. The custom `.env.example` assertion only verifies selected placeholders are empty—it is not a repository secret scanner. Phase 1 Task 1 uses a frozen uv lock, dependency audit, repository history/directory secret scans and immutable action pins; GitHub Actions run 29210718504 verified these gates. Hash chaining is tamper-evident, not automatically tamper-proof, and the synthetic local store is not a production security boundary.

## Privacy lifecycle

Before personal data, define purpose, minimization, consent/authority, access, correction, export, retention, deletion, legal hold, processors, region, incident owner and recovery. Keep mutable identity/profile separate from pseudonymous append-only decision facts; counsel resolves erasure/audit tension.
