from dataclasses import replace
from datetime import timedelta
from decimal import Decimal
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from hypothesis import given
from hypothesis import strategies as st

from bharat_equity.application.corporate_actions import AdjustmentService
from bharat_equity.domain.errors import DomainError, ReasonCode
from bharat_equity.domain.models import PriceBasis
from bharat_equity.infrastructure.storage import AppliedActionLedger, ImmutableEvidenceStore
from bharat_equity.providers.synthetic import T2, SyntheticProvider

positive_decimals = st.decimals(
    min_value=Decimal("0.01"),
    max_value=Decimal("100000"),
    places=2,
    allow_nan=False,
    allow_infinity=False,
)
positive_integers = st.integers(min_value=1, max_value=1000)


def adjustment_service(root: Path) -> AdjustmentService:
    return AdjustmentService(
        AppliedActionLedger(root / "ledger"), ImmutableEvidenceStore(root / "results")
    )


@given(
    price=positive_decimals,
    quantity=positive_decimals,
    numerator=positive_integers,
    denominator=positive_integers,
)
def test_split_adjustment_preserves_economic_value(
    price: Decimal, quantity: Decimal, numerator: int, denominator: int
) -> None:
    action = replace(
        SyntheticProvider.split,
        numerator=Decimal(numerator),
        denominator=Decimal(denominator),
    )
    raw = replace(
        SyntheticProvider.price,
        open=price,
        high=price,
        low=price,
        close=price,
        volume=quantity,
    )
    with TemporaryDirectory() as directory:
        adjusted = adjustment_service(Path(directory)).adjust_bar(
            raw,
            action,
            SyntheticProvider.listing,
            source_series_id="SYNTHETIC-SOURCE",
            result_series_id="SYNTHETIC-SPLIT-RESULT",
            method_version="1",
            adjustment_cutoff=T2,
        )
    expected = raw.close * raw.volume
    actual = adjusted.close * adjusted.volume
    assert abs(expected - actual) <= abs(expected) * Decimal("1e-24") + Decimal("1e-18")


@given(
    price=positive_decimals,
    quantity=positive_decimals,
    bonus=positive_integers,
    held=positive_integers,
)
def test_bonus_adjustment_preserves_economic_value(
    price: Decimal, quantity: Decimal, bonus: int, held: int
) -> None:
    action = replace(
        SyntheticProvider.bonus,
        numerator=Decimal(bonus),
        denominator=Decimal(held),
    )
    raw = replace(
        SyntheticProvider.price,
        open=price,
        high=price,
        low=price,
        close=price,
        volume=quantity,
    )
    with TemporaryDirectory() as directory:
        adjusted = adjustment_service(Path(directory)).adjust_bar(
            raw,
            action,
            SyntheticProvider.listing,
            source_series_id="SYNTHETIC-SOURCE",
            result_series_id="SYNTHETIC-BONUS-RESULT",
            method_version="1",
            adjustment_cutoff=T2,
        )
    expected = raw.close * raw.volume
    actual = adjusted.close * adjusted.volume
    assert abs(expected - actual) <= abs(expected) * Decimal("1e-24") + Decimal("1e-18")


@pytest.mark.parametrize(
    ("offset", "changed"),
    [(-1, True), (0, False), (1, False)],
)
def test_action_effective_boundary(tmp_path, offset: int, changed: bool) -> None:
    raw = replace(SyntheticProvider.price, effective_at=T2 + timedelta(microseconds=offset))
    service = adjustment_service(tmp_path)
    adjusted = service.adjust_bar(
        raw,
        SyntheticProvider.bonus,
        SyntheticProvider.listing,
        source_series_id="SYNTHETIC-SOURCE-SERIES",
        result_series_id=f"SYNTHETIC-RESULT-{offset}",
        method_version="1",
        adjustment_cutoff=max(T2, raw.effective_at),
    )
    assert (adjusted.close != raw.close) is changed
    assert adjusted.price_basis is PriceBasis.BACK_ADJUSTED
    assert raw.price_basis is PriceBasis.RAW


def test_target_security_and_listing_mismatch_blocks(tmp_path) -> None:
    wrong_listing = replace(
        SyntheticProvider.listing,
        listing_id="SYNTHETIC-WRONG-LISTING",
        security_id="SYNTHETIC-SECURITY-B",
    )
    service = adjustment_service(tmp_path)
    with pytest.raises(DomainError) as error:
        service.adjust_series(
            (SyntheticProvider.price,),
            SyntheticProvider.bonus,
            wrong_listing,
            source_series_id="SYNTHETIC-SOURCE",
            result_series_id="SYNTHETIC-RESULT",
            method_version="1",
            adjustment_cutoff=T2,
        )
    assert error.value.code is ReasonCode.IDENTITY_CONFLICT


def test_duplicate_rejected_after_ledger_reload(tmp_path) -> None:
    kwargs = dict(
        bars=(SyntheticProvider.price,),
        action=SyntheticProvider.bonus,
        listing=SyntheticProvider.listing,
        source_series_id="SYNTHETIC-SOURCE",
        result_series_id="SYNTHETIC-RESULT",
        method_version="1",
        adjustment_cutoff=T2,
    )
    adjustment_service(tmp_path).adjust_series(**kwargs)
    kwargs["result_series_id"] = "SYNTHETIC-DIFFERENT-RESULT"
    kwargs["source_series_id"] = "SYNTHETIC-SOURCE-ALIAS"
    with pytest.raises(DomainError) as error:
        adjustment_service(tmp_path).adjust_series(**kwargs)
    assert error.value.code is ReasonCode.DUPLICATE_CORPORATE_ACTION


def test_revised_terms_same_logical_action_cannot_reapply(tmp_path) -> None:
    common = dict(
        bars=(SyntheticProvider.price,),
        listing=SyntheticProvider.listing,
        source_series_id="SYNTHETIC-SOURCE",
        method_version="1",
        adjustment_cutoff=T2,
    )
    first = adjustment_service(tmp_path).adjust_series(
        action=SyntheticProvider.bonus,
        result_series_id="SYNTHETIC-RESULT-A",
        **common,
    )
    assert ImmutableEvidenceStore(tmp_path / "results").get(first.result_evidence_hash)
    revised = replace(SyntheticProvider.bonus, numerator=Decimal("2"), revision=2)
    with pytest.raises(DomainError) as error:
        adjustment_service(tmp_path).adjust_series(
            action=revised,
            result_series_id="SYNTHETIC-RESULT-B",
            **common,
        )
    assert error.value.code is ReasonCode.DUPLICATE_CORPORATE_ACTION


def test_future_action_and_empty_series_fail_without_ledger_commit(tmp_path) -> None:
    service = adjustment_service(tmp_path)
    common = dict(
        action=SyntheticProvider.bonus,
        listing=SyntheticProvider.listing,
        source_series_id="SYNTHETIC-SOURCE",
        result_series_id="SYNTHETIC-RESULT",
        method_version="1",
    )
    with pytest.raises(DomainError) as future:
        service.adjust_series(
            (SyntheticProvider.price,), adjustment_cutoff=T2 - timedelta(microseconds=1), **common
        )
    assert future.value.code is ReasonCode.FUTURE_INFORMATION_REJECTED
    with pytest.raises(DomainError) as empty:
        service.adjust_series((), adjustment_cutoff=T2, **common)
    assert empty.value.code is ReasonCode.INSUFFICIENT_HISTORY
    assert not list((tmp_path / "ledger").rglob("*.json"))


def test_future_effective_action_is_rejected(tmp_path) -> None:
    future = replace(
        SyntheticProvider.bonus,
        effective_at=T2 + timedelta(days=10),
        usable_from=T2,
    )
    with pytest.raises(DomainError) as error:
        adjustment_service(tmp_path).adjust_series(
            (SyntheticProvider.price,),
            future,
            SyntheticProvider.listing,
            source_series_id="SYNTHETIC-SOURCE",
            result_series_id="SYNTHETIC-RESULT",
            method_version="1",
            adjustment_cutoff=T2,
        )
    assert error.value.code is ReasonCode.FUTURE_INFORMATION_REJECTED
