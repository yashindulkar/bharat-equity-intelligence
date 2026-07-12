from dataclasses import replace
from datetime import UTC, date, datetime
from decimal import Decimal

import pytest
from hypothesis import given
from hypothesis import strategies as st

from bharat_equity.domain.errors import DomainError, ReasonCode
from bharat_equity.domain.models import (
    AnalysisCutoff,
    ClassificationHistory,
    DataProvenance,
    DatasetManifest,
    FinancialFact,
    FinancialReportingPeriod,
    IdentifierHistory,
    IndexMembershipHistory,
    ISINHistory,
    Security,
    SourceRecord,
    SymbolHistory,
)
from bharat_equity.providers.synthetic import T0, T1, SyntheticProvider


def temporal() -> dict[str, object]:
    return {
        "effective_at": T0,
        "published_at": T1,
        "observed_at": T1,
        "ingested_at": T1,
        "validated_at": T1,
        "usable_from": T1,
    }


@pytest.mark.parametrize(
    "factory",
    [
        lambda: Security(" ", "SYNTHETIC-COMPANY", "EQUITY", "SYNTHETIC-INR"),
        lambda: replace(SyntheticProvider.listing, listing_id="   "),
        lambda: IdentifierHistory(
            **temporal(),
            security_id=" ",
            identifier_type="SYNTHETIC",
            identifier_value="X",
            issuer="SYNTHETIC",
        ),
        lambda: ISINHistory(**temporal(), security_id="SYNTHETIC", isin=" "),
        lambda: SymbolHistory(**temporal(), listing_id="SYNTHETIC", symbol=" "),
        lambda: ClassificationHistory(
            **temporal(), company_id="SYNTHETIC", taxonomy=" ", sector="S", industry="I"
        ),
        lambda: IndexMembershipHistory(**temporal(), security_id="SYNTHETIC", index_id=" "),
        lambda: FinancialReportingPeriod(
            " ", "SYNTHETIC", date(2025, 1, 1), date(2025, 12, 31), 2025, "ANNUAL"
        ),
        lambda: replace(SyntheticProvider.original_filing, version_chain_id=" "),
        lambda: FinancialFact(
            **temporal(),
            fact_id="SYNTHETIC-FACT",
            version_chain_id=" ",
            filing_id="SYNTHETIC-FILING",
            company_id="SYNTHETIC-COMPANY",
            period_id="SYNTHETIC-PERIOD",
            reporting_scope="CONSOLIDATED",
            metric="M",
            value=Decimal("1"),
            unit="U",
        ),
        lambda: SourceRecord(
            **temporal(),
            source_record_id=" ",
            provider_name="SYNTHETIC",
            source_identifier="SYNTHETIC",
            raw_content_hash="sha256:" + "a" * 64,
        ),
        lambda: DataProvenance(" ", "1", "1", "SYNTHETIC"),
        lambda: DatasetManifest(" ", T1, T1, (), 0, 0, 0, 0, (), "sha256:" + "a" * 64),
        lambda: AnalysisCutoff(T1, " "),
    ],
)
def test_whitespace_only_required_fields_rejected(factory) -> None:
    with pytest.raises(DomainError) as error:
        factory()
    assert error.value.code in {
        ReasonCode.CRITICAL_FIELD_MISSING,
        ReasonCode.IDENTITY_CONFLICT,
    }


def test_reporting_period_order_and_listing_consistency() -> None:
    with pytest.raises(DomainError):
        FinancialReportingPeriod(
            "SYNTHETIC", "SYNTHETIC", date(2025, 12, 31), date(2025, 1, 1), 2025, "ANNUAL"
        )
    with pytest.raises(DomainError) as error:
        replace(SyntheticProvider.listing, effective_at=datetime(2024, 1, 1, tzinfo=UTC))
    assert error.value.code is ReasonCode.IDENTITY_CONFLICT


@given(st.sampled_from(["NaN", "Infinity", "-Infinity"]))
def test_non_finite_price_and_fact_rejected(value: str) -> None:
    invalid = Decimal(value)
    with pytest.raises(DomainError):
        replace(SyntheticProvider.price, close=invalid)
    with pytest.raises(DomainError):
        FinancialFact(
            **temporal(),
            fact_id="SYNTHETIC-FACT",
            version_chain_id="SYNTHETIC-CHAIN",
            filing_id="SYNTHETIC-FILING",
            company_id="SYNTHETIC-COMPANY",
            period_id="SYNTHETIC-PERIOD",
            reporting_scope="CONSOLIDATED",
            metric="M",
            value=invalid,
            unit="U",
        )


def test_analysis_cutoff_rejects_unknown_view() -> None:
    with pytest.raises(DomainError):
        AnalysisCutoff(T1, "SYNTHETIC-UNKNOWN")


def test_non_finite_dividend_rejected_with_typed_error() -> None:
    with pytest.raises(DomainError) as error:
        replace(SyntheticProvider.dividend, cash_amount=Decimal("NaN"))
    assert error.value.code is ReasonCode.CRITICAL_FIELD_MISSING
