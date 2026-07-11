"""Limited, explicitly non-production corporate-action transformations."""

from __future__ import annotations

from dataclasses import dataclass, replace
from decimal import Decimal

from bharat_equity.domain.errors import DomainError, ReasonCode
from bharat_equity.domain.models import (
    CorporateAction,
    CorporateActionStatus,
    CorporateActionType,
    EndOfDayPriceBar,
)


class AdjustmentLedger:
    def __init__(self) -> None:
        self._keys: set[str] = set()

    def adjust(
        self,
        bar: EndOfDayPriceBar,
        action: CorporateAction,
        *,
        series_id: str = "SYNTHETIC_RAW",
        method_version: str = "1",
    ) -> EndOfDayPriceBar:
        ledger_key = f"{action.idempotency_key}|{series_id}|{method_version}"
        if ledger_key in self._keys:
            raise DomainError(ReasonCode.DUPLICATE_CORPORATE_ACTION, "action already applied")
        if action.status is not CorporateActionStatus.CONFIRMED:
            raise DomainError(ReasonCode.PROVIDER_CONFLICT, "action is not confirmed")
        if action.action_type not in (
            CorporateActionType.STOCK_SPLIT,
            CorporateActionType.BONUS_ISSUE,
        ):
            raise DomainError(
                ReasonCode.UNSUPPORTED_CORPORATE_ACTION, "action is not multiplicative"
            )
        assert action.numerator is not None and action.denominator is not None
        share_factor = (
            action.numerator / action.denominator
            if action.action_type is CorporateActionType.STOCK_SPLIT
            else (action.numerator + action.denominator) / action.denominator
        )
        self._keys.add(ledger_key)
        return replace(
            bar,
            open=bar.open / share_factor,
            high=bar.high / share_factor,
            low=bar.low / share_factor,
            close=bar.close / share_factor,
            volume=bar.volume * share_factor,
            is_adjusted=True,
        )

    def adjust_series(
        self,
        bars: tuple[EndOfDayPriceBar, ...],
        action: CorporateAction,
        *,
        listing_id: str,
        series_id: str,
        method_version: str = "1",
    ) -> AdjustedSeries:
        if any(bar.is_adjusted or bar.listing_id != listing_id for bar in bars):
            raise DomainError(ReasonCode.IDENTITY_CONFLICT, "series must contain matching raw bars")
        ledger_key = f"{action.idempotency_key}|{series_id}|{method_version}"
        if ledger_key in self._keys:
            raise DomainError(
                ReasonCode.DUPLICATE_CORPORATE_ACTION, "series action already applied"
            )
        if action.status is not CorporateActionStatus.CONFIRMED:
            raise DomainError(ReasonCode.PROVIDER_CONFLICT, "action is not confirmed")
        if action.action_type not in (
            CorporateActionType.STOCK_SPLIT,
            CorporateActionType.BONUS_ISSUE,
        ):
            raise DomainError(
                ReasonCode.UNSUPPORTED_CORPORATE_ACTION, "action is not multiplicative"
            )
        assert action.numerator is not None and action.denominator is not None
        factor = (
            action.numerator / action.denominator
            if action.action_type is CorporateActionType.STOCK_SPLIT
            else (action.numerator + action.denominator) / action.denominator
        )
        adjusted = tuple(
            replace(
                bar,
                open=bar.open / factor,
                high=bar.high / factor,
                low=bar.low / factor,
                close=bar.close / factor,
                volume=bar.volume * factor,
                is_adjusted=True,
            )
            if bar.effective_at < action.effective_at
            else bar
            for bar in bars
        )
        self._keys.add(ledger_key)
        return AdjustedSeries(series_id, method_version, (action.action_id,), factor, adjusted)


@dataclass(frozen=True, slots=True)
class AdjustedSeries:
    series_id: str
    method_version: str
    applied_action_ids: tuple[str, ...]
    share_factor: Decimal
    bars: tuple[EndOfDayPriceBar, ...]


def preserves_value(price: Decimal, quantity: Decimal, share_factor: Decimal) -> bool:
    return price * quantity == (price / share_factor) * (quantity * share_factor)
