"""Cross-record half-open interval conflict validators."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from itertools import combinations
from typing import TypeVar

from .errors import ReasonCode
from .models import (
    ClassificationHistory,
    ExchangeListing,
    IdentifierHistory,
    IndexMembershipHistory,
    ISINHistory,
    SymbolHistory,
)

T = TypeVar(
    "T",
    SymbolHistory,
    ISINHistory,
    ClassificationHistory,
    IndexMembershipHistory,
    IdentifierHistory,
)


@dataclass(frozen=True, slots=True)
class IntervalConflict:
    code: ReasonCode
    subject_key: tuple[str, ...]
    left_value: str
    right_value: str
    overlap_at: datetime


def intervals_overlap(left: T, right: T) -> bool:
    left_end = left.effective_until
    right_end = right.effective_until
    return (left_end is None or right.effective_at < left_end) and (
        right_end is None or left.effective_at < right_end
    )


def _conflicts(
    records: list[T],
    *,
    subject: Callable[[T], tuple[str, ...]],
    value: Callable[[T], str],
    duplicate_is_conflict: bool,
) -> tuple[IntervalConflict, ...]:
    found: list[IntervalConflict] = []
    for left, right in combinations(records, 2):
        left_subject = subject(left)
        if left_subject != subject(right) or not intervals_overlap(left, right):
            continue
        left_value = value(left)
        right_value = value(right)
        successive_correction = (
            left.superseded_at is not None and left.superseded_at <= right.usable_from
        ) or (right.superseded_at is not None and right.superseded_at <= left.usable_from)
        if successive_correction:
            continue
        if duplicate_is_conflict or left_value != right_value:
            found.append(
                IntervalConflict(
                    ReasonCode.IDENTITY_CONFLICT,
                    left_subject,
                    left_value,
                    right_value,
                    max(left.effective_at, right.effective_at),
                )
            )
    return tuple(found)


def validate_symbol_histories(records: list[SymbolHistory]) -> tuple[IntervalConflict, ...]:
    return _conflicts(
        records,
        subject=lambda r: (r.listing_id,),
        value=lambda r: r.symbol,
        duplicate_is_conflict=True,
    )


def validate_isin_histories(records: list[ISINHistory]) -> tuple[IntervalConflict, ...]:
    return _conflicts(
        records,
        subject=lambda r: (r.security_id,),
        value=lambda r: r.isin,
        duplicate_is_conflict=True,
    )


def validate_classification_histories(
    records: list[ClassificationHistory],
) -> tuple[IntervalConflict, ...]:
    return _conflicts(
        records,
        subject=lambda r: (r.company_id, r.taxonomy),
        value=lambda r: f"{r.sector}|{r.industry}",
        duplicate_is_conflict=False,
    )


def validate_index_memberships(
    records: list[IndexMembershipHistory],
) -> tuple[IntervalConflict, ...]:
    return _conflicts(
        records,
        subject=lambda r: (r.security_id, r.index_id),
        value=lambda r: r.index_id,
        duplicate_is_conflict=True,
    )


def validate_identifier_histories(
    records: list[IdentifierHistory],
) -> tuple[IntervalConflict, ...]:
    return _conflicts(
        records,
        subject=lambda r: (r.issuer, r.identifier_type, r.identifier_value),
        value=lambda r: r.security_id,
        duplicate_is_conflict=True,
    )


def validate_listing_intervals(records: list[ExchangeListing]) -> tuple[IntervalConflict, ...]:
    found: list[IntervalConflict] = []
    for left, right in combinations(records, 2):
        if left.listing_id != right.listing_id:
            continue
        left_end = left.effective_until
        right_end = right.effective_until
        overlap = (left_end is None or right.effective_at < left_end) and (
            right_end is None or left.effective_at < right_end
        )
        if overlap:
            found.append(
                IntervalConflict(
                    ReasonCode.IDENTITY_CONFLICT,
                    (left.listing_id,),
                    left.security_id,
                    right.security_id,
                    max(left.effective_at, right.effective_at),
                )
            )
    return tuple(found)
