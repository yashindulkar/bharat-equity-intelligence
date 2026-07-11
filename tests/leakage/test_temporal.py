from datetime import UTC, datetime

import pytest

from bharat_equity.application.temporal import VintageView, is_effective, select_vintage
from bharat_equity.domain.errors import DomainError, ReasonCode
from bharat_equity.domain.models import ClassificationHistory, IndexMembershipHistory
from bharat_equity.providers.synthetic import T0, T1, T2, SyntheticProvider


def test_future_filing_and_restatement_vintages() -> None:
    records = list(SyntheticProvider().fetch_fundamentals().records)
    june = datetime(2025, 6, 15, tzinfo=UTC)
    october = datetime(2025, 10, 1, tzinfo=UTC)
    assert select_vintage(
        records, business_at=june, cutoff=june, view=VintageView.AS_KNOWN_THEN
    ).filing_id.endswith("V1")
    assert select_vintage(
        records, business_at=october, cutoff=october, view=VintageView.AS_KNOWN_THEN
    ).filing_id.endswith("V2")
    assert select_vintage(
        records, business_at=june, cutoff=june, view=VintageView.LATEST_CORRECTED
    ).filing_id.endswith("V1")


def test_effective_interval_is_half_open() -> None:
    record = SyntheticProvider.original_filing
    assert is_effective(record, record.effective_at)
    if record.effective_until is not None:
        assert not is_effective(record, record.effective_until)


def test_future_membership_and_classification_are_unavailable() -> None:
    fields = dict(
        effective_at=T2,
        published_at=T1,
        observed_at=T1,
        ingested_at=T1,
        validated_at=T1,
        usable_from=T1,
    )
    membership = IndexMembershipHistory(
        **fields, security_id="SYNTHETIC-SEC", index_id="SYNTHETIC-INDEX"
    )
    classification = ClassificationHistory(
        **fields,
        company_id="SYNTHETIC-COMPANY",
        taxonomy="SYNTHETIC-TAXONOMY",
        sector="SYNTHETIC-SECTOR",
        industry="SYNTHETIC-INDUSTRY",
    )
    assert (
        select_vintage([membership], business_at=T1, cutoff=T1, view=VintageView.AS_KNOWN_THEN)
        is None
    )
    assert (
        select_vintage([classification], business_at=T1, cutoff=T1, view=VintageView.AS_KNOWN_THEN)
        is None
    )


def test_late_ingestion_and_after_close_do_not_leak() -> None:
    record = SyntheticProvider.original_filing
    before = datetime(2025, 5, 31, 23, 59, tzinfo=UTC)
    assert (
        select_vintage([record], business_at=T0, cutoff=before, view=VintageView.AS_KNOWN_THEN)
        is None
    )


def test_naive_cutoff_is_rejected() -> None:
    with pytest.raises(DomainError) as error:
        select_vintage(
            [SyntheticProvider.original_filing],
            business_at=T0,
            cutoff=datetime(2025, 6, 1),
            view=VintageView.AS_KNOWN_THEN,
        )
    assert error.value.code is ReasonCode.INVALID_TIMESTAMP
