from dataclasses import replace
from datetime import timedelta

from bharat_equity.domain.errors import ReasonCode
from bharat_equity.domain.intervals import (
    validate_classification_histories,
    validate_identifier_histories,
    validate_index_memberships,
    validate_isin_histories,
    validate_listing_intervals,
)
from bharat_equity.domain.models import (
    ClassificationHistory,
    IdentifierHistory,
    IndexMembershipHistory,
    ISINHistory,
)
from bharat_equity.providers.synthetic import T0, T1, SyntheticProvider


def fields() -> dict[str, object]:
    return {
        "effective_at": T0,
        "published_at": T1,
        "observed_at": T1,
        "ingested_at": T1,
        "validated_at": T1,
        "usable_from": T1,
    }


def test_all_identity_history_conflicts_are_structured() -> None:
    later = T0 + timedelta(days=1)
    isin = [
        ISINHistory(**fields(), security_id="SYNTHETIC-SEC", isin="SYNTHETIC-ISIN-A"),
        ISINHistory(
            **{**fields(), "effective_at": later},
            security_id="SYNTHETIC-SEC",
            isin="SYNTHETIC-ISIN-B",
        ),
    ]
    classifications = [
        ClassificationHistory(
            **fields(),
            company_id="SYNTHETIC-COMPANY",
            taxonomy="SYNTHETIC-TAX",
            sector="A",
            industry="A",
        ),
        ClassificationHistory(
            **{**fields(), "effective_at": later},
            company_id="SYNTHETIC-COMPANY",
            taxonomy="SYNTHETIC-TAX",
            sector="B",
            industry="B",
        ),
    ]
    memberships = [
        IndexMembershipHistory(**fields(), security_id="SYNTHETIC-SEC", index_id="SYNTHETIC-INDEX"),
        IndexMembershipHistory(
            **{**fields(), "effective_at": later},
            security_id="SYNTHETIC-SEC",
            index_id="SYNTHETIC-INDEX",
        ),
    ]
    identifiers = [
        IdentifierHistory(
            **fields(),
            security_id="SYNTHETIC-SEC-A",
            identifier_type="VENDOR",
            identifier_value="SYNTHETIC-ID",
            issuer="SYNTHETIC",
        ),
        IdentifierHistory(
            **{**fields(), "effective_at": later},
            security_id="SYNTHETIC-SEC-B",
            identifier_type="VENDOR",
            identifier_value="SYNTHETIC-ID",
            issuer="SYNTHETIC",
        ),
    ]
    for conflicts in (
        validate_isin_histories(isin),
        validate_classification_histories(classifications),
        validate_index_memberships(memberships),
        validate_identifier_histories(identifiers),
    ):
        assert conflicts and conflicts[0].code is ReasonCode.IDENTITY_CONFLICT


def test_listing_overlap_conflict_and_adjacent_relisting_allowed() -> None:
    conflicts = validate_listing_intervals(
        [
            SyntheticProvider.listing,
            replace(SyntheticProvider.listing, security_id="SYNTHETIC-OTHER-SECURITY"),
        ]
    )
    assert conflicts and conflicts[0].code is ReasonCode.IDENTITY_CONFLICT


def test_superseded_identity_correction_is_not_a_concurrent_conflict() -> None:
    correction_at = T1 + timedelta(days=1)
    original = ISINHistory(
        **fields(),
        security_id="SYNTHETIC-SEC",
        isin="SYNTHETIC-ISIN-A",
        superseded_at=correction_at,
    )
    corrected_fields = {
        **fields(),
        "published_at": correction_at,
        "observed_at": correction_at,
        "ingested_at": correction_at,
        "validated_at": correction_at,
        "usable_from": correction_at,
    }
    corrected = ISINHistory(
        **corrected_fields,
        security_id="SYNTHETIC-SEC",
        isin="SYNTHETIC-ISIN-B",
        revision=2,
    )
    assert not validate_isin_histories([original, corrected])
