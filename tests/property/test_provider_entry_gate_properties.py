import hashlib
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest
from hypothesis import given
from hypothesis import strategies as st

from bharat_equity.application.provider_evaluation import (
    DEFAULT_SCORECARD_VERSION,
    EvaluationRequest,
    deterministic_report,
    evaluate_hard_gates,
    history_gap_relevant,
    publication_gate,
    validate_provider_envelope,
)
from bharat_equity.domain.errors import ReasonCode
from bharat_equity.domain.provider_policy import (
    CAPABILITY_NAMES,
    ApprovalStatus,
    CapabilityState,
    CompetingValue,
    ConfidenceLevel,
    ConflictResolutionStatus,
    CorrectionRequirement,
    DataCategory,
    DataDomain,
    DataUsagePolicy,
    DeletionDisposition,
    DeletionEvidenceReference,
    DispositionState,
    EvidenceReference,
    GapResolutionStatus,
    GapSeverity,
    GeographyScope,
    HistoryGap,
    MembershipState,
    Permission,
    ProcessingGeographyGrant,
    ProviderCapabilityRegistry,
    ProviderResponseEnvelope,
    ProviderScorecard,
    PublicationStatus,
    ReconciliationConflict,
    RemediationAction,
    RemediationExecution,
    RemediationStatus,
    ScorecardEntry,
    ScoreDimension,
    TerminationDeletionLifecycle,
    TerminationLifecycleRegistry,
    UniverseMembershipEvidence,
    UsagePurpose,
    contract_snapshot_id,
)

BASE = datetime(2026, 1, 1, tzinfo=UTC)
HISTORY_START = datetime(2020, 1, 1, tzinfo=UTC)
LATEST_SESSION = datetime(2025, 12, 31, tzinfo=UTC)
EVIDENCE = EvidenceReference("SYNTHETIC-EVIDENCE", "SYNTHETIC-1", BASE - timedelta(days=1))


def base_policy(*, termination_at: datetime | None = None) -> DataUsagePolicy:
    termination = termination_at or BASE + timedelta(days=365)
    purposes = {purpose: Permission.PROHIBITED for purpose in UsagePurpose}
    purposes[UsagePurpose.PRIVATE_HOUSEHOLD_RESEARCH] = Permission.PERMITTED
    return DataUsagePolicy(
        policy_id="SYNTHETIC-POLICY",
        provider_id="SYNTHETIC-PROVIDER",
        product="SYNTHETIC-PRODUCT",
        agreement_version="SYNTHETIC-AGREEMENT-1",
        effective_from=BASE - timedelta(days=365),
        effective_until=termination,
        termination_event_id="SYNTHETIC-TERMINATION-1",
        termination_at=termination,
        early_termination_amendment=None,
        permitted_users=("SYNTHETIC-OPERATOR",),
        permitted_purposes=purposes,
        raw_retention=Permission.PERMITTED,
        derived_data=Permission.PROHIBITED,
        backtesting=Permission.PROHIBITED,
        model_training=Permission.PROHIBITED,
        display=Permission.PROHIBITED,
        citation=Permission.PROHIBITED,
        backup=Permission.PROHIBITED,
        fixtures=Permission.PROHIBITED,
        post_termination_raw_data=Permission.PROHIBITED,
        post_termination_backup=Permission.PROHIBITED,
        post_termination_fixtures=Permission.PROHIBITED,
        post_termination_derived_data=Permission.PROHIBITED,
        post_termination_audit_evidence=Permission.PROHIBITED,
        deletion_obligations="SYNTHETIC delete all categories",
        processing_geography=ProcessingGeographyGrant(
            GeographyScope.JURISDICTIONS,
            ("SYNTHETIC-JURISDICTION",),
            (EVIDENCE,),
        ),
        geographical_restrictions=(),
        evidence_references=(EVIDENCE,),
        reviewer="SYNTHETIC-REVIEWER",
        approved_at=BASE - timedelta(days=300),
        rejected_at=None,
        review_due_at=BASE + timedelta(days=300),
        external_ai_processing=Permission.PROHIBITED,
        approval_status=ApprovalStatus.APPROVED,
    )


def base_capabilities(*, gaps: tuple[HistoryGap, ...] = ()) -> ProviderCapabilityRegistry:
    return ProviderCapabilityRegistry(
        provider_id="SYNTHETIC-PROVIDER",
        product="SYNTHETIC-PRODUCT",
        version="SYNTHETIC-1",
        capabilities={name: CapabilityState.SUPPORTED for name in CAPABILITY_NAMES},
        historical_start=HISTORY_START,
        historical_end=LATEST_SESSION,
        history_gaps=gaps,
        capability_evidence={name: (EVIDENCE,) for name in CAPABILITY_NAMES},
    )


def base_request(*, at: datetime = BASE, **changes: object) -> EvaluationRequest:
    values: dict[str, object] = {
        "at": at,
        "purpose": UsagePurpose.PRIVATE_HOUSEHOLD_RESEARCH,
        "user": "SYNTHETIC-OPERATOR",
        "processing_geography": "SYNTHETIC-JURISDICTION",
        "required_history_start": HISTORY_START,
        "latest_required_session": LATEST_SESSION,
        "required_security_ids": ("SYNTHETIC-SECURITY",),
    }
    values.update(changes)
    return EvaluationRequest(**values)  # type: ignore[arg-type]


def weights_from_units(units: tuple[int, ...]) -> dict[ScoreDimension, Decimal]:
    return {
        dimension: Decimal(unit) / Decimal("10000")
        for dimension, unit in zip(ScoreDimension, units, strict=True)
    }


def base_scorecard(
    policy: DataUsagePolicy,
    *,
    at: datetime = BASE,
    evidence_at: datetime | None = None,
    raw_scores: tuple[Decimal, ...] | None = None,
    weights: dict[ScoreDimension, Decimal] | None = None,
) -> ProviderScorecard:
    evidence = EvidenceReference(
        "SYNTHETIC-SCORE-EVIDENCE",
        "SYNTHETIC-1",
        evidence_at or at,
    )
    selected_scores = raw_scores or tuple(Decimal("80") for _ in ScoreDimension)
    selected_weights = weights or {dimension: Decimal("0.125") for dimension in ScoreDimension}
    return ProviderScorecard(
        provider_id="SYNTHETIC-PROVIDER",
        product="SYNTHETIC-PRODUCT",
        product_version="SYNTHETIC-1",
        policy_id=policy.policy_id,
        agreement_version=policy.agreement_version,
        policy_snapshot_id=contract_snapshot_id(policy),
        scorecard_version=DEFAULT_SCORECARD_VERSION,
        methodology_version="SYNTHETIC-METHOD-1",
        assessed_at=at,
        evidence_references=(evidence,),
        entries=tuple(
            ScorecardEntry(
                dimension,
                raw_score,
                selected_weights[dimension],
                (evidence,),
                "SYNTHETIC-ASSESSOR",
                at,
                "SYNTHETIC-METHOD-1",
                "SYNTHETIC explanation",
                ConfidenceLevel.MEDIUM,
            )
            for dimension, raw_score in zip(ScoreDimension, selected_scores, strict=True)
        ),
    )


def empty_registry() -> TerminationLifecycleRegistry:
    return TerminationLifecycleRegistry("SYNTHETIC-REGISTRY-1", ())


def passing_artifact() -> tuple[
    ProviderCapabilityRegistry,
    DataUsagePolicy,
    TerminationLifecycleRegistry,
    EvaluationRequest,
    ProviderScorecard,
    object,
]:
    policy = base_policy()
    capabilities = base_capabilities()
    registry = empty_registry()
    request = base_request()
    scorecard = base_scorecard(policy)
    artifact = evaluate_hard_gates(capabilities, policy, registry, request, scorecard)
    return capabilities, policy, registry, request, scorecard, artifact


@given(
    left_start=st.integers(min_value=0, max_value=100),
    left_width=st.integers(min_value=0, max_value=100),
    right_start=st.integers(min_value=0, max_value=100),
    right_width=st.integers(min_value=0, max_value=100),
)
@pytest.mark.property
def test_closed_interval_gap_boundaries_match_mathematical_overlap(
    left_start: int,
    left_width: int,
    right_start: int,
    right_width: int,
) -> None:
    gap_start = BASE + timedelta(days=left_start)
    gap_end = gap_start + timedelta(days=left_width)
    request_start = BASE + timedelta(days=right_start)
    request_end = request_start + timedelta(days=right_width)
    gap = HistoryGap(
        DataDomain.EOD_MARKET_DATA,
        gap_start,
        gap_end,
        "NSE",
        ("SYNTHETIC-SECURITY",),
        None,
        GapSeverity.CRITICAL,
        EVIDENCE,
        GapResolutionStatus.OPEN,
    )
    request = base_request(
        required_history_start=request_start,
        latest_required_session=request_end,
        required_universe_scope=None,
    )
    expected = gap_start <= request_end and request_start <= gap_end
    assert history_gap_relevant(gap, request) is expected


@given(
    member_from=st.integers(min_value=0, max_value=20),
    member_until=st.integers(min_value=20, max_value=40),
)
@pytest.mark.property
def test_universe_gap_relevance_fails_closed_unless_nonmembership_covers_interval(
    member_from: int,
    member_until: int,
) -> None:
    gap_start = BASE
    gap_end = BASE + timedelta(days=30)
    gap = HistoryGap(
        DataDomain.EOD_MARKET_DATA,
        gap_start,
        gap_end,
        "NSE",
        (),
        "SYNTHETIC-UNIVERSE",
        GapSeverity.CRITICAL,
        EVIDENCE,
        GapResolutionStatus.OPEN,
    )
    record = UniverseMembershipEvidence(
        "SYNTHETIC-SECURITY",
        "SYNTHETIC-UNIVERSE",
        BASE + timedelta(days=member_from),
        BASE + timedelta(days=member_until),
        MembershipState.NON_MEMBER,
        EVIDENCE,
    )
    request = base_request(
        required_history_start=gap_start,
        latest_required_session=gap_end,
        required_universe_scope=None,
        universe_membership_evidence=(record,),
    )
    expected = not (member_from == 0 and member_until >= 30)
    assert history_gap_relevant(gap, request) is expected


@given(
    hours_after_termination=st.integers(min_value=0, max_value=72),
    deadline_hours=st.integers(min_value=0, max_value=48),
    category=st.sampled_from(tuple(DataCategory)),
)
@pytest.mark.property
def test_lifecycle_deadline_state_machine_is_category_independent(
    hours_after_termination: int,
    deadline_hours: int,
    category: DataCategory,
) -> None:
    termination = BASE
    at = termination + timedelta(hours=hours_after_termination)
    deadline = termination + timedelta(hours=deadline_hours)
    policy = base_policy(termination_at=termination)
    dispositions = []
    for item in DataCategory:
        state = DispositionState.COMPLETED
        if item is category:
            state = DispositionState.NOT_DUE
        completed = state is DispositionState.COMPLETED
        dispositions.append(
            DeletionDisposition(
                item,
                Permission.PROHIBITED,
                state,
                deadline,
                termination if completed else None,
                (DeletionEvidenceReference(item, EVIDENCE),) if completed else (),
                "SYNTHETIC-VERIFIER" if completed else None,
                "SYNTHETIC-1",
            )
        )
    lifecycle = TerminationDeletionLifecycle(
        "SYNTHETIC-LIFECYCLE",
        policy.provider_id,
        policy.product,
        policy.policy_id,
        policy.agreement_version,
        policy.termination_event_id or "",
        termination,
        tuple(dispositions),
        "SYNTHETIC-1",
    )
    registry = TerminationLifecycleRegistry("SYNTHETIC-REGISTRY-1", (lifecycle,))
    result = evaluate_hard_gates(
        base_capabilities(),
        policy,
        registry,
        base_request(at=at),
        base_scorecard(policy, at=min(at, BASE)),
    )
    if at > deadline:
        assert ReasonCode.TERMINATION_DELETION_OVERDUE in result.reasons
    else:
        assert ReasonCode.TERMINATION_DELETION_OVERDUE not in result.reasons


@given(category=st.sampled_from(tuple(DataCategory)))
@pytest.mark.property
def test_each_completed_deletion_category_requires_own_evidence(category: DataCategory) -> None:
    with pytest.raises(ValueError, match="category-specific"):
        DeletionDisposition(
            category,
            Permission.PROHIBITED,
            DispositionState.COMPLETED,
            BASE,
            BASE,
            (),
            "SYNTHETIC-VERIFIER",
            "SYNTHETIC-1",
        )


@given(
    score_units=st.tuples(*(st.integers(min_value=0, max_value=10000) for _ in ScoreDimension)),
    cut_points=st.lists(
        st.integers(min_value=0, max_value=10000),
        min_size=7,
        max_size=7,
        unique=True,
    ),
)
@pytest.mark.property
def test_decimal_scorecard_exact_totals_and_deterministic_rounding(
    score_units: tuple[int, ...],
    cut_points: list[int],
) -> None:
    policy = base_policy()
    scores = tuple(Decimal(value) / Decimal("100") for value in score_units)
    boundaries = (0, *sorted(cut_points), 10000)
    weight_units = tuple(right - left for left, right in zip(boundaries, boundaries[1:]))
    weights = weights_from_units(weight_units)
    candidate = base_scorecard(policy, raw_scores=scores, weights=weights)
    expected = sum(
        (
            score * weights[dimension]
            for score, dimension in zip(scores, ScoreDimension, strict=True)
        ),
        Decimal(),
    ).quantize(Decimal("0.01"))
    assert candidate.weighted_score() == expected
    assert candidate.weighted_score() == candidate.weighted_score()


@given(offset=st.integers(min_value=-48, max_value=48))
@pytest.mark.property
def test_scorecard_assessment_and_evidence_obey_evaluation_cutoff(offset: int) -> None:
    policy = base_policy()
    instant = BASE + timedelta(hours=offset)
    request = base_request()
    candidate = base_scorecard(policy, at=instant, evidence_at=instant)
    result = evaluate_hard_gates(base_capabilities(), policy, empty_registry(), request, candidate)
    if offset > 0:
        assert ReasonCode.SCORECARD_FUTURE_ASSESSMENT in result.reasons
        assert ReasonCode.SCORECARD_FUTURE_EVIDENCE in result.reasons
    else:
        assert result.passed


@given(payload=st.binary(min_size=1, max_size=128), index=st.integers(min_value=0, max_value=127))
@pytest.mark.property
def test_payload_single_byte_mutation_never_preserves_envelope_hash(
    payload: bytes, index: int
) -> None:
    selected = index % len(payload)
    mutated = payload[:selected] + bytes((payload[selected] ^ 1,)) + payload[selected + 1 :]
    policy = base_policy()
    envelope = ProviderResponseEnvelope(
        provider_id="SYNTHETIC-PROVIDER",
        product="SYNTHETIC-PRODUCT",
        product_version="SYNTHETIC-1",
        request_id="SYNTHETIC-REQUEST",
        source_record_id="SYNTHETIC-SOURCE",
        retrieved_at=BASE,
        published_at=BASE,
        payload_schema_version="SYNTHETIC-SCHEMA-1",
        content_type="application/octet-stream",
        immutable_payload_hash=f"sha256:{hashlib.sha256(payload).hexdigest()}",
        policy_id=policy.policy_id,
        agreement_version=policy.agreement_version,
        policy_snapshot_id=contract_snapshot_id(policy),
        intended_usage_purpose=UsagePurpose.PRIVATE_HOUSEHOLD_RESEARCH,
    )
    result = validate_provider_envelope(
        envelope,
        mutated,
        base_capabilities(),
        policy,
        base_request(),
        frozenset({"SYNTHETIC-SCHEMA-1"}),
    )
    assert ReasonCode.EVIDENCE_INTEGRITY_FAILURE in result.reasons


def remediation_execution(
    action: RemediationAction, status: RemediationStatus
) -> RemediationExecution:
    completed = status is RemediationStatus.COMPLETED
    return RemediationExecution(
        action,
        status,
        BASE if completed else None,
        (EVIDENCE,) if completed else (),
        "SYNTHETIC-VERIFIER" if completed else None,
    )


def generated_conflict(kind: str, identifier: int) -> ReconciliationConflict:
    if kind == "rejected":
        resolution = ConflictResolutionStatus.INVALID_NON_REMEDIABLE
        severity = GapSeverity.CRITICAL
        requirement = CorrectionRequirement.NONE
        remediation = RemediationStatus.NOT_REQUIRED
    elif kind == "quarantined":
        resolution = ConflictResolutionStatus.RESOLVED_APPROVED
        severity = GapSeverity.CRITICAL
        requirement = CorrectionRequirement.CORRECTION_REQUIRED
        remediation = RemediationStatus.PENDING
    else:
        resolution = ConflictResolutionStatus.UNRESOLVED
        severity = GapSeverity.WARNING
        requirement = CorrectionRequirement.CORRECTION_REQUIRED
        remediation = RemediationStatus.PENDING
    reviewed = resolution is not ConflictResolutionStatus.UNRESOLVED
    return ReconciliationConflict(
        f"SYNTHETIC-CONFLICT-{identifier}",
        "close",
        (
            CompetingValue("SYNTHETIC-A", "1", "raw", EVIDENCE, ConfidenceLevel.HIGH),
            CompetingValue("SYNTHETIC-B", "2", "raw", EVIDENCE, ConfidenceLevel.MEDIUM),
        ),
        "SYNTHETIC-TOLERANCE",
        "SYNTHETIC-1",
        "1",
        severity,
        resolution,
        requirement,
        remediation_execution(RemediationAction.CORRECTION, remediation),
        remediation_execution(RemediationAction.REPUBLICATION, RemediationStatus.NOT_REQUIRED),
        EVIDENCE if reviewed else None,
        BASE if reviewed else None,
    )


@given(
    kinds=st.lists(st.sampled_from(("warning", "quarantined", "rejected")), min_size=1, max_size=8)
)
@pytest.mark.property
def test_multiple_conflicts_always_choose_strictest_outcome(kinds: list[str]) -> None:
    capabilities, policy, registry, request, scorecard, artifact_object = passing_artifact()
    conflicts = tuple(generated_conflict(kind, index) for index, kind in enumerate(kinds))
    decision = publication_gate(
        evaluation_artifact=artifact_object,  # type: ignore[arg-type]
        capabilities=capabilities,
        policy=policy,
        lifecycle_registry=registry,
        request=request,
        scorecard=scorecard,
        stale=False,
        critical_missing=False,
        reconciliation_conflicts=conflicts,
    )
    expected = (
        PublicationStatus.REJECTED
        if "rejected" in kinds
        else (
            PublicationStatus.QUARANTINED
            if "quarantined" in kinds
            else PublicationStatus.ACCEPTED_WITH_WARNINGS
        )
    )
    assert decision.status is expected


@given(values=st.dictionaries(st.text(min_size=1, max_size=8), st.integers(), max_size=8))
@pytest.mark.property
def test_reports_remain_deterministic_for_generated_sections(values: dict[str, int]) -> None:
    *_, artifact = passing_artifact()
    sections = {"generated": values}
    assert deterministic_report("SYNTHETIC-PROVIDER", artifact, sections) == deterministic_report(
        "SYNTHETIC-PROVIDER", artifact, sections
    )


@given(
    start_offset=st.integers(min_value=1, max_value=3650),
    end_offset=st.integers(min_value=1, max_value=3650),
)
@pytest.mark.property
def test_generated_invalid_provider_history_intervals_fail(
    start_offset: int, end_offset: int
) -> None:
    later = BASE + timedelta(days=max(start_offset, end_offset))
    earlier = BASE + timedelta(days=min(start_offset, end_offset) - 1)
    with pytest.raises(ValueError, match="historical_end"):
        replace(base_capabilities(), historical_start=later, historical_end=earlier)
