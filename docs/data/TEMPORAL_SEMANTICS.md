# Temporal Semantics

All instants are aware UTC. `effective_at` begins business truth; `effective_until` is its exclusive end. `published_at` is source release time; `observed_at` first authorized observation; `ingested_at` evidence custody; `validated_at` required validation completion; `usable_from` earliest permitted decision use; `superseded_at` system-time acceptance of replacement. `usable_from >= max(published_at, observed_at, ingested_at, validated_at)`.

`AS_KNOWN_THEN(C)` requires `usable_from <= C` and no supersession at/before C. `LATEST_CORRECTED(V)` selects the highest accepted revision usable by explicit view cutoff V. Both still require the business-effective interval to contain the requested business time. No cutoff defaults to wall-clock now.

After-close behavior uses exact instants. Asia/Kolkata is display/session logic only; internal data remains UTC. Missing exact publication time for critical evidence blocks same-session use.
