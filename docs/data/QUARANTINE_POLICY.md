# Quarantine and publication policy

**Verified — implementation commits `f03797d` and `e767ee3`, 2026-07-17.** Publication reruns the complete hard-gate evaluator from the current capability, policy, lifecycle registry, request and scorecard. The supplied deterministic, content-addressed audit artifact must exactly equal that authoritative result across all result and snapshot fields. Its hash is not treated as authentication or proof of evaluator execution.

- `ACCEPTED`: the evaluation artifact is valid and passed, record gates pass, and no findings exist.
- `ACCEPTED_WITH_WARNINGS`: gates pass and findings are nonblocking. This includes an unresolved warning-severity conflict or a reviewer-approved conflict whose required correction/republication is fully completed with evidence.
- `QUARANTINED`: a remediable critical problem blocks canonical publication. This includes an unresolved critical conflict and any reviewed conflict with required correction or republication still pending or invalid.
- `REJECTED`: invalid/failed evaluation artifact, stale data, policy/provider failure, integrity failure, prohibited use, or invalid/non-remediable reconciliation conflict prevents publication.

Reviewer approval alone never permits a known correction/republication requirement to enter canonical publication. Completion claims without action-specific evidence fail contract construction. Strictness is `REJECTED` over `QUARANTINED` over warnings over normal acceptance. Complete typed conflicts and structured reasons are preserved; no source value is discarded and no score overrides publication status.
