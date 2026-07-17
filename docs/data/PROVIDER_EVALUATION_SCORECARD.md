# Provider evaluation scorecard

**Proposal — version `research-defaults-1.0.0`.** Apply every hard gate in `REAL_DATA_ENTRY_GATE.md` first. A failure produces no score and cannot be offset by cost or quality.

| Dimension | Proposed weight |
|---|---:|
| PIT correctness | 25% |
| Licensing and retention | 20% |
| Security master | 15% |
| Corporate actions | 10% |
| Financial statements | 10% |
| History and delistings | 10% |
| Reliability/support | 5% |
| Cost | 5% |

These are versioned research defaults, not universal truth, provider approval, or evidence of suitability.

**Verified — implementation commits `f03797d` and `e767ee3`, 2026-07-17.** A scorecard binds provider, product, product version, policy ID, agreement version, immutable policy snapshot, scorecard version, methodology version and UTC assessment time. Scorecard-level and dimension-level evidence references require explicit availability timestamps. Every dimension entry requires a finite Decimal 0–100 score, finite Decimal 0–1 weight, evidence, assessor, UTC `assessed_at`, matching method version, explanation, and typed confidence.

The scorecard requires the exact dimension set once each and an exact Decimal weight total of 1. NaN and positive/negative infinity are rejected for both scores and weights. Construction enforces `entry evidence.available_at <= entry.assessed_at <= scorecard.assessed_at` and `scorecard evidence.available_at <= scorecard.assessed_at`; exact equality is allowed. Evaluation additionally requires every evidence and assessment instant at or before `EvaluationRequest.at`. Wrong policy/agreement/snapshot binding or future evidence fails the hard gate. The deterministic weighted total uses `ROUND_HALF_EVEN` and two decimal places. Scoring occurs only after every hard gate passes.

**Verified:** zero real providers evaluated and zero approved.
