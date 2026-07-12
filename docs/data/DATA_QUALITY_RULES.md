# Data Quality Rules

Hard failures include stale critical prices (`DATA_STALE`), missing identity (`CRITICAL_FIELD_MISSING`), unresolved provider conflict, future information, invalid OHLC/negative volume, identity conflicts, unsupported or duplicate corporate actions and duplicate source records. Hard failures force `DATA_BLOCKED`; an aggregate completeness value cannot override them.

Provider conflicts and duplicates are preserved as evidence. Staleness must ultimately be calendar/session-relative. Financial-sector fixtures exist to prove industrial formulas are inapplicable; Task 1 implements no factor formulas.

Every `ReasonCode` has an exhaustive `HARD_BLOCK`, `INSUFFICIENT_EVIDENCE`, or `WARNING` classification. Unknown codes cannot silently receive a weaker status. Manifest duplicates emit `DUPLICATE_SOURCE_RECORD` as well as deterministic counts.
