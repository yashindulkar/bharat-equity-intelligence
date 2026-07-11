from datetime import datetime
from decimal import Decimal

import pytest

from bharat_equity.domain.errors import DomainError, ReasonCode
from bharat_equity.domain.models import Company, EndOfDayPriceBar
from bharat_equity.providers.synthetic import T0, T1, SyntheticProvider


def test_company_requires_critical_identity() -> None:
    with pytest.raises(DomainError) as error:
        Company("", "SYNTHETIC", "SYNTHETIC", "SYNTHETIC")
    assert error.value.code is ReasonCode.CRITICAL_FIELD_MISSING


def test_naive_datetime_rejected() -> None:
    bar = SyntheticProvider.price
    with pytest.raises(DomainError) as error:
        EndOfDayPriceBar(
            **{
                **bar.to_dict(),
                "effective_at": datetime(2025, 1, 1),
                "published_at": T1,
                "observed_at": T1,
                "ingested_at": T1,
                "validated_at": T1,
                "usable_from": T1,
                "open": Decimal("1"),
                "high": Decimal("1"),
                "low": Decimal("1"),
                "close": Decimal("1"),
                "volume": Decimal("0"),
            }
        )
    assert error.value.code is ReasonCode.INVALID_TIMESTAMP


@pytest.mark.parametrize("values", [("10", "9", "8", "7", "1"), ("1", "2", "1", "1", "-1")])
def test_invalid_ohlc_or_volume_rejected(values: tuple[str, ...]) -> None:
    with pytest.raises(DomainError) as error:
        EndOfDayPriceBar(
            effective_at=T0,
            published_at=T1,
            observed_at=T1,
            ingested_at=T1,
            validated_at=T1,
            usable_from=T1,
            listing_id="SYNTHETIC",
            session_date=SyntheticProvider.price.session_date,
            currency="SYNTHETIC",
            open=Decimal(values[0]),
            high=Decimal(values[1]),
            low=Decimal(values[2]),
            close=Decimal(values[3]),
            volume=Decimal(values[4]),
        )
    assert error.value.code is ReasonCode.INVALID_PRICE_BAR
