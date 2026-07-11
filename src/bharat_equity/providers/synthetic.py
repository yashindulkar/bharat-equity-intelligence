"""Deterministic impossible synthetic Indian-equity-style records; never production data."""
# mypy: disable-error-code="arg-type"

from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal

from bharat_equity.domain.models import (
    Company,
    CorporateAction,
    CorporateActionStatus,
    CorporateActionType,
    EndOfDayPriceBar,
    FinancialFiling,
    ValidationStatus,
)
from bharat_equity.infrastructure.storage import content_hash

from .ports import ProviderResult

T0 = datetime(2025, 1, 1, tzinfo=UTC)
T1 = datetime(2025, 6, 1, tzinfo=UTC)
T2 = datetime(2025, 9, 1, tzinfo=UTC)


def _temporal(
    *,
    effective_at: datetime = T0,
    usable_from: datetime = T1,
    revision: int = 1,
    superseded_at: datetime | None = None,
) -> dict[str, object]:
    return {
        "effective_at": effective_at,
        "published_at": usable_from,
        "observed_at": usable_from,
        "ingested_at": usable_from,
        "validated_at": usable_from,
        "usable_from": usable_from,
        "revision": revision,
        "superseded_at": superseded_at,
    }


class SyntheticProvider:
    """Fixtures cover normal, symbol-change, delisting, split, bonus and restatement cases."""

    companies = (
        Company(
            "SYNTHETIC-COMPLETE-ENTITY",
            "Impossible Nebula Gears SYNTHETIC Limited",
            "SYNTHETIC Nebula",
            "SYNTHETIC-IN",
        ),
        Company(
            "SYNTHETIC-RENAME-ENTITY",
            "Impossible Rename Quasar SYNTHETIC Limited",
            "SYNTHETIC Rename",
            "SYNTHETIC-IN",
        ),
        Company(
            "SYNTHETIC-DELIST-ENTITY",
            "Impossible Delisted Comet SYNTHETIC Limited",
            "SYNTHETIC Delisted",
            "SYNTHETIC-IN",
        ),
        Company(
            "SYNTHETIC-FINANCE-ENTITY",
            "Impossible Finance Void SYNTHETIC Limited",
            "SYNTHETIC Finance",
            "SYNTHETIC-IN",
        ),
    )
    price = EndOfDayPriceBar(
        **_temporal(),
        listing_id="SYNTHETIC-LISTING-1",
        session_date=date(2025, 5, 30),
        currency="SYNTHETIC-INR",
        open=Decimal("100"),
        high=Decimal("110"),
        low=Decimal("95"),
        close=Decimal("108"),
        volume=Decimal("1000"),
    )
    split = CorporateAction(
        **_temporal(usable_from=T2),
        action_id="SYNTHETIC-ACTION-SPLIT",
        security_id="SYNTHETIC-SECURITY-SPLIT",
        action_type=CorporateActionType.STOCK_SPLIT,
        idempotency_key="SYNTHETIC-SPLIT-1-TO-10",
        status=CorporateActionStatus.CONFIRMED,
        source_record_ids=("SYNTHETIC-SOURCE-SPLIT",),
        numerator=Decimal("10"),
        denominator=Decimal("1"),
    )
    bonus = CorporateAction(
        **_temporal(usable_from=T2),
        action_id="SYNTHETIC-ACTION-BONUS",
        security_id="SYNTHETIC-SECURITY-BONUS",
        action_type=CorporateActionType.BONUS_ISSUE,
        idempotency_key="SYNTHETIC-BONUS-1-FOR-1",
        status=CorporateActionStatus.CONFIRMED,
        source_record_ids=("SYNTHETIC-SOURCE-BONUS",),
        numerator=Decimal("1"),
        denominator=Decimal("1"),
    )
    original_filing = FinancialFiling(
        **_temporal(usable_from=T1, superseded_at=T2),
        filing_id="SYNTHETIC-FILING-V1",
        company_id="SYNTHETIC-COMPLETE-ENTITY",
        period_id="SYNTHETIC-PERIOD-2025",
        filing_kind="SYNTHETIC_ANNUAL",
        source_record_id="SYNTHETIC-SOURCE-FILING-V1",
    )
    restated_filing = FinancialFiling(
        **_temporal(usable_from=T2, revision=2),
        filing_id="SYNTHETIC-FILING-V2",
        company_id="SYNTHETIC-COMPLETE-ENTITY",
        period_id="SYNTHETIC-PERIOD-2025",
        filing_kind="SYNTHETIC_ANNUAL_RESTATED",
        source_record_id="SYNTHETIC-SOURCE-FILING-V2",
    )

    def _result(
        self, name: str, records: tuple[object, ...], published: datetime | None = T1
    ) -> ProviderResult:
        digest = content_hash([repr(record) for record in records])
        return ProviderResult(
            "SYNTHETIC_PROVIDER_DO_NOT_USE_LIVE",
            f"SYNTHETIC-{name}",
            T2,
            published,
            "1.0.0",
            digest,
            ValidationStatus.VALID,
            records,
        )

    def fetch_security_master(self) -> ProviderResult:
        return self._result("SECURITY-MASTER", self.companies)

    def fetch_prices(self) -> ProviderResult:
        return self._result("PRICES", (self.price,))

    def fetch_corporate_actions(self) -> ProviderResult:
        return self._result("ACTIONS", (self.split, self.bonus, self.split))

    def fetch_fundamentals(self) -> ProviderResult:
        return self._result("FUNDAMENTALS", (self.original_filing, self.restated_filing))

    def fetch_index_constituents(self) -> ProviderResult:
        return self._result("INDEX", ())

    def fetch_market_calendar(self) -> ProviderResult:
        return self._result("CALENDAR", ())
