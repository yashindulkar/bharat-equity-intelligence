from dataclasses import replace
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from bharat_equity.application.temporal import VintageView, is_effective, select_vintage
from bharat_equity.domain.errors import DomainError, ReasonCode
from bharat_equity.domain.models import (
    ClassificationHistory,
    FinancialFact,
    IndexMembershipHistory,
)
from bharat_equity.providers.synthetic import T0, T1, T2, SyntheticProvider


def test_future_filing_and_restatement_vintages() -> None:
    records = list(SyntheticProvider().fetch_fundamentals().records)
    june = datetime(2025, 6, 15, tzinfo=UTC)
    october = datetime(2025, 10, 1, tzinfo=UTC)
    assert select_vintage(
        records,
        business_at=june,
        cutoff=june,
        view=VintageView.AS_KNOWN_THEN,
    ).filing_id.endswith("V1")
    assert select_vintage(
        records,
        business_at=october,
        cutoff=october,
        view=VintageView.AS_KNOWN_THEN,
    ).filing_id.endswith("V2")
    assert select_vintage(
        records,
        business_at=june,
        cutoff=october,
        view=VintageView.LATEST_CORRECTED,
    ).filing_id.endswith("V2")


def test_supersession_boundary_is_exact() -> None:
    records = [SyntheticProvider.original_filing, SyntheticProvider.restated_filing]
    before = T2 - timedelta(microseconds=1)
    assert select_vintage(
        records, business_at=T0, cutoff=before, view=VintageView.AS_KNOWN_THEN
    ).filing_id.endswith("V1")
    assert select_vintage(
        records, business_at=T0, cutoff=T2, view=VintageView.AS_KNOWN_THEN
    ).filing_id.endswith("V2")


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
        select_vintage(
            [membership],
            business_at=T1,
            cutoff=T1,
            view=VintageView.AS_KNOWN_THEN,
        )
        is None
    )
    assert (
        select_vintage(
            [classification],
            business_at=T1,
            cutoff=T1,
            view=VintageView.AS_KNOWN_THEN,
        )
        is None
    )


def test_late_ingestion_and_after_close_do_not_leak() -> None:
    market_close = datetime(2025, 6, 2, 10, 0, tzinfo=UTC)  # 15:30 Asia/Kolkata
    published = market_close + timedelta(microseconds=1)
    ingested = market_close + timedelta(minutes=2)
    record = replace(
        SyntheticProvider.original_filing,
        published_at=published,
        observed_at=published,
        ingested_at=ingested,
        validated_at=ingested,
        usable_from=ingested,
        superseded_at=None,
    )
    assert (
        select_vintage(
            [record],
            business_at=T0,
            cutoff=market_close,
            view=VintageView.AS_KNOWN_THEN,
        )
        is None
    )
    assert (
        select_vintage([record], business_at=T0, cutoff=ingested, view=VintageView.AS_KNOWN_THEN)
        is record
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


def test_mixed_filing_chains_rejected() -> None:
    unrelated = replace(SyntheticProvider.restated_filing, version_chain_id="SYNTHETIC-OTHER-CHAIN")
    with pytest.raises(DomainError) as error:
        select_vintage(
            [SyntheticProvider.original_filing, unrelated],
            business_at=T1,
            cutoff=T2,
            view=VintageView.LATEST_CORRECTED,
        )
    assert error.value.code is ReasonCode.IDENTITY_CONFLICT


def test_reused_chain_across_company_or_period_is_rejected() -> None:
    unrelated = replace(SyntheticProvider.restated_filing, company_id="SYNTHETIC-OTHER-COMPANY")
    with pytest.raises(DomainError) as error:
        select_vintage(
            [SyntheticProvider.original_filing, unrelated],
            business_at=T0,
            cutoff=T2,
            view=VintageView.LATEST_CORRECTED,
        )
    assert error.value.code is ReasonCode.IDENTITY_CONFLICT


def test_mixed_financial_fact_metrics_rejected() -> None:
    fields = dict(
        effective_at=T0,
        published_at=T1,
        observed_at=T1,
        ingested_at=T1,
        validated_at=T1,
        usable_from=T1,
        version_chain_id="SYNTHETIC-FACT-CHAIN",
        filing_id="SYNTHETIC-FILING",
        company_id="SYNTHETIC-COMPANY",
        period_id="SYNTHETIC-PERIOD",
        reporting_scope="CONSOLIDATED",
        value=Decimal("1"),
        unit="SYNTHETIC-UNIT",
    )
    left = FinancialFact(**fields, fact_id="SYNTHETIC-FACT-A", metric="SYNTHETIC-A")
    right = FinancialFact(**fields, fact_id="SYNTHETIC-FACT-B", metric="SYNTHETIC-B")
    with pytest.raises(DomainError) as error:
        select_vintage([left, right], business_at=T0, cutoff=T1, view=VintageView.AS_KNOWN_THEN)
    assert error.value.code is ReasonCode.IDENTITY_CONFLICT


def test_reused_fact_chain_across_company_is_rejected() -> None:
    fields = dict(
        effective_at=T0,
        published_at=T1,
        observed_at=T1,
        ingested_at=T1,
        validated_at=T1,
        usable_from=T1,
        version_chain_id="SYNTHETIC-FACT-CHAIN",
        filing_id="SYNTHETIC-FILING",
        period_id="SYNTHETIC-PERIOD",
        reporting_scope="CONSOLIDATED",
        metric="SYNTHETIC-METRIC",
        value=Decimal("1"),
        unit="SYNTHETIC-UNIT",
    )
    left = FinancialFact(**fields, fact_id="SYNTHETIC-FACT-A", company_id="SYNTHETIC-A")
    right = FinancialFact(**fields, fact_id="SYNTHETIC-FACT-B", company_id="SYNTHETIC-B")
    with pytest.raises(DomainError) as error:
        select_vintage([left, right], business_at=T0, cutoff=T1, view=VintageView.AS_KNOWN_THEN)
    assert error.value.code is ReasonCode.IDENTITY_CONFLICT
