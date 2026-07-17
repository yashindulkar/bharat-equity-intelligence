import hashlib
import json
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any

import pytest

from bharat_equity.application.provider_evaluation import (
    DEFAULT_SCORECARD_VERSION,
    DEFAULT_WEIGHTS,
    EVALUATION_ARTIFACT_SCHEMA_VERSION,
    REPORT_SCHEMA_VERSION,
    EvaluationArtifact,
    EvaluationRequest,
    deterministic_report,
    evaluate_hard_gates,
    history_gap_relevant,
    publication_gate,
    validate_evaluation_artifact,
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

NOW = datetime(2026, 7, 13, 12, tzinfo=UTC)
HISTORY_START = datetime(2020, 1, 1, tzinfo=UTC)
LATEST_SESSION = datetime(2026, 7, 10, 10, tzinfo=UTC)
EVIDENCE = EvidenceReference(
    "SYNTHETIC-EVIDENCE",
    "SYNTHETIC-1",
    NOW - timedelta(days=30),
)


def capabilities(
    *,
    historical_start: datetime = HISTORY_START,
    historical_end: datetime = LATEST_SESSION,
    history_gaps: tuple[HistoryGap, ...] = (),
    **changes: CapabilityState,
) -> ProviderCapabilityRegistry:
    values = {name: CapabilityState.SUPPORTED for name in CAPABILITY_NAMES}
    values.update(changes)
    return ProviderCapabilityRegistry(
        provider_id="SYNTHETIC-PROVIDER",
        product="SYNTHETIC-PRODUCT",
        version="SYNTHETIC-1",
        capabilities=values,
        historical_start=historical_start,
        historical_end=historical_end,
        history_gaps=history_gaps,
        capability_evidence={
            name: (
                EvidenceReference(
                    f"SYNTHETIC-EVIDENCE-{name}",
                    "SYNTHETIC-1",
                    NOW - timedelta(days=30),
                ),
            )
            for name in CAPABILITY_NAMES
        },
    )


def policy(
    *,
    purpose: Permission = Permission.PERMITTED,
    raw: Permission = Permission.PERMITTED,
    approval: ApprovalStatus = ApprovalStatus.APPROVED,
    termination_at: datetime | None = None,
    geography: ProcessingGeographyGrant | None = None,
    restrictions: tuple[str, ...] = ("SYNTHETIC-FORBIDDEN-JURISDICTION",),
) -> DataUsagePolicy:
    ends_at = termination_at or NOW + timedelta(days=120)
    purposes = {item: Permission.PROHIBITED for item in UsagePurpose}
    purposes[UsagePurpose.PRIVATE_HOUSEHOLD_RESEARCH] = purpose
    approved_at = NOW - timedelta(days=20) if approval is ApprovalStatus.APPROVED else None
    rejected_at = NOW - timedelta(days=1) if approval is ApprovalStatus.REJECTED else None
    review_due = NOW + timedelta(days=90) if approval is ApprovalStatus.APPROVED else None
    return DataUsagePolicy(
        policy_id="SYNTHETIC-POLICY",
        provider_id="SYNTHETIC-PROVIDER",
        product="SYNTHETIC-PRODUCT",
        agreement_version="SYNTHETIC-AGREEMENT-1",
        effective_from=NOW - timedelta(days=30),
        effective_until=ends_at,
        termination_event_id="SYNTHETIC-TERMINATION-1",
        termination_at=ends_at,
        early_termination_amendment=None,
        permitted_users=("SYNTHETIC-OPERATOR",),
        permitted_purposes=purposes,
        raw_retention=raw,
        derived_data=Permission.PERMITTED,
        backtesting=Permission.PROHIBITED,
        model_training=Permission.PROHIBITED,
        display=Permission.PERMITTED,
        citation=Permission.UNKNOWN,
        backup=Permission.UNKNOWN,
        fixtures=Permission.PERMITTED,
        post_termination_raw_data=Permission.PROHIBITED,
        post_termination_backup=Permission.PROHIBITED,
        post_termination_fixtures=Permission.PROHIBITED,
        post_termination_derived_data=Permission.PERMITTED,
        post_termination_audit_evidence=Permission.PERMITTED,
        deletion_obligations="SYNTHETIC deletion required",
        processing_geography=geography
        or ProcessingGeographyGrant(
            GeographyScope.JURISDICTIONS,
            ("SYNTHETIC-JURISDICTION",),
            (EVIDENCE,),
        ),
        geographical_restrictions=restrictions,
        evidence_references=(EVIDENCE,),
        reviewer="SYNTHETIC-REVIEWER",
        approved_at=approved_at,
        rejected_at=rejected_at,
        review_due_at=review_due,
        external_ai_processing=Permission.PROHIBITED,
        approval_status=approval,
    )


def request(**changes: object) -> EvaluationRequest:
    values: dict[str, object] = {
        "at": NOW,
        "purpose": UsagePurpose.PRIVATE_HOUSEHOLD_RESEARCH,
        "user": "SYNTHETIC-OPERATOR",
        "processing_geography": "SYNTHETIC-JURISDICTION",
        "required_history_start": HISTORY_START,
        "latest_required_session": LATEST_SESSION,
        "required_security_ids": ("SYNTHETIC-SECURITY",),
    }
    values.update(changes)
    return EvaluationRequest(**values)  # type: ignore[arg-type]


def scorecard(
    governing_policy: DataUsagePolicy,
    *,
    raw_score: Decimal = Decimal("80"),
    weights: dict[ScoreDimension, Decimal] | None = None,
    assessed_at: datetime = NOW,
    evidence_available_at: datetime | None = None,
    entry_assessed_at: datetime | None = None,
    entry_evidence_available_at: datetime | None = None,
    scorecard_evidence_available_at: datetime | None = None,
) -> ProviderScorecard:
    selected = weights or dict(DEFAULT_WEIGHTS)
    selected_entry_assessed_at = entry_assessed_at or assessed_at
    shared_evidence_at = evidence_available_at or (
        min(assessed_at, selected_entry_assessed_at) - timedelta(days=1)
    )
    scorecard_evidence = EvidenceReference(
        "SYNTHETIC-SCORECARD-EVIDENCE",
        "SYNTHETIC-SCORE-EVIDENCE-1",
        scorecard_evidence_available_at or shared_evidence_at,
    )
    entry_evidence = EvidenceReference(
        "SYNTHETIC-ENTRY-EVIDENCE",
        "SYNTHETIC-SCORE-EVIDENCE-1",
        entry_evidence_available_at or shared_evidence_at,
    )
    return ProviderScorecard(
        provider_id="SYNTHETIC-PROVIDER",
        product="SYNTHETIC-PRODUCT",
        product_version="SYNTHETIC-1",
        policy_id=governing_policy.policy_id,
        agreement_version=governing_policy.agreement_version,
        policy_snapshot_id=contract_snapshot_id(governing_policy),
        scorecard_version=DEFAULT_SCORECARD_VERSION,
        methodology_version="SYNTHETIC-METHOD-1",
        assessed_at=assessed_at,
        evidence_references=(scorecard_evidence,),
        entries=tuple(
            ScorecardEntry(
                dimension=dimension,
                raw_score=raw_score,
                weight=selected[dimension],
                evidence_references=(entry_evidence,),
                assessor="SYNTHETIC-ASSESSOR",
                assessed_at=selected_entry_assessed_at,
                method_version="SYNTHETIC-METHOD-1",
                explanation=f"SYNTHETIC explanation for {dimension.value}",
                confidence=ConfidenceLevel.MEDIUM,
            )
            for dimension in ScoreDimension
        ),
    )


def disposition(
    category: DataCategory,
    permission: Permission,
    state: DispositionState,
    deadline: datetime,
) -> DeletionDisposition:
    completed = state is DispositionState.COMPLETED
    retained = state is DispositionState.RETAINED
    evidence = (
        (
            DeletionEvidenceReference(
                category,
                EvidenceReference(
                    f"SYNTHETIC-{category.value}-EVIDENCE",
                    "SYNTHETIC-1",
                    NOW - timedelta(hours=1),
                ),
            ),
        )
        if completed or retained
        else ()
    )
    return DeletionDisposition(
        category=category,
        contractual_permission=permission,
        state=state,
        applicable_deadline=deadline,
        completion_at=NOW if completed else None,
        evidence_references=evidence,
        verifier=f"SYNTHETIC-{category.value}-VERIFIER" if completed or retained else None,
        record_version="SYNTHETIC-DISPOSITION-1",
    )


def lifecycle(
    governing_policy: DataUsagePolicy,
    *,
    deadline: datetime,
    prohibited_state: DispositionState = DispositionState.COMPLETED,
) -> TerminationDeletionLifecycle:
    assert governing_policy.termination_at is not None
    assert governing_policy.termination_event_id is not None
    permissions = {
        DataCategory.RAW_DATA: governing_policy.post_termination_raw_data,
        DataCategory.BACKUPS: governing_policy.post_termination_backup,
        DataCategory.TEST_FIXTURES: governing_policy.post_termination_fixtures,
        DataCategory.DERIVED_DATA: governing_policy.post_termination_derived_data,
        DataCategory.AUDIT_EVIDENCE: governing_policy.post_termination_audit_evidence,
    }
    return TerminationDeletionLifecycle(
        lifecycle_id="SYNTHETIC-LIFECYCLE-1",
        provider_id=governing_policy.provider_id,
        product=governing_policy.product,
        policy_id=governing_policy.policy_id,
        agreement_version=governing_policy.agreement_version,
        termination_event_id=governing_policy.termination_event_id,
        termination_at=governing_policy.termination_at,
        dispositions=tuple(
            disposition(
                category,
                permission,
                DispositionState.RETAINED
                if permission is Permission.PERMITTED
                else prohibited_state,
                deadline,
            )
            for category, permission in permissions.items()
        ),
        record_version="SYNTHETIC-LIFECYCLE-RECORD-1",
    )


def registry(*records: TerminationDeletionLifecycle) -> TerminationLifecycleRegistry:
    return TerminationLifecycleRegistry("SYNTHETIC-LIFECYCLE-REGISTRY-1", records)


def execution(action: RemediationAction, status: RemediationStatus) -> RemediationExecution:
    completed = status is RemediationStatus.COMPLETED
    return RemediationExecution(
        action,
        status,
        NOW if completed else None,
        (EVIDENCE,) if completed else (),
        "SYNTHETIC-REMEDIATION-VERIFIER" if completed else None,
    )


def conflict(
    status: ConflictResolutionStatus,
    *,
    severity: GapSeverity = GapSeverity.CRITICAL,
    requirement: CorrectionRequirement = CorrectionRequirement.CORRECTION_REQUIRED,
    correction_status: RemediationStatus = RemediationStatus.PENDING,
    republication_status: RemediationStatus = RemediationStatus.NOT_REQUIRED,
    conflict_id: str | None = None,
) -> ReconciliationConflict:
    reviewed = status is not ConflictResolutionStatus.UNRESOLVED
    if status is ConflictResolutionStatus.INVALID_NON_REMEDIABLE:
        requirement = CorrectionRequirement.NONE
        correction_status = RemediationStatus.NOT_REQUIRED
        republication_status = RemediationStatus.NOT_REQUIRED
    return ReconciliationConflict(
        conflict_id or f"SYNTHETIC-CONFLICT-{status.value}",
        "close",
        (
            CompetingValue(
                "SYNTHETIC-SOURCE-A",
                "100.00",
                "SYNTHETIC-RAW-CLOSE",
                EVIDENCE,
                ConfidenceLevel.HIGH,
            ),
            CompetingValue(
                "SYNTHETIC-SOURCE-B",
                "101.00",
                "SYNTHETIC-RAW-CLOSE",
                EVIDENCE,
                ConfidenceLevel.MEDIUM,
            ),
        ),
        "SYNTHETIC-EXACT",
        "SYNTHETIC-1",
        "1.00",
        severity,
        status,
        requirement,
        execution(RemediationAction.CORRECTION, correction_status),
        execution(RemediationAction.REPUBLICATION, republication_status),
        EVIDENCE if reviewed else None,
        NOW if reviewed else None,
    )


def passing_context() -> tuple[
    ProviderCapabilityRegistry,
    DataUsagePolicy,
    TerminationLifecycleRegistry,
    EvaluationRequest,
    ProviderScorecard,
    EvaluationArtifact,
]:
    current_policy = policy()
    current_capabilities = capabilities()
    current_registry = registry()
    current_request = request()
    current_scorecard = scorecard(current_policy)
    artifact = evaluate_hard_gates(
        current_capabilities,
        current_policy,
        current_registry,
        current_request,
        current_scorecard,
    )
    return (
        current_capabilities,
        current_policy,
        current_registry,
        current_request,
        current_scorecard,
        artifact,
    )


def forged_artifact(
    source: EvaluationArtifact,
    **changes: object,
) -> EvaluationArtifact:
    """Reproduce the caller exploit: forge fields and a consistent content hash."""

    names = (
        "schema_version",
        "passed",
        "reasons",
        "weighted_score",
        "scorecard_version",
        "capability_snapshot_id",
        "policy_snapshot_id",
        "lifecycle_registry_snapshot_id",
        "lifecycle_snapshot_id",
        "scorecard_snapshot_id",
        "request_snapshot_id",
        "evaluated_at",
    )
    values: dict[str, Any] = {name: getattr(source, name) for name in names}
    values.update(changes)
    content = {
        **values,
        "reasons": [reason.value for reason in values["reasons"]],
        "weighted_score": (
            None if values["weighted_score"] is None else str(values["weighted_score"])
        ),
        "evaluated_at": values["evaluated_at"].isoformat(),
    }
    payload = json.dumps(content, sort_keys=True, separators=(",", ":"))
    values["artifact_id"] = f"sha256:{hashlib.sha256(payload.encode('utf-8')).hexdigest()}"
    forged = object.__new__(EvaluationArtifact)
    for name, value in values.items():
        object.__setattr__(forged, name, value)
    return forged


def publish(
    conflict_records: tuple[ReconciliationConflict, ...] = (),
    **changes: object,
) -> PublicationStatus:
    (
        current_capabilities,
        current_policy,
        current_registry,
        current_request,
        current_scorecard,
        artifact,
    ) = passing_context()
    values: dict[str, object] = {
        "evaluation_artifact": artifact,
        "capabilities": current_capabilities,
        "policy": current_policy,
        "lifecycle_registry": current_registry,
        "request": current_request,
        "scorecard": current_scorecard,
        "stale": False,
        "critical_missing": False,
        "reconciliation_conflicts": conflict_records,
    }
    values.update(changes)
    return publication_gate(**values).status  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("candidate", "expected"),
    [
        (policy(purpose=Permission.UNKNOWN), ReasonCode.PERMISSION_UNKNOWN),
        (policy(purpose=Permission.PROHIBITED), ReasonCode.PURPOSE_NOT_PERMITTED),
        (policy(raw=Permission.PROHIBITED), ReasonCode.RAW_RETENTION_FORBIDDEN),
        (policy(approval=ApprovalStatus.PENDING), ReasonCode.PROVIDER_NOT_APPROVED),
    ],
)
def test_policy_hard_gates(candidate: DataUsagePolicy, expected: ReasonCode) -> None:
    result = evaluate_hard_gates(
        capabilities(), candidate, registry(), request(), scorecard(candidate)
    )
    assert not result.passed
    assert expected in result.reasons
    assert result.weighted_score is None


def test_score_exists_only_after_all_hard_gates_pass() -> None:
    *_, result = passing_context()
    assert result.passed
    assert result.weighted_score == Decimal("80.00")
    assert result.scorecard_version == DEFAULT_SCORECARD_VERSION


def test_terminated_agreement_without_lifecycle_fails_dedicated_reason() -> None:
    terminated_policy = policy(termination_at=NOW)
    result = evaluate_hard_gates(
        capabilities(), terminated_policy, registry(), request(), scorecard(terminated_policy)
    )
    assert ReasonCode.AGREEMENT_EXPIRED in result.reasons
    assert ReasonCode.TERMINATION_LIFECYCLE_MISSING in result.reasons
    assert ReasonCode.TERMINATION_DELETION_OVERDUE not in result.reasons


def test_pretermination_does_not_require_lifecycle() -> None:
    *_, result = passing_context()
    assert result.passed
    assert ReasonCode.TERMINATION_LIFECYCLE_MISSING not in result.reasons


def test_termination_exact_boundary_is_deterministic() -> None:
    terminated_policy = policy(termination_at=NOW)
    record = lifecycle(terminated_policy, deadline=NOW + timedelta(days=1))
    result = evaluate_hard_gates(
        capabilities(),
        terminated_policy,
        registry(record),
        request(),
        scorecard(terminated_policy),
    )
    assert result.reasons == (ReasonCode.AGREEMENT_EXPIRED,)


@pytest.mark.parametrize(
    "changes",
    [
        {"provider_id": "SYNTHETIC-OTHER"},
        {"product": "SYNTHETIC-OTHER"},
        {"policy_id": "SYNTHETIC-OTHER"},
        {"agreement_version": "SYNTHETIC-OTHER"},
        {"termination_event_id": "SYNTHETIC-OTHER"},
    ],
)
def test_lifecycle_cross_agreement_substitution_fails(changes: dict[str, object]) -> None:
    terminated_policy = policy(termination_at=NOW)
    candidate = replace(
        lifecycle(terminated_policy, deadline=NOW + timedelta(days=1)),
        **changes,
    )
    result = evaluate_hard_gates(
        capabilities(),
        terminated_policy,
        registry(candidate),
        request(),
        scorecard(terminated_policy),
    )
    assert ReasonCode.TERMINATION_LIFECYCLE_MISMATCH in result.reasons


def test_inconsistent_termination_timestamp_fails_lifecycle_construction() -> None:
    terminated_policy = policy(termination_at=NOW)
    with pytest.raises(ValueError, match="completion cannot precede termination"):
        replace(
            lifecycle(terminated_policy, deadline=NOW + timedelta(days=1)),
            termination_at=NOW + timedelta(seconds=1),
        )


def test_exact_lifecycle_identity_succeeds_deletion_evaluation() -> None:
    terminated_policy = policy(termination_at=NOW)
    candidate = lifecycle(terminated_policy, deadline=NOW + timedelta(days=1))
    result = evaluate_hard_gates(
        capabilities(),
        terminated_policy,
        registry(candidate),
        request(),
        scorecard(terminated_policy),
    )
    assert ReasonCode.TERMINATION_LIFECYCLE_MISSING not in result.reasons
    assert ReasonCode.TERMINATION_LIFECYCLE_MISMATCH not in result.reasons


@pytest.mark.parametrize("category", list(DataCategory))
def test_completed_deletion_requires_category_specific_evidence(category: DataCategory) -> None:
    with pytest.raises(ValueError, match="category-specific"):
        DeletionDisposition(
            category,
            Permission.PROHIBITED,
            DispositionState.COMPLETED,
            NOW,
            NOW,
            (),
            "SYNTHETIC-VERIFIER",
            "SYNTHETIC-1",
        )


def test_one_deletion_certificate_cannot_support_unrelated_categories() -> None:
    raw_evidence = DeletionEvidenceReference(
        DataCategory.RAW_DATA,
        EvidenceReference("SYNTHETIC-RAW-CERT", "SYNTHETIC-1", NOW),
    )
    raw = DeletionDisposition(
        DataCategory.RAW_DATA,
        Permission.PROHIBITED,
        DispositionState.COMPLETED,
        NOW,
        NOW,
        (raw_evidence,),
        "SYNTHETIC-VERIFIER",
        "SYNTHETIC-1",
    )
    assert raw.evidence_references == (raw_evidence,)
    with pytest.raises(ValueError, match="governed category"):
        replace(raw, category=DataCategory.BACKUPS)


def test_retained_derived_permission_cannot_authorize_raw_retention() -> None:
    with pytest.raises(ValueError, match="explicit category permission"):
        disposition(
            DataCategory.RAW_DATA,
            Permission.PROHIBITED,
            DispositionState.RETAINED,
            NOW,
        )


def test_prohibited_category_overdue_after_deadline_fails() -> None:
    terminated_policy = policy(termination_at=NOW - timedelta(days=2))
    record = lifecycle(
        terminated_policy,
        deadline=NOW - timedelta(days=1),
        prohibited_state=DispositionState.OVERDUE,
    )
    result = evaluate_hard_gates(
        capabilities(), terminated_policy, registry(record), request(), scorecard(terminated_policy)
    )
    assert ReasonCode.TERMINATION_DELETION_OVERDUE in result.reasons


def test_permitted_retention_is_distinct_from_deletion_completion() -> None:
    retained = disposition(
        DataCategory.DERIVED_DATA,
        Permission.PERMITTED,
        DispositionState.RETAINED,
        NOW,
    )
    assert retained.state is DispositionState.RETAINED
    assert retained.completion_at is None


def test_approved_policy_rejects_empty_geography_scope() -> None:
    with pytest.raises(ValueError, match="at least one"):
        ProcessingGeographyGrant(GeographyScope.JURISDICTIONS, (), (EVIDENCE,))


def test_unknown_processing_geography_fails_closed() -> None:
    current_policy = policy()
    result = evaluate_hard_gates(
        capabilities(),
        current_policy,
        registry(),
        request(processing_geography="SYNTHETIC-UNKNOWN"),
        scorecard(current_policy),
    )
    assert ReasonCode.PROCESSING_GEOGRAPHY_UNKNOWN in result.reasons


def test_explicit_processing_geography_passes() -> None:
    *_, result = passing_context()
    assert result.passed


def test_restricted_processing_geography_fails() -> None:
    current_policy = policy()
    result = evaluate_hard_gates(
        capabilities(),
        current_policy,
        registry(),
        request(processing_geography="SYNTHETIC-FORBIDDEN-JURISDICTION"),
        scorecard(current_policy),
    )
    assert ReasonCode.PURPOSE_NOT_PERMITTED in result.reasons


def test_worldwide_permission_requires_explicit_typed_scope() -> None:
    worldwide = ProcessingGeographyGrant(GeographyScope.WORLDWIDE, (), (EVIDENCE,))
    current_policy = policy(geography=worldwide, restrictions=())
    result = evaluate_hard_gates(
        capabilities(),
        current_policy,
        registry(),
        request(processing_geography="SYNTHETIC-ANYWHERE"),
        scorecard(current_policy),
    )
    assert result.passed


def test_permitted_and_restricted_geography_overlap_fails_construction() -> None:
    with pytest.raises(ValueError, match="both permitted and restricted"):
        policy(restrictions=("SYNTHETIC-JURISDICTION",))


@pytest.mark.parametrize(
    "changes",
    [
        {"permitted_users": ("",)},
        {"approved_at": NOW + timedelta(days=121)},
        {"review_due_at": NOW - timedelta(days=21)},
        {
            "approval_status": ApprovalStatus.REJECTED,
            "approved_at": NOW - timedelta(days=1),
            "rejected_at": NOW,
            "review_due_at": None,
        },
        {"evidence_references": ()},
    ],
)
def test_invalid_policy_identity_and_timeline_invariants_fail_at_construction(
    changes: dict[str, object],
) -> None:
    with pytest.raises((TypeError, ValueError)):
        replace(policy(), **changes)


def test_permission_maps_require_enums_and_are_defensively_immutable() -> None:
    current = policy()
    source = dict(current.permitted_purposes)
    source[UsagePurpose.PRIVATE_HOUSEHOLD_RESEARCH] = "PERMITTED"  # type: ignore[assignment]
    with pytest.raises(TypeError, match="Permission"):
        replace(current, permitted_purposes=source)
    with pytest.raises(TypeError):
        current.permitted_purposes[UsagePurpose.BACKTESTING] = Permission.PERMITTED  # type: ignore[index]


def test_capability_maps_are_defensively_copied_and_read_only() -> None:
    source = {name: CapabilityState.SUPPORTED for name in CAPABILITY_NAMES}
    candidate = ProviderCapabilityRegistry(
        provider_id="SYNTHETIC-PROVIDER",
        product="SYNTHETIC-PRODUCT",
        version="SYNTHETIC-1",
        capabilities=source,
        historical_start=HISTORY_START,
        historical_end=LATEST_SESSION,
        history_gaps=(),
        capability_evidence={name: (EVIDENCE,) for name in CAPABILITY_NAMES},
    )
    source["historical_depth"] = CapabilityState.UNKNOWN
    assert candidate.capabilities["historical_depth"] is CapabilityState.SUPPORTED
    with pytest.raises(TypeError):
        candidate.capabilities["historical_depth"] = CapabilityState.UNKNOWN  # type: ignore[index]


def envelope(governing_policy: DataUsagePolicy, payload: bytes) -> ProviderResponseEnvelope:
    return ProviderResponseEnvelope(
        provider_id="SYNTHETIC-PROVIDER",
        product="SYNTHETIC-PRODUCT",
        product_version="SYNTHETIC-1",
        request_id="SYNTHETIC-REQUEST",
        source_record_id="SYNTHETIC-SOURCE",
        retrieved_at=NOW,
        published_at=NOW - timedelta(minutes=1),
        payload_schema_version="SYNTHETIC-SCHEMA-1",
        content_type="application/json",
        immutable_payload_hash=f"sha256:{hashlib.sha256(payload).hexdigest()}",
        policy_id=governing_policy.policy_id,
        agreement_version=governing_policy.agreement_version,
        policy_snapshot_id=contract_snapshot_id(governing_policy),
        intended_usage_purpose=UsagePurpose.PRIVATE_HOUSEHOLD_RESEARCH,
    )


def validate_envelope(
    candidate: ProviderResponseEnvelope, payload: bytes
) -> tuple[ReasonCode, ...]:
    return validate_provider_envelope(
        candidate,
        payload,
        capabilities(),
        policy(),
        request(),
        frozenset({"SYNTHETIC-SCHEMA-1"}),
    ).reasons


def test_exact_valid_envelope_and_payload_pass() -> None:
    payload = b"SYNTHETIC-PAYLOAD"
    assert not validate_envelope(envelope(policy(), payload), payload)


@pytest.mark.parametrize(
    ("changes", "reason"),
    [
        ({"provider_id": "SYNTHETIC-OTHER"}, ReasonCode.ENVELOPE_MISMATCH),
        ({"product": "SYNTHETIC-OTHER"}, ReasonCode.ENVELOPE_MISMATCH),
        ({"product_version": "SYNTHETIC-OTHER"}, ReasonCode.ENVELOPE_MISMATCH),
        ({"policy_id": "SYNTHETIC-OTHER"}, ReasonCode.ENVELOPE_MISMATCH),
        (
            {"agreement_version": "SYNTHETIC-OTHER"},
            ReasonCode.ENVELOPE_AGREEMENT_MISMATCH,
        ),
        (
            {"policy_snapshot_id": f"sha256:{'0' * 64}"},
            ReasonCode.ENVELOPE_POLICY_SNAPSHOT_MISMATCH,
        ),
        (
            {"intended_usage_purpose": UsagePurpose.BACKTESTING},
            ReasonCode.ENVELOPE_MISMATCH,
        ),
        ({"payload_schema_version": "SYNTHETIC-OTHER"}, ReasonCode.SCHEMA_NOT_ALLOWED),
    ],
)
def test_envelope_binding_mismatches_fail(changes: dict[str, object], reason: ReasonCode) -> None:
    payload = b"SYNTHETIC-PAYLOAD"
    assert reason in validate_envelope(replace(envelope(policy(), payload), **changes), payload)


def test_single_byte_payload_mutation_fails_sha256() -> None:
    payload = b"SYNTHETIC-PAYLOAD"
    assert ReasonCode.EVIDENCE_INTEGRITY_FAILURE in validate_envelope(
        envelope(policy(), payload), payload[:-1] + b"X"
    )


@pytest.mark.parametrize(
    ("candidate", "expected"),
    [
        (
            conflict(ConflictResolutionStatus.UNRESOLVED),
            PublicationStatus.QUARANTINED,
        ),
        (
            conflict(
                ConflictResolutionStatus.UNRESOLVED,
                severity=GapSeverity.WARNING,
            ),
            PublicationStatus.ACCEPTED_WITH_WARNINGS,
        ),
        (
            conflict(ConflictResolutionStatus.INVALID_NON_REMEDIABLE),
            PublicationStatus.REJECTED,
        ),
        (
            conflict(
                ConflictResolutionStatus.RESOLVED_APPROVED,
                correction_status=RemediationStatus.PENDING,
            ),
            PublicationStatus.QUARANTINED,
        ),
        (
            conflict(
                ConflictResolutionStatus.RESOLVED_APPROVED,
                correction_status=RemediationStatus.INVALID,
            ),
            PublicationStatus.QUARANTINED,
        ),
        (
            conflict(
                ConflictResolutionStatus.RESOLVED_APPROVED,
                correction_status=RemediationStatus.COMPLETED,
            ),
            PublicationStatus.ACCEPTED_WITH_WARNINGS,
        ),
        (
            conflict(
                ConflictResolutionStatus.RESOLVED_APPROVED,
                requirement=CorrectionRequirement.REPUBLICATION_REQUIRED,
                correction_status=RemediationStatus.NOT_REQUIRED,
                republication_status=RemediationStatus.PENDING,
            ),
            PublicationStatus.QUARANTINED,
        ),
        (
            conflict(
                ConflictResolutionStatus.RESOLVED_APPROVED,
                requirement=CorrectionRequirement.REPUBLICATION_REQUIRED,
                correction_status=RemediationStatus.NOT_REQUIRED,
                republication_status=RemediationStatus.COMPLETED,
            ),
            PublicationStatus.ACCEPTED_WITH_WARNINGS,
        ),
        (
            conflict(
                ConflictResolutionStatus.RESOLVED_APPROVED,
                requirement=CorrectionRequirement.CORRECTION_AND_REPUBLICATION_REQUIRED,
                correction_status=RemediationStatus.COMPLETED,
                republication_status=RemediationStatus.PENDING,
            ),
            PublicationStatus.QUARANTINED,
        ),
        (
            conflict(
                ConflictResolutionStatus.RESOLVED_APPROVED,
                requirement=CorrectionRequirement.CORRECTION_AND_REPUBLICATION_REQUIRED,
                correction_status=RemediationStatus.COMPLETED,
                republication_status=RemediationStatus.COMPLETED,
            ),
            PublicationStatus.ACCEPTED_WITH_WARNINGS,
        ),
    ],
)
def test_reconciliation_transition_matrix(
    candidate: ReconciliationConflict, expected: PublicationStatus
) -> None:
    assert publish((candidate,)) is expected


def test_completed_remediation_without_evidence_fails_construction() -> None:
    with pytest.raises(ValueError, match="requires evidence"):
        RemediationExecution(
            RemediationAction.CORRECTION,
            RemediationStatus.COMPLETED,
        )


def test_multiple_conflicts_use_strictest_outcome() -> None:
    warning = conflict(
        ConflictResolutionStatus.UNRESOLVED,
        severity=GapSeverity.WARNING,
        conflict_id="SYNTHETIC-WARNING",
    )
    pending = conflict(
        ConflictResolutionStatus.RESOLVED_APPROVED,
        conflict_id="SYNTHETIC-PENDING",
    )
    rejected = conflict(
        ConflictResolutionStatus.INVALID_NON_REMEDIABLE,
        conflict_id="SYNTHETIC-REJECTED",
    )
    assert publish((warning, pending)) is PublicationStatus.QUARANTINED
    assert publish((warning, pending, rejected)) is PublicationStatus.REJECTED


def test_no_conflict_uses_normal_publication_path() -> None:
    assert publish() is PublicationStatus.ACCEPTED


def test_reconciliation_rejects_duplicate_sources_and_identical_values() -> None:
    base = conflict(ConflictResolutionStatus.UNRESOLVED)
    with pytest.raises(ValueError, match="source_record_ids"):
        replace(
            base,
            values=(
                base.values[0],
                replace(base.values[1], source_record_id="SYNTHETIC-SOURCE-A"),
            ),
        )
    with pytest.raises(ValueError, match="distinct"):
        replace(
            base,
            values=(base.values[0], replace(base.values[1], value="100.00")),
        )


def test_scorecard_future_assessment_and_evidence_fail_pit_gate() -> None:
    current_policy = policy()
    future_assessment = evaluate_hard_gates(
        capabilities(),
        current_policy,
        registry(),
        request(),
        scorecard(current_policy, assessed_at=NOW + timedelta(seconds=1)),
    )
    assert ReasonCode.SCORECARD_FUTURE_ASSESSMENT in future_assessment.reasons
    future_evidence = evaluate_hard_gates(
        capabilities(),
        current_policy,
        registry(),
        request(),
        scorecard(
            current_policy,
            assessed_at=NOW + timedelta(seconds=1),
            evidence_available_at=NOW + timedelta(seconds=1),
        ),
    )
    assert ReasonCode.SCORECARD_FUTURE_EVIDENCE in future_evidence.reasons


def test_entry_evidence_cannot_postdate_claimed_assessment() -> None:
    with pytest.raises(ValueError, match="entry evidence cannot become available"):
        scorecard(
            policy(),
            entry_assessed_at=NOW - timedelta(days=2),
            entry_evidence_available_at=NOW - timedelta(days=1),
        )


def test_scorecard_evidence_cannot_postdate_claimed_assessment() -> None:
    with pytest.raises(ValueError, match="scorecard evidence cannot become available"):
        scorecard(
            policy(),
            assessed_at=NOW - timedelta(days=2),
            entry_assessed_at=NOW - timedelta(days=2),
            scorecard_evidence_available_at=NOW - timedelta(days=1),
        )


def test_score_evidence_exact_assessment_boundaries_succeed() -> None:
    boundary = NOW - timedelta(days=1)
    candidate = scorecard(
        policy(),
        assessed_at=boundary,
        entry_assessed_at=boundary,
        entry_evidence_available_at=boundary,
        scorecard_evidence_available_at=boundary,
    )
    assert candidate.assessed_at == boundary
    assert all(entry.assessed_at == boundary for entry in candidate.entries)


def test_entry_assessment_cannot_follow_scorecard_assessment() -> None:
    with pytest.raises(ValueError, match="entry assessment cannot follow"):
        scorecard(
            policy(),
            assessed_at=NOW - timedelta(days=1),
            entry_assessed_at=NOW,
        )


def test_historical_score_evidence_before_request_cutoff_succeeds() -> None:
    current_policy = policy()
    assessment = NOW - timedelta(days=1)
    evidence = assessment - timedelta(days=1)
    result = evaluate_hard_gates(
        capabilities(),
        current_policy,
        registry(),
        request(),
        scorecard(
            current_policy,
            assessed_at=assessment,
            entry_assessed_at=assessment,
            entry_evidence_available_at=evidence,
            scorecard_evidence_available_at=evidence,
        ),
    )
    assert result.passed


def test_evidence_before_cutoff_but_after_assessment_still_fails() -> None:
    assessment = NOW - timedelta(days=2)
    with pytest.raises(ValueError, match="entry evidence cannot become available"):
        scorecard(
            policy(),
            assessed_at=NOW - timedelta(days=1),
            entry_assessed_at=assessment,
            entry_evidence_available_at=assessment + timedelta(hours=1),
        )


def test_scorecard_exact_cutoff_boundary_succeeds() -> None:
    current_policy = policy()
    result = evaluate_hard_gates(
        capabilities(),
        current_policy,
        registry(),
        request(),
        scorecard(current_policy, assessed_at=NOW, evidence_available_at=NOW),
    )
    assert result.passed


@pytest.mark.parametrize(
    "changes",
    [
        {"policy_id": "SYNTHETIC-OTHER"},
        {"agreement_version": "SYNTHETIC-OTHER"},
        {"policy_snapshot_id": f"sha256:{'0' * 64}"},
    ],
)
def test_scorecard_wrong_policy_binding_fails(changes: dict[str, object]) -> None:
    current_policy = policy()
    candidate = replace(scorecard(current_policy), **changes)
    result = evaluate_hard_gates(capabilities(), current_policy, registry(), request(), candidate)
    assert ReasonCode.SCORECARD_POLICY_MISMATCH in result.reasons


@pytest.mark.parametrize(
    "value",
    [Decimal("NaN"), Decimal("Infinity"), Decimal("-Infinity")],
)
def test_non_finite_scores_and_weights_fail(value: Decimal) -> None:
    current_policy = policy()
    with pytest.raises(ValueError):
        scorecard(current_policy, raw_score=value)
    invalid = dict(DEFAULT_WEIGHTS)
    invalid[ScoreDimension.COST] = value
    with pytest.raises(ValueError):
        scorecard(current_policy, weights=invalid)


@pytest.mark.parametrize("weight", [Decimal("-0.01"), Decimal("1.01")])
def test_weight_bounds_fail(weight: Decimal) -> None:
    invalid = dict(DEFAULT_WEIGHTS)
    invalid[ScoreDimension.COST] = weight
    with pytest.raises(ValueError, match="between 0 and 1"):
        scorecard(policy(), weights=invalid)


def test_invalid_weight_total_missing_and_duplicate_dimensions_fail() -> None:
    current_policy = policy()
    invalid = dict(DEFAULT_WEIGHTS)
    invalid[ScoreDimension.COST] = Decimal("0.06")
    with pytest.raises(ValueError, match="sum exactly"):
        scorecard(current_policy, weights=invalid)
    valid = scorecard(current_policy)
    with pytest.raises(ValueError, match="complete"):
        replace(valid, entries=valid.entries[:-1])
    with pytest.raises(ValueError, match="unique"):
        replace(valid, entries=(*valid.entries[:-1], valid.entries[0]))


def test_weighted_score_uses_deterministic_half_even_rounding() -> None:
    assert scorecard(policy(), raw_score=Decimal("80.005")).weighted_score() == Decimal("80.00")
    assert scorecard(policy(), raw_score=Decimal("80.015")).weighted_score() == Decimal("80.02")


def universe_gap(**changes: object) -> HistoryGap:
    values: dict[str, object] = {
        "data_domain": DataDomain.EOD_MARKET_DATA,
        "starts_at": datetime(2026, 1, 1, tzinfo=UTC),
        "ends_at": datetime(2026, 1, 31, tzinfo=UTC),
        "affected_venue": "NSE",
        "affected_security_ids": (),
        "affected_universe_scope": "NIFTY_200",
        "severity": GapSeverity.CRITICAL,
        "evidence": EVIDENCE,
        "resolution_status": GapResolutionStatus.OPEN,
    }
    values.update(changes)
    return HistoryGap(**values)  # type: ignore[arg-type]


def membership(
    state: MembershipState,
    starts_at: datetime,
    ends_at: datetime,
) -> UniverseMembershipEvidence:
    return UniverseMembershipEvidence(
        "SYNTHETIC-SECURITY",
        "NIFTY_200",
        starts_at,
        ends_at,
        state,
        EVIDENCE,
    )


def gap_request(**changes: object) -> EvaluationRequest:
    values: dict[str, object] = {
        "required_history_start": datetime(2026, 1, 1, tzinfo=UTC),
        "latest_required_session": datetime(2026, 1, 31, tzinfo=UTC),
        "required_universe_scope": None,
    }
    values.update(changes)
    return request(**values)


def test_explicit_security_vs_universe_gap_unknown_membership_blocks() -> None:
    assert history_gap_relevant(universe_gap(), gap_request())


def test_effective_dated_member_blocks_and_proven_nonmember_does_not() -> None:
    start = datetime(2026, 1, 1, tzinfo=UTC)
    end = datetime(2026, 1, 31, tzinfo=UTC)
    assert history_gap_relevant(
        universe_gap(),
        gap_request(universe_membership_evidence=(membership(MembershipState.MEMBER, start, end),)),
    )
    assert not history_gap_relevant(
        universe_gap(),
        gap_request(
            universe_membership_evidence=(membership(MembershipState.NON_MEMBER, start, end),)
        ),
    )


def test_membership_changing_during_gap_blocks() -> None:
    assert history_gap_relevant(
        universe_gap(),
        gap_request(
            universe_membership_evidence=(
                membership(
                    MembershipState.NON_MEMBER,
                    datetime(2026, 1, 1, tzinfo=UTC),
                    datetime(2026, 1, 15, tzinfo=UTC),
                ),
                membership(
                    MembershipState.MEMBER,
                    datetime(2026, 1, 15, tzinfo=UTC),
                    datetime(2026, 1, 31, tzinfo=UTC),
                ),
            )
        ),
    )


def test_empty_requested_scope_fails_closed_for_relevant_gap() -> None:
    assert history_gap_relevant(
        universe_gap(),
        gap_request(required_security_ids=(), required_universe_scope=None),
    )


def test_gap_domain_venue_and_closed_interval_boundaries() -> None:
    candidate_request = gap_request()
    assert not history_gap_relevant(universe_gap(affected_venue="BSE"), candidate_request)
    assert not history_gap_relevant(
        universe_gap(data_domain=DataDomain.FINANCIAL_FACTS), candidate_request
    )
    boundary = datetime(2026, 1, 1, tzinfo=UTC)
    assert history_gap_relevant(
        universe_gap(starts_at=boundary, ends_at=boundary),
        gap_request(required_history_start=boundary, latest_required_session=boundary),
    )


def test_resolved_and_warning_history_gaps_do_not_block_gate() -> None:
    current_policy = policy()
    warning = universe_gap(severity=GapSeverity.WARNING)
    resolved = universe_gap(resolution_status=GapResolutionStatus.RESOLVED)
    result = evaluate_hard_gates(
        capabilities(history_gaps=(warning, resolved)),
        current_policy,
        registry(),
        request(),
        scorecard(current_policy),
    )
    assert result.passed


def test_evaluation_artifact_is_factory_controlled_and_validates() -> None:
    (
        current_capabilities,
        current_policy,
        current_registry,
        current_request,
        current_scorecard,
        artifact,
    ) = passing_context()
    with pytest.raises(TypeError, match="only be created"):
        EvaluationArtifact()
    assert validate_evaluation_artifact(
        artifact,
        current_capabilities,
        current_policy,
        current_registry,
        current_request,
        current_scorecard,
    )
    assert artifact.schema_version == EVALUATION_ARTIFACT_SCHEMA_VERSION


def test_internally_consistent_forged_passing_artifact_cannot_authorize_failure() -> None:
    current_policy = policy(purpose=Permission.UNKNOWN)
    current_capabilities = capabilities()
    current_registry = registry()
    current_request = request()
    current_scorecard = scorecard(current_policy)
    failed = evaluate_hard_gates(
        current_capabilities,
        current_policy,
        current_registry,
        current_request,
        current_scorecard,
    )
    assert not failed.passed
    forged = forged_artifact(
        failed,
        passed=True,
        reasons=(),
        weighted_score=Decimal("80.00"),
        scorecard_version=DEFAULT_SCORECARD_VERSION,
    )
    assert forged.artifact_id != failed.artifact_id
    assert not validate_evaluation_artifact(
        forged,
        current_capabilities,
        current_policy,
        current_registry,
        current_request,
        current_scorecard,
    )
    decision = publication_gate(
        evaluation_artifact=forged,
        capabilities=current_capabilities,
        policy=current_policy,
        lifecycle_registry=current_registry,
        request=current_request,
        scorecard=current_scorecard,
        stale=False,
        critical_missing=False,
    )
    assert decision.status is PublicationStatus.REJECTED
    assert decision.reasons[0].code == ReasonCode.EVALUATION_ARTIFACT_INVALID.value


@pytest.mark.parametrize(
    "changes",
    [
        {
            "passed": False,
            "reasons": (ReasonCode.PERMISSION_UNKNOWN,),
            "weighted_score": None,
            "scorecard_version": None,
        },
        {"weighted_score": Decimal("99.99")},
        {"scorecard_version": "SYNTHETIC-FORGED-SCORECARD"},
    ],
)
def test_internally_consistent_result_field_forgery_is_rejected(
    changes: dict[str, object],
) -> None:
    (
        current_capabilities,
        current_policy,
        current_registry,
        current_request,
        current_scorecard,
        artifact,
    ) = passing_context()
    forged = forged_artifact(artifact, **changes)
    assert not validate_evaluation_artifact(
        forged,
        current_capabilities,
        current_policy,
        current_registry,
        current_request,
        current_scorecard,
    )


def test_removing_failure_reason_from_consistent_artifact_is_rejected() -> None:
    current_policy = policy(purpose=Permission.UNKNOWN)
    current_scorecard = scorecard(current_policy)
    failed = evaluate_hard_gates(
        capabilities(), current_policy, registry(), request(), current_scorecard
    )
    assert failed.reasons
    forged = forged_artifact(failed, reasons=failed.reasons[1:])
    assert not validate_evaluation_artifact(
        forged,
        capabilities(),
        current_policy,
        registry(),
        request(),
        current_scorecard,
    )


def test_every_bound_input_snapshot_invalidates_stale_artifact() -> None:
    (
        current_capabilities,
        current_policy,
        current_registry,
        current_request,
        current_scorecard,
        artifact,
    ) = passing_context()
    contexts = (
        {
            "capabilities": replace(current_capabilities, version="SYNTHETIC-2"),
            "policy": current_policy,
            "lifecycle_registry": current_registry,
            "request": current_request,
            "scorecard": current_scorecard,
        },
        {
            "capabilities": current_capabilities,
            "policy": replace(current_policy, reviewer="SYNTHETIC-SECOND-REVIEWER"),
            "lifecycle_registry": current_registry,
            "request": current_request,
            "scorecard": current_scorecard,
        },
        {
            "capabilities": current_capabilities,
            "policy": current_policy,
            "lifecycle_registry": replace(
                current_registry, registry_version="SYNTHETIC-REGISTRY-2"
            ),
            "request": current_request,
            "scorecard": current_scorecard,
        },
        {
            "capabilities": current_capabilities,
            "policy": current_policy,
            "lifecycle_registry": current_registry,
            "request": replace(current_request, require_backup=True),
            "scorecard": current_scorecard,
        },
        {
            "capabilities": current_capabilities,
            "policy": current_policy,
            "lifecycle_registry": current_registry,
            "request": current_request,
            "scorecard": replace(current_scorecard, scorecard_version="SYNTHETIC-SCORECARD-2"),
        },
    )
    for context in contexts:
        decision = publication_gate(
            evaluation_artifact=artifact,
            **context,  # type: ignore[arg-type]
            stale=False,
            critical_missing=False,
        )
        assert decision.status is PublicationStatus.REJECTED
        assert decision.reasons[0].code == ReasonCode.EVALUATION_ARTIFACT_INVALID.value


def test_publication_accepts_valid_artifact_and_rejects_mutated_inputs() -> None:
    (
        current_capabilities,
        current_policy,
        current_registry,
        current_request,
        current_scorecard,
        artifact,
    ) = passing_context()
    accepted = publication_gate(
        evaluation_artifact=artifact,
        capabilities=current_capabilities,
        policy=current_policy,
        lifecycle_registry=current_registry,
        request=current_request,
        scorecard=current_scorecard,
        stale=False,
        critical_missing=False,
    )
    assert accepted.status is PublicationStatus.ACCEPTED
    rejected = publication_gate(
        evaluation_artifact=artifact,
        capabilities=current_capabilities,
        policy=current_policy,
        lifecycle_registry=current_registry,
        request=replace(current_request, require_backup=True),
        scorecard=current_scorecard,
        stale=False,
        critical_missing=False,
    )
    assert rejected.status is PublicationStatus.REJECTED
    assert rejected.reasons[0].code == ReasonCode.EVALUATION_ARTIFACT_INVALID.value


def test_failed_hard_gate_cannot_publish_accepted() -> None:
    current_policy = policy(purpose=Permission.UNKNOWN)
    artifact = evaluate_hard_gates(
        capabilities(), current_policy, registry(), request(), scorecard(current_policy)
    )
    decision = publication_gate(
        evaluation_artifact=artifact,
        capabilities=capabilities(),
        policy=current_policy,
        lifecycle_registry=registry(),
        request=request(),
        scorecard=scorecard(current_policy),
        stale=False,
        critical_missing=False,
    )
    assert decision.status is PublicationStatus.REJECTED


def test_eod_coverage_uses_caller_supplied_completed_session_boundaries() -> None:
    current_policy = policy()
    for evaluation_at in (
        datetime(2026, 7, 10, 14, tzinfo=UTC),
        datetime(2026, 7, 12, 9, tzinfo=UTC),
        datetime(2026, 8, 15, 9, tzinfo=UTC),
        LATEST_SESSION,
    ):
        candidate_request = request(at=evaluation_at)
        candidate_scorecard = scorecard(
            current_policy,
            assessed_at=min(evaluation_at, NOW),
        )
        result = evaluate_hard_gates(
            capabilities(),
            current_policy,
            registry(),
            candidate_request,
            candidate_scorecard,
        )
        assert ReasonCode.INSUFFICIENT_HISTORY not in result.reasons


def test_insufficient_final_session_fails() -> None:
    current_policy = policy()
    result = evaluate_hard_gates(
        capabilities(historical_end=LATEST_SESSION - timedelta(microseconds=1)),
        current_policy,
        registry(),
        request(),
        scorecard(current_policy),
    )
    assert ReasonCode.INSUFFICIENT_HISTORY in result.reasons


def test_deterministic_report_has_explicit_schema_and_versions() -> None:
    *_, artifact = passing_context()
    sections = {
        "schema_mapping_report": {"mapped": ["SYNTHETIC-ID"]},
        "missing_field_report": {"missing": []},
        "temporal_capability_report": {"pit": "SUPPORTED"},
        "licensing_capability_report": {"purpose": "PERMITTED"},
        "identity_conflict_report": {"conflicts": []},
        "action_completeness_report": {"complete": True},
    }
    first = deterministic_report("SYNTHETIC-PROVIDER", artifact, sections)
    second = deterministic_report("SYNTHETIC-PROVIDER", artifact, sections)
    assert first == second
    payload = __import__("json").loads(first[0])
    assert payload["report_schema_version"] == REPORT_SCHEMA_VERSION
    assert payload["evaluation_artifact_schema_version"] == EVALUATION_ARTIFACT_SCHEMA_VERSION
    assert payload["hard_gate"]["scorecard_version"] == DEFAULT_SCORECARD_VERSION
