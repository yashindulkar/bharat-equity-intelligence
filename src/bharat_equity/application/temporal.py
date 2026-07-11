"""Explicit point-in-time selection."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import TypeVar

from bharat_equity.domain.models import TemporalRecord, require_utc

T = TypeVar("T", bound=TemporalRecord)


class VintageView(StrEnum):
    AS_KNOWN_THEN = "AS_KNOWN_THEN"
    LATEST_CORRECTED = "LATEST_CORRECTED"


def is_effective(record: TemporalRecord, business_at: datetime) -> bool:
    require_utc(business_at, "business_at")
    return record.effective_at <= business_at and (
        record.effective_until is None or business_at < record.effective_until
    )


def select_vintage(
    records: list[T], *, business_at: datetime, cutoff: datetime, view: VintageView
) -> T | None:
    """Select an admissible record deterministically; cutoffs are never implicit."""
    require_utc(cutoff, "cutoff")
    candidates = [r for r in records if is_effective(r, business_at) and r.usable_from <= cutoff]
    if view is VintageView.AS_KNOWN_THEN:
        candidates = [r for r in candidates if r.superseded_at is None or cutoff < r.superseded_at]
    if not candidates:
        return None

    def stable_id(record: TemporalRecord) -> str:
        for name in ("filing_id", "fact_id", "action_id", "source_record_id"):
            value = getattr(record, name, None)
            if isinstance(value, str):
                return value
        return record.schema_version

    return max(candidates, key=lambda r: (r.revision, r.usable_from, stable_id(r)))
