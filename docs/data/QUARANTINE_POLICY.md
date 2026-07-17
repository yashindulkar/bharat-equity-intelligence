# Quarantine and publication policy

**Verified — implementation commit `f03797d`, 2026-07-17.** Publication requires a valid factory-created, content-addressed `EvaluationArtifact` matching the current capability, policy, lifecycle, scorecard and request snapshots.

- `ACCEPTED`: the evaluation artifact is valid and passed, record gates pass, and no findings exist.
- `ACCEPTED_WITH_WARNINGS`: gates pass and findings are nonblocking. This includes an unresolved warning-severity conflict or a reviewer-approved conflict whose required correction/republication is fully completed with evidence.
- `QUARANTINED`: a remediable critical problem blocks canonical publication. This includes an unresolved critical conflict and any reviewed conflict with required correction or republication still pending or invalid.
- `REJECTED`: invalid/failed evaluation artifact, stale data, policy/provider failure, integrity failure, prohibited use, or invalid/non-remediable reconciliation conflict prevents publication.

Reviewer approval alone never permits a known correction/republication requirement to enter canonical publication. Completion claims without action-specific evidence fail contract construction. Strictness is `REJECTED` over `QUARANTINED` over warnings over normal acceptance. Complete typed conflicts and structured reasons are preserved; no source value is discarded and no score overrides publication status.
