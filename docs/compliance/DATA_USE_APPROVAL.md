# Data-use approval record

**Verified:** no real provider is approved.

The approval packet must identify provider/product/agreement/version/effective dates, exact termination event, permitted users/purpose, raw retention, derived data, backtesting, model training, display, citation, backup, fixtures, geography, AI/subprocessors, versioned evidence, reviewer, approval/rejection timestamps, and review deadline. Only construction-valid `APPROVED` records with explicit `PERMITTED` rights for the intended use may pass. Silence, unknown enum values, blank users/evidence, incoherent decision timestamps, and future/out-of-interval approvals fail closed.

Processing geography is an evidence-backed typed grant: either a nonempty canonical jurisdiction list or explicit `WORLDWIDE`. Empty rights do not mean unrestricted processing. Worldwide rights cannot coexist with restrictions, and a jurisdiction cannot be both permitted and restricted.

Post-termination terms separately govern raw data, backups, fixtures, derived data and audit hashes/evidence. The authoritative lifecycle registry must contain one exact provider/product/policy/agreement/termination-event record when termination applies. Every category has its own permission, deadline, state, evidence, verifier and version. Category-bound deletion evidence is not transferable to another category. `RETAINED` requires permission and is not represented as `COMPLETED`. Missing/mismatched lifecycle state and overdue prohibited retention fail independently from the unconditional new-ingestion rejection.

Provider envelopes and scorecards bind the policy ID, agreement version and immutable policy snapshot. Entry evidence must have existed by its claimed entry assessment; scorecard-level evidence must have existed by the scorecard assessment; all evidence and assessments must also precede the evaluation cutoff. Post-termination retention permission never authorizes new retrieval.

**Verified — human statement 2026-07-13:** Yash operates; Yash's mother makes the final investment decision; household-only/private/no-public/no-paid/no-sharing/no-social use; local-first Mac; NSE/EOD/prospective Nifty 200 scope; no personal portfolio data; BSE deferred; external AI access to licensed raw data denied absent explicit contract permission.

**Open questions:** viewers, hosting country, retention, backup, cloud storage, specific AI exception, budget, provider/product/agreement, benchmark rights, and qualified licensing review.
