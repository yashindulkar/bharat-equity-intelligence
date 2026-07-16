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

### Task 2 provider credential boundary

Provider credentials must come from the macOS Keychain or an equivalently reviewed local secret source, never source files, committed environment values, CLI arguments, manifests, fixtures, licensed-payload directories, logs, exceptions, or external-AI prompts. Use a product-specific least-privilege read-only credential, restrict local access to the operator, redact authorization headers and query secrets before logging, and keep credentials outside raw/staging storage and backups. Record issuer, scope, owner, rotation/expiry dates and revocation procedure without recording the secret. Rotate on schedule or suspected exposure; revoke immediately on termination or incident. A future adapter must add failure-injection tests for redaction and revocation.

**Verified test boundary:** the autouse pytest fixture denies direct Python socket connection/send APIs suite-wide (`connect`, `connect_ex`, `sendto`, `sendmsg`, and `create_connection`). It does not sandbox network-capable subprocesses, so the repository does not claim complete process-level network isolation. Tests contain no intended network subprocess. Other controls are empty secret placeholders, CI secret scanning, hostile fixtures, bounded parsing, no secrets/personal/licensed data in Git/logs, reason-coded fail-closed output, hashes, and reproducible manifests. The custom `.env.example` assertion is not a repository secret scanner. Hash chaining is tamper-evident, not automatically tamper-proof, and the synthetic local store is not a production security boundary.

## Privacy lifecycle

Before personal data, define purpose, minimization, consent/authority, access, correction, export, retention, deletion, legal hold, processors, region, incident owner and recovery. Keep mutable identity/profile separate from pseudonymous append-only decision facts; counsel resolves erasure/audit tension.
