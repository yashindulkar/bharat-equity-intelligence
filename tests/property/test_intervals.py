from datetime import timedelta

from hypothesis import given, settings
from hypothesis import strategies as st

from bharat_equity.domain.intervals import (
    intervals_overlap,
    validate_classification_histories,
    validate_identifier_histories,
    validate_index_memberships,
    validate_isin_histories,
    validate_listing_intervals,
    validate_symbol_histories,
)
from bharat_equity.domain.models import (
    ClassificationHistory,
    IdentifierHistory,
    IndexMembershipHistory,
    ISINHistory,
    SymbolHistory,
)
from bharat_equity.providers.synthetic import T0, T1, SyntheticProvider


def symbol(start, end, value="SYNTHETIC-SYMBOL") -> SymbolHistory:
    readiness = min(start, T1)
    return SymbolHistory(
        effective_at=start,
        effective_until=end,
        published_at=readiness,
        observed_at=readiness,
        ingested_at=readiness,
        validated_at=readiness,
        usable_from=readiness,
        listing_id="SYNTHETIC-LISTING",
        symbol=value,
    )


@settings(max_examples=40, derandomize=True)
@given(length=st.integers(min_value=1, max_value=1000))
def test_half_open_adjacent_intervals_do_not_overlap(length: int) -> None:
    boundary = T0 + timedelta(seconds=length)
    assert not intervals_overlap(symbol(T0, boundary), symbol(boundary, None))


@settings(max_examples=40, derandomize=True)
@given(offset=st.integers(min_value=1, max_value=999))
def test_overlapping_symbol_histories_are_conflicts(offset: int) -> None:
    end = T0 + timedelta(seconds=1000)
    left = symbol(T0, end, "SYNTHETIC-A")
    right = symbol(T0 + timedelta(seconds=offset), None, "SYNTHETIC-B")
    assert validate_symbol_histories([left, right])


@settings(max_examples=40, derandomize=True)
@given(offset=st.integers(min_value=1, max_value=999))
def test_all_history_validator_families_detect_generated_overlaps(offset: int) -> None:
    later = T0 + timedelta(seconds=offset)
    base = dict(
        effective_at=T0,
        published_at=T1,
        observed_at=T1,
        ingested_at=T1,
        validated_at=T1,
        usable_from=T1,
    )
    shifted = {**base, "effective_at": later}
    assert validate_isin_histories(
        [
            ISINHistory(**base, security_id="SYNTHETIC-SEC", isin="SYNTHETIC-A"),
            ISINHistory(**shifted, security_id="SYNTHETIC-SEC", isin="SYNTHETIC-B"),
        ]
    )
    assert validate_classification_histories(
        [
            ClassificationHistory(
                **base,
                company_id="SYNTHETIC-COMPANY",
                taxonomy="SYNTHETIC-TAX",
                sector="A",
                industry="A",
            ),
            ClassificationHistory(
                **shifted,
                company_id="SYNTHETIC-COMPANY",
                taxonomy="SYNTHETIC-TAX",
                sector="B",
                industry="B",
            ),
        ]
    )
    assert validate_index_memberships(
        [
            IndexMembershipHistory(**base, security_id="SYNTHETIC-SEC", index_id="SYNTHETIC-INDEX"),
            IndexMembershipHistory(
                **shifted, security_id="SYNTHETIC-SEC", index_id="SYNTHETIC-INDEX"
            ),
        ]
    )
    assert validate_identifier_histories(
        [
            IdentifierHistory(
                **base,
                security_id="SYNTHETIC-A",
                identifier_type="VENDOR",
                identifier_value="SYNTHETIC-ID",
                issuer="SYNTHETIC",
            ),
            IdentifierHistory(
                **shifted,
                security_id="SYNTHETIC-B",
                identifier_type="VENDOR",
                identifier_value="SYNTHETIC-ID",
                issuer="SYNTHETIC",
            ),
        ]
    )
    later_listing = SyntheticProvider.listing.__class__(
        SyntheticProvider.listing.listing_id,
        "SYNTHETIC-OTHER-SECURITY",
        SyntheticProvider.listing.exchange_id,
        later,
        effective_at=later,
    )
    assert validate_listing_intervals([SyntheticProvider.listing, later_listing])


def test_adjacent_listing_intervals_are_not_overlapping() -> None:
    boundary = T0 + timedelta(days=10)
    first = SyntheticProvider.listing.__class__(
        "SYNTHETIC-RELISTING",
        "SYNTHETIC-SECURITY-1",
        "SYNTHETIC-EXCHANGE",
        T0,
        boundary,
        effective_at=T0,
        effective_until=boundary,
    )
    second = SyntheticProvider.listing.__class__(
        "SYNTHETIC-RELISTING",
        "SYNTHETIC-SECURITY-1",
        "SYNTHETIC-EXCHANGE",
        boundary,
        effective_at=boundary,
    )
    assert not validate_listing_intervals([first, second])
