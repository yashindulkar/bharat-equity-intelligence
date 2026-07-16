from datetime import UTC, datetime, timedelta

import pytest
from hypothesis import given
from hypothesis import strategies as st

from bharat_equity.domain.provider_policy import (
    CAPABILITY_NAMES,
    CapabilityState,
    DataDomain,
    EvidenceReference,
    GapResolutionStatus,
    GapSeverity,
    HistoryGap,
    ProviderCapabilityRegistry,
)

EVIDENCE = EvidenceReference("SYNTHETIC-EVIDENCE", "SYNTHETIC-1")


@given(
    start_offset=st.integers(min_value=0, max_value=3650),
    width=st.integers(min_value=0, max_value=3650),
)
@pytest.mark.property
def test_generated_history_gap_intervals_accept_ordered_bounds(
    start_offset: int,
    width: int,
) -> None:
    base = datetime(2000, 1, 1, tzinfo=UTC)
    starts_at = base + timedelta(days=start_offset)
    gap = HistoryGap(
        DataDomain.EOD_MARKET_DATA,
        starts_at,
        starts_at + timedelta(days=width),
        "NSE",
        ("SYNTHETIC-SECURITY",),
        None,
        GapSeverity.CRITICAL,
        EVIDENCE,
        GapResolutionStatus.OPEN,
    )
    assert gap.starts_at <= gap.ends_at


@given(
    start_offset=st.integers(min_value=1, max_value=3650),
    end_offset=st.integers(min_value=1, max_value=3650),
)
@pytest.mark.property
def test_generated_invalid_history_intervals_fail(
    start_offset: int,
    end_offset: int,
) -> None:
    base = datetime(2000, 1, 1, tzinfo=UTC)
    later = base + timedelta(days=max(start_offset, end_offset))
    earlier = base + timedelta(days=min(start_offset, end_offset) - 1)
    with pytest.raises(ValueError, match="historical_end"):
        ProviderCapabilityRegistry(
            provider_id="SYNTHETIC-PROVIDER",
            product="SYNTHETIC-PRODUCT",
            version="SYNTHETIC-1",
            capabilities={name: CapabilityState.UNKNOWN for name in CAPABILITY_NAMES},
            historical_start=later,
            historical_end=earlier,
            history_gaps=(),
            capability_evidence={name: () for name in CAPABILITY_NAMES},
        )
