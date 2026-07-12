"""Synthetic-only, identity-safe backward corporate-action adjustments."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime
from decimal import Decimal

from bharat_equity.domain.errors import DomainError, ReasonCode
from bharat_equity.domain.models import (
    CorporateAction,
    CorporateActionStatus,
    CorporateActionType,
    EndOfDayPriceBar,
    ExchangeListing,
    PriceBasis,
    require_text,
    require_utc,
)
from bharat_equity.infrastructure.storage import (
    AppliedActionLedger,
    ImmutableEvidenceStore,
    content_hash,
)


def canonical_action_identity(action: CorporateAction) -> str:
    return content_hash(
        {
            "action_id": action.action_id,
            "security_id": action.security_id,
            "listing_id": action.listing_id,
            "action_type": action.action_type.value,
            "effective_at": action.effective_at.isoformat(),
        }
    )


def _share_factor(action: CorporateAction) -> Decimal:
    if action.status is not CorporateActionStatus.CONFIRMED:
        raise DomainError(ReasonCode.PROVIDER_CONFLICT, "action is not confirmed")
    if action.action_type not in (CorporateActionType.STOCK_SPLIT, CorporateActionType.BONUS_ISSUE):
        raise DomainError(ReasonCode.UNSUPPORTED_CORPORATE_ACTION, "action is not multiplicative")
    assert action.numerator is not None and action.denominator is not None
    if action.action_type is CorporateActionType.STOCK_SPLIT:
        return action.numerator / action.denominator  # post-action shares / pre-action shares
    return (action.denominator + action.numerator) / action.denominator  # held + bonus / held


def _validate_target(
    bars: tuple[EndOfDayPriceBar, ...], action: CorporateAction, listing: ExchangeListing
) -> None:
    if (
        action.listing_id is None
        or action.listing_id != listing.listing_id
        or action.security_id != listing.security_id
        or any(bar.listing_id != listing.listing_id for bar in bars)
        or any(bar.price_basis is not PriceBasis.RAW for bar in bars)
    ):
        raise DomainError(
            ReasonCode.IDENTITY_CONFLICT,
            "action, listing, security, series and raw bars must identify one target",
        )


@dataclass(frozen=True, slots=True)
class AdjustedSeries:
    series_id: str
    source_series_id: str
    listing_id: str
    security_id: str
    method_version: str
    adjustment_cutoff: datetime
    applied_action_ids: tuple[str, ...]
    resulting_price_basis: PriceBasis
    source_series_content_hash: str
    result_evidence_hash: str
    share_factor: Decimal
    bars: tuple[EndOfDayPriceBar, ...]


class AdjustmentService:
    def __init__(self, ledger: AppliedActionLedger, result_store: ImmutableEvidenceStore) -> None:
        self.ledger = ledger
        self.result_store = result_store

    def adjust_series(
        self,
        bars: tuple[EndOfDayPriceBar, ...],
        action: CorporateAction,
        listing: ExchangeListing,
        *,
        source_series_id: str,
        result_series_id: str,
        method_version: str,
        adjustment_cutoff: datetime,
    ) -> AdjustedSeries:
        for name, value in (
            ("source_series_id", source_series_id),
            ("result_series_id", result_series_id),
            ("method_version", method_version),
        ):
            require_text(value, name)
        require_utc(adjustment_cutoff, "adjustment_cutoff")
        _validate_target(bars, action, listing)
        if not bars:
            raise DomainError(ReasonCode.INSUFFICIENT_HISTORY, "cannot adjust an empty series")
        if action.usable_from > adjustment_cutoff:
            raise DomainError(
                ReasonCode.FUTURE_INFORMATION_REJECTED,
                "action was not usable by the adjustment cutoff",
            )
        if action.effective_at > adjustment_cutoff:
            raise DomainError(
                ReasonCode.FUTURE_INFORMATION_REJECTED,
                "action is not yet effective at the adjustment cutoff",
            )
        if not (
            listing.effective_at <= action.effective_at
            and (listing.effective_until is None or action.effective_at < listing.effective_until)
        ):
            raise DomainError(ReasonCode.IDENTITY_CONFLICT, "action is outside listing interval")
        if any(
            bar.effective_at < listing.effective_at
            or (listing.effective_until is not None and bar.effective_at >= listing.effective_until)
            for bar in bars
        ):
            raise DomainError(ReasonCode.IDENTITY_CONFLICT, "bar is outside listing interval")
        if any(bar.effective_at > adjustment_cutoff for bar in bars):
            raise DomainError(
                ReasonCode.FUTURE_INFORMATION_REJECTED,
                "bar is later than the adjustment cutoff",
            )
        factor = _share_factor(action)
        adjusted = tuple(
            replace(
                bar,
                open=bar.open / factor,
                high=bar.high / factor,
                low=bar.low / factor,
                close=bar.close / factor,
                volume=bar.volume * factor,
                price_basis=PriceBasis.BACK_ADJUSTED,
            )
            if bar.effective_at < action.effective_at
            else replace(bar, price_basis=PriceBasis.BACK_ADJUSTED)
            for bar in bars
        )
        source_series_content_hash = content_hash(
            {
                "listing_id": listing.listing_id,
                "security_id": listing.security_id,
                "bars": [bar.to_dict() for bar in bars],
            }
        )
        result_payload = {
            "source_series_content_hash": source_series_content_hash,
            "result_series_id": result_series_id,
            "method_version": method_version,
            "adjustment_cutoff": adjustment_cutoff.isoformat(),
            "action_id": action.action_id,
            "price_basis": PriceBasis.BACK_ADJUSTED.value,
            "bars": [bar.to_dict() for bar in adjusted],
        }
        result_evidence_hash = self.result_store.put(result_payload)
        self.ledger.record(
            canonical_action_identity(action),
            source_series_content_hash,
            method_version,
            result_evidence_hash,
        )
        return AdjustedSeries(
            result_series_id,
            source_series_id,
            listing.listing_id,
            listing.security_id,
            method_version,
            adjustment_cutoff,
            (action.action_id,),
            PriceBasis.BACK_ADJUSTED,
            source_series_content_hash,
            result_evidence_hash,
            factor,
            adjusted,
        )

    def adjust_bar(
        self,
        bar: EndOfDayPriceBar,
        action: CorporateAction,
        listing: ExchangeListing,
        *,
        source_series_id: str,
        result_series_id: str,
        method_version: str,
        adjustment_cutoff: datetime,
    ) -> EndOfDayPriceBar:
        return self.adjust_series(
            (bar,),
            action,
            listing,
            source_series_id=source_series_id,
            result_series_id=result_series_id,
            method_version=method_version,
            adjustment_cutoff=adjustment_cutoff,
        ).bars[0]


def preserves_value(price: Decimal, quantity: Decimal, share_factor: Decimal) -> bool:
    return price * quantity == (price / share_factor) * (quantity * share_factor)
