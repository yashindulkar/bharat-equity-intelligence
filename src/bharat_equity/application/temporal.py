"""Explicit point-in-time selection."""

from __future__ import annotations

from collections.abc import Hashable, Sequence
from datetime import datetime
from enum import StrEnum
from typing import TypeVar

from bharat_equity.domain.errors import DomainError, ReasonCode
from bharat_equity.domain.models import (
    ClassificationHistory,
    FinancialFact,
    FinancialFiling,
    IdentifierHistory,
    IndexMembershipHistory,
    ISINHistory,
    SymbolHistory,
    TemporalRecord,
    require_utc,
)

T = TypeVar("T", bound=TemporalRecord)


class VintageView(StrEnum):
    AS_KNOWN_THEN = "AS_KNOWN_THEN"
    LATEST_CORRECTED = "LATEST_CORRECTED"


def is_effective(record: TemporalRecord, business_at: datetime) -> bool:
    require_utc(business_at, "business_at")
    return record.effective_at <= business_at and (
        record.effective_until is None or business_at < record.effective_until
    )


def logical_version_key(record: TemporalRecord) -> Hashable:
    if isinstance(record, FinancialFiling):
        return ("filing", record.version_chain_id, record.company_id, record.period_id)
    if isinstance(record, FinancialFact):
        return (
            "fact",
            record.version_chain_id,
            record.company_id,
            record.period_id,
            record.reporting_scope,
            record.metric,
            record.unit,
            record.currency,
        )
    if isinstance(record, SymbolHistory):
        return ("symbol", record.listing_id)
    if isinstance(record, ISINHistory):
        return ("isin", record.security_id)
    if isinstance(record, IdentifierHistory):
        return ("identifier", record.security_id, record.identifier_type, record.issuer)
    if isinstance(record, ClassificationHistory):
        return ("classification", record.company_id, record.taxonomy)
    if isinstance(record, IndexMembershipHistory):
        return ("membership", record.security_id, record.index_id)
    raise DomainError(
        ReasonCode.IDENTITY_CONFLICT,
        f"{type(record).__name__} has no intrinsic logical version key",
    )


def select_vintage(
    records: Sequence[T],
    *,
    business_at: datetime,
    cutoff: datetime,
    view: VintageView,
) -> T | None:
    """Select an admissible record deterministically; cutoffs are never implicit."""
    require_utc(cutoff, "cutoff")
    if records:
        keys = {logical_version_key(record) for record in records}
        if len(keys) != 1:
            raise DomainError(
                ReasonCode.IDENTITY_CONFLICT,
                "vintage candidates must belong to one logical version chain",
            )
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
