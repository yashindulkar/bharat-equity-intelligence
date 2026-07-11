"""Typed Phase 1 contracts. All instants are aware UTC and decimals serialize as strings."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, date, datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any, ClassVar

from .errors import DomainError, ReasonCode

SCHEMA_VERSION = "1.0.0"


def require_utc(value: datetime, name: str) -> None:
    if (
        value.tzinfo is None
        or value.utcoffset() is None
        or value.utcoffset() != UTC.utcoffset(value)
    ):
        raise DomainError(ReasonCode.INVALID_TIMESTAMP, f"{name} must be timezone-aware UTC")


def _json_value(value: Any) -> Any:
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, datetime | date):
        return value.isoformat()
    if isinstance(value, StrEnum):
        return value.value
    if isinstance(value, tuple):
        return [_json_value(item) for item in value]
    if isinstance(value, dict):
        return {key: _json_value(item) for key, item in value.items()}
    return value


@dataclass(frozen=True, slots=True)
class Contract:
    schema_version: str = field(default=SCHEMA_VERSION, kw_only=True)
    SCHEMA: ClassVar[str] = SCHEMA_VERSION

    def to_dict(self) -> dict[str, Any]:
        return _json_value(asdict(self))  # type: ignore[no-any-return]


@dataclass(frozen=True, slots=True, kw_only=True)
class EffectivePeriod(Contract):
    effective_at: datetime
    effective_until: datetime | None = None

    def __post_init__(self) -> None:
        require_utc(self.effective_at, "effective_at")
        if self.effective_until is not None:
            require_utc(self.effective_until, "effective_until")
            if self.effective_until <= self.effective_at:
                raise DomainError(
                    ReasonCode.INVALID_TIMESTAMP, "effective_until must follow effective_at"
                )


@dataclass(frozen=True, slots=True, kw_only=True)
class TemporalRecord(EffectivePeriod):
    published_at: datetime
    observed_at: datetime
    ingested_at: datetime
    validated_at: datetime
    usable_from: datetime
    superseded_at: datetime | None = None
    revision: int = 1

    def __post_init__(self) -> None:
        EffectivePeriod.__post_init__(self)
        for name in ("published_at", "observed_at", "ingested_at", "validated_at", "usable_from"):
            require_utc(getattr(self, name), name)
        if self.superseded_at is not None:
            require_utc(self.superseded_at, "superseded_at")
            if self.superseded_at < self.usable_from:
                raise DomainError(
                    ReasonCode.INVALID_TIMESTAMP, "superseded_at cannot precede usable_from"
                )
        if self.revision < 1:
            raise ValueError("revision must be positive")
        if self.usable_from < max(
            self.published_at, self.observed_at, self.ingested_at, self.validated_at
        ):
            raise DomainError(
                ReasonCode.INVALID_TIMESTAMP, "usable_from cannot precede evidence readiness"
            )


@dataclass(frozen=True, slots=True)
class Company(Contract):
    company_id: str
    legal_name: str
    display_name: str
    jurisdiction: str

    def __post_init__(self) -> None:
        if not all((self.company_id, self.legal_name, self.display_name, self.jurisdiction)):
            raise DomainError(
                ReasonCode.CRITICAL_FIELD_MISSING, "company identity fields are required"
            )


@dataclass(frozen=True, slots=True)
class Security(Contract):
    security_id: str
    company_id: str
    security_type: str
    currency: str


@dataclass(frozen=True, slots=True)
class ExchangeListing(EffectivePeriod):
    listing_id: str
    security_id: str
    exchange_id: str
    listed_at: datetime
    delisted_at: datetime | None = None

    def __post_init__(self) -> None:
        EffectivePeriod.__post_init__(self)
        require_utc(self.listed_at, "listed_at")
        if self.delisted_at is not None:
            require_utc(self.delisted_at, "delisted_at")
            if self.delisted_at <= self.listed_at:
                raise DomainError(ReasonCode.INVALID_TIMESTAMP, "delisted_at must follow listed_at")


@dataclass(frozen=True, slots=True)
class IdentifierHistory(TemporalRecord):
    security_id: str
    identifier_type: str
    identifier_value: str
    issuer: str


@dataclass(frozen=True, slots=True)
class ISINHistory(TemporalRecord):
    security_id: str
    isin: str


@dataclass(frozen=True, slots=True)
class SymbolHistory(TemporalRecord):
    listing_id: str
    symbol: str


@dataclass(frozen=True, slots=True)
class ClassificationHistory(TemporalRecord):
    company_id: str
    taxonomy: str
    sector: str
    industry: str


@dataclass(frozen=True, slots=True)
class IndexMembershipHistory(TemporalRecord):
    security_id: str
    index_id: str


@dataclass(frozen=True, slots=True)
class TradingCalendarSession(Contract):
    exchange_id: str
    session_date: date
    opens_at: datetime
    closes_at: datetime

    def __post_init__(self) -> None:
        require_utc(self.opens_at, "opens_at")
        require_utc(self.closes_at, "closes_at")
        if self.closes_at <= self.opens_at:
            raise DomainError(ReasonCode.INVALID_TIMESTAMP, "session close must follow open")


@dataclass(frozen=True, slots=True)
class EndOfDayPriceBar(TemporalRecord):
    listing_id: str
    session_date: date
    currency: str
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal
    is_adjusted: bool = False

    def __post_init__(self) -> None:
        TemporalRecord.__post_init__(self)
        if min(self.open, self.high, self.low, self.close) <= 0 or self.volume < 0:
            raise DomainError(
                ReasonCode.INVALID_PRICE_BAR, "prices must be positive and volume non-negative"
            )
        if (
            self.low > min(self.open, self.close)
            or self.high < max(self.open, self.close)
            or self.low > self.high
        ):
            raise DomainError(ReasonCode.INVALID_PRICE_BAR, "OHLC relationship is invalid")


@dataclass(frozen=True, slots=True)
class FinancialReportingPeriod(Contract):
    period_id: str
    company_id: str
    starts_on: date
    ends_on: date
    fiscal_year: int
    period_kind: str


@dataclass(frozen=True, slots=True)
class FinancialFiling(TemporalRecord):
    filing_id: str
    company_id: str
    period_id: str
    filing_kind: str
    source_record_id: str


@dataclass(frozen=True, slots=True)
class FinancialFact(TemporalRecord):
    fact_id: str
    filing_id: str
    metric: str
    value: Decimal
    unit: str
    currency: str | None = None


class CorporateActionType(StrEnum):
    CASH_DIVIDEND = "CASH_DIVIDEND"
    STOCK_SPLIT = "STOCK_SPLIT"
    BONUS_ISSUE = "BONUS_ISSUE"
    SYMBOL_CHANGE = "SYMBOL_CHANGE"
    DELISTING = "DELISTING"
    RIGHTS_ISSUE = "RIGHTS_ISSUE_UNSUPPORTED"
    MERGER = "MERGER_UNSUPPORTED"
    DEMERGER = "DEMERGER_UNSUPPORTED"


class CorporateActionStatus(StrEnum):
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    CONFLICTING = "CONFLICTING"


@dataclass(frozen=True, slots=True)
class CorporateAction(TemporalRecord):
    action_id: str
    security_id: str
    action_type: CorporateActionType
    idempotency_key: str
    status: CorporateActionStatus
    source_record_ids: tuple[str, ...]
    listing_id: str | None = None
    numerator: Decimal | None = None
    denominator: Decimal | None = None
    cash_amount: Decimal | None = None
    currency: str | None = None
    old_symbol: str | None = None
    new_symbol: str | None = None
    ex_date: date | None = None
    record_date: date | None = None
    payment_date: date | None = None

    def __post_init__(self) -> None:
        TemporalRecord.__post_init__(self)
        if (
            not all((self.action_id, self.security_id, self.idempotency_key))
            or not self.source_record_ids
        ):
            raise DomainError(
                ReasonCode.CRITICAL_FIELD_MISSING, "action identity and sources are required"
            )
        if self.action_type in (CorporateActionType.STOCK_SPLIT, CorporateActionType.BONUS_ISSUE):
            if (
                self.numerator is None
                or self.denominator is None
                or min(self.numerator, self.denominator) <= 0
            ):
                raise DomainError(
                    ReasonCode.UNSUPPORTED_CORPORATE_ACTION, "positive action ratio required"
                )
        if self.action_type is CorporateActionType.CASH_DIVIDEND and (
            self.cash_amount is None or self.cash_amount < 0
        ):
            raise DomainError(
                ReasonCode.UNSUPPORTED_CORPORATE_ACTION, "non-negative dividend required"
            )
        if self.action_type is CorporateActionType.SYMBOL_CHANGE and not all(
            (self.listing_id, self.old_symbol, self.new_symbol)
        ):
            raise DomainError(ReasonCode.CRITICAL_FIELD_MISSING, "symbol change terms required")
        if self.action_type is CorporateActionType.DELISTING and self.listing_id is None:
            raise DomainError(ReasonCode.CRITICAL_FIELD_MISSING, "delisting listing_id required")


@dataclass(frozen=True, slots=True)
class SourceRecord(TemporalRecord):
    source_record_id: str
    provider_name: str
    source_identifier: str
    raw_content_hash: str


@dataclass(frozen=True, slots=True)
class DataProvenance(Contract):
    source_record_id: str
    parser_version: str
    transformation_version: str
    evidence_reference: str


class ValidationStatus(StrEnum):
    VALID = "VALID"
    WARNING = "WARNING"
    INVALID = "INVALID"


@dataclass(frozen=True, slots=True)
class ValidationResult(Contract):
    record_id: str
    status: ValidationStatus
    reason_codes: tuple[ReasonCode, ...] = ()


@dataclass(frozen=True, slots=True)
class DatasetManifest(Contract):
    dataset_id: str
    created_at: datetime
    cutoff: datetime
    record_hashes: tuple[str, ...]
    rejected_count: int
    manifest_hash: str

    def __post_init__(self) -> None:
        require_utc(self.created_at, "created_at")
        require_utc(self.cutoff, "cutoff")


@dataclass(frozen=True, slots=True)
class AnalysisCutoff(Contract):
    decision_cutoff: datetime
    view: str

    def __post_init__(self) -> None:
        require_utc(self.decision_cutoff, "decision_cutoff")


class EligibilityStatus(StrEnum):
    ELIGIBLE_FOR_RESEARCH = "ELIGIBLE_FOR_RESEARCH"
    INELIGIBLE = "INELIGIBLE"
    DATA_BLOCKED = "DATA_BLOCKED"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


@dataclass(frozen=True, slots=True)
class AbstentionReason(Contract):
    code: ReasonCode
    detail: str


@dataclass(frozen=True, slots=True)
class ResearchEligibilityResult(Contract):
    security_id: str
    status: EligibilityStatus
    reasons: tuple[AbstentionReason, ...] = ()
