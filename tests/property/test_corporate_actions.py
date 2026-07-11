from decimal import Decimal

import pytest

from bharat_equity.application.corporate_actions import AdjustmentLedger, preserves_value
from bharat_equity.domain.errors import DomainError, ReasonCode
from bharat_equity.providers.synthetic import SyntheticProvider


@pytest.mark.parametrize(
    "price,quantity,factor", [("100", "7", "10"), ("99.5", "3", "2"), ("1", "1000", "1.5")]
)
def test_adjustment_preserves_economic_value(price: str, quantity: str, factor: str) -> None:
    assert preserves_value(Decimal(price), Decimal(quantity), Decimal(factor))


def test_bonus_is_deterministic_raw_unchanged_and_duplicate_blocked() -> None:
    raw = SyntheticProvider.price
    ledger = AdjustmentLedger()
    adjusted = ledger.adjust(raw, SyntheticProvider.bonus)
    assert (
        adjusted.close == Decimal("54")
        and adjusted.is_adjusted
        and raw.close == Decimal("108")
        and not raw.is_adjusted
    )
    with pytest.raises(DomainError) as error:
        ledger.adjust(raw, SyntheticProvider.bonus)
    assert error.value.code is ReasonCode.DUPLICATE_CORPORATE_ACTION
