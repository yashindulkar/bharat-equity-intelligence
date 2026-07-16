from dataclasses import replace
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from bharat_equity.application.provider_evaluation import (
    DEFAULT_SCORECARD_VERSION,
    DEFAULT_WEIGHTS,
    REPORT_SCHEMA_VERSION,
    EvaluationRequest,
    GateResult,
    deterministic_report,
    evaluate_hard_gates,
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
    DataDomain,
    DataUsagePolicy,
    DeletionState,
    EvidenceReference,
    GapResolutionStatus,
    GapSeverity,
    HistoryGap,
    Permission,
    ProviderCapabilityRegistry,
    ProviderResponseEnvelope,
    ProviderScorecard,
    PublicationStatus,
    ReconciliationConflict,
    ScorecardEntry,
    ScoreDimension,
    TerminationDeletionLifecycle,
    UsagePurpose,
)

NOW = datetime(2026, 7, 13, 12, tzinfo=UTC)
HISTORY_START = datetime(2020, 1, 1, tzinfo=UTC)
LATEST_SESSION = datetime(2026, 7, 10, 10, tzinfo=UTC)
EVIDENCE = EvidenceReference("SYNTHETIC-EVIDENCE", "SYNTHETIC-1")


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
    until: datetime | None = None,
) -> DataUsagePolicy:
    purposes = {item: Permission.PROHIBITED for item in UsagePurpose}
    purposes[UsagePurpose.PRIVATE_HOUSEHOLD_RESEARCH] = purpose
    approved_at = NOW - timedelta(days=20) if approval is ApprovalStatus.APPROVED else None
    rejected_at = NOW - timedelta(days=1) if approval is ApprovalStatus.REJECTED else None
    review_due = NOW + timedelta(days=120) if approval is ApprovalStatus.APPROVED else None
    return DataUsagePolicy(
        policy_id="SYNTHETIC-POLICY",
        provider_id="SYNTHETIC-PROVIDER",
        product="SYNTHETIC-PRODUCT",
        agreement_version="SYNTHETIC-1",
        effective_from=NOW - timedelta(days=30),
        effective_until=until or NOW + timedelta(days=120),
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
        permitted_processing_geographies=("SYNTHETIC-JURISDICTION",),
        geographical_restrictions=("SYNTHETIC-FORBIDDEN-JURISDICTION",),
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
    *,
    raw_score: Decimal = Decimal("80"),
    weights: dict[ScoreDimension, Decimal] | None = None,
) -> ProviderScorecard:
    selected = weights or DEFAULT_WEIGHTS
    return ProviderScorecard(
        provider_id="SYNTHETIC-PROVIDER",
        product="SYNTHETIC-PRODUCT",
        product_version="SYNTHETIC-1",
        scorecard_version=DEFAULT_SCORECARD_VERSION,
        entries=tuple(
            ScorecardEntry(
                dimension=dimension,
                raw_score=raw_score,
                weight=selected[dimension],
                evidence_references=(EVIDENCE,),
                assessor="SYNTHETIC-ASSESSOR",
                assessed_at=NOW,
                method_version="SYNTHETIC-METHOD-1",
                explanation=f"SYNTHETIC explanation for {dimension.value}",
                confidence=ConfidenceLevel.MEDIUM,
            )
            for dimension in ScoreDimension
        ),
    )


def lifecycle(
    *,
    at: datetime,
    deadline: datetime,
    raw: DeletionState,
    backup: DeletionState,
    fixture: DeletionState,
    derived: DeletionState = DeletionState.NOT_DUE,
    audit: DeletionState = DeletionState.NOT_DUE,
) -> TerminationDeletionLifecycle:
    statuses = (raw, backup, fixture, derived, audit)
    evidence = (EVIDENCE,) if DeletionState.COMPLETED in statuses else ()
    return TerminationDeletionLifecycle(
        termination_at=at,
        deletion_deadline=deadline,
        raw_data_status=raw,
        backup_status=backup,
        fixture_status=fixture,
        derived_data_retention_permission=Permission.PERMITTED,
        derived_data_status=derived,
        audit_evidence_retention_permission=Permission.PERMITTED,
        audit_evidence_status=audit,
        deletion_verification_evidence=evidence,
    )


def conflict(
    status: ConflictResolutionStatus,
    *,
    severity: GapSeverity = GapSeverity.CRITICAL,
) -> ReconciliationConflict:
    reviewed = status is not ConflictResolutionStatus.UNRESOLVED
    return ReconciliationConflict(
        conflict_id=f"SYNTHETIC-CONFLICT-{status.value}",
        field="close",
        values=(
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
        tolerance_rule="SYNTHETIC-EXACT",
        tolerance_version="SYNTHETIC-1",
        measured_difference="1.00",
        severity=severity,
        resolution_status=status,
        correction_requirement=(
            CorrectionRequirement.CORRECTION_REQUIRED
            if status is ConflictResolutionStatus.UNRESOLVED
            else (
                CorrectionRequirement.NONE
                if status is ConflictResolutionStatus.INVALID_NON_REMEDIABLE
                else CorrectionRequirement.REPUBLICATION_REQUIRED
            )
        ),
        reviewer_evidence=EVIDENCE if reviewed else None,
        reviewed_at=NOW if reviewed else None,
    )


@pytest.mark.parametrize(
    ("candidate", "expected"),
    [
        (policy(purpose=Permission.UNKNOWN), ReasonCode.PERMISSION_UNKNOWN),
        (
            policy(purpose=Permission.PROHIBITED),
            ReasonCode.PURPOSE_NOT_PERMITTED,
        ),
        (
            policy(until=NOW - timedelta(seconds=1)),
            ReasonCode.AGREEMENT_EXPIRED,
        ),
        (
            policy(raw=Permission.PROHIBITED),
            ReasonCode.RAW_RETENTION_FORBIDDEN,
        ),
        (
            policy(approval=ApprovalStatus.PENDING),
            ReasonCode.PROVIDER_NOT_APPROVED,
        ),
    ],
)
def test_policy_hard_gates(
    candidate: DataUsagePolicy,
    expected: ReasonCode,
) -> None:
    result = evaluate_hard_gates(
        capabilities(),
        candidate,
        request(),
        scorecard(),
    )
    assert not result.passed
    assert expected in result.reasons
    assert result.weighted_score is None


def test_score_exists_only_after_all_hard_gates_pass() -> None:
    result = evaluate_hard_gates(
        capabilities(),
        policy(),
        request(),
        scorecard(),
    )
    assert result.passed
    assert result.weighted_score == Decimal("80.00")
    assert result.scorecard_version == DEFAULT_SCORECARD_VERSION


@pytest.mark.parametrize(
    ("evaluation_at", "latest_session"),
    [
        (
            datetime(2026, 7, 10, 14, tzinfo=UTC),
            LATEST_SESSION,
        ),
        (
            datetime(2026, 7, 12, 9, tzinfo=UTC),
            LATEST_SESSION,
        ),
        (
            datetime(2026, 8, 15, 9, tzinfo=UTC),
            LATEST_SESSION,
        ),
        (LATEST_SESSION, LATEST_SESSION),
    ],
)
def test_eod_coverage_uses_caller_supplied_completed_session(
    evaluation_at: datetime,
    latest_session: datetime,
) -> None:
    result = evaluate_hard_gates(
        capabilities(historical_end=LATEST_SESSION),
        policy(),
        request(at=evaluation_at, latest_required_session=latest_session),
        scorecard(),
    )
    assert result.passed


def test_insufficient_final_session_fails() -> None:
    result = evaluate_hard_gates(
        capabilities(historical_end=LATEST_SESSION - timedelta(seconds=1)),
        policy(),
        request(),
        scorecard(),
    )
    assert ReasonCode.INSUFFICIENT_HISTORY in result.reasons


def test_intersecting_critical_gap_blocks_but_irrelevant_gap_does_not() -> None:
    blocking = HistoryGap(
        DataDomain.EOD_MARKET_DATA,
        datetime(2026, 1, 1, tzinfo=UTC),
        datetime(2026, 1, 2, tzinfo=UTC),
        "NSE",
        ("SYNTHETIC-SECURITY",),
        None,
        GapSeverity.CRITICAL,
        EVIDENCE,
        GapResolutionStatus.OPEN,
    )
    irrelevant = replace(
        blocking,
        affected_security_ids=("SYNTHETIC-OTHER",),
    )
    assert not evaluate_hard_gates(
        capabilities(history_gaps=(blocking,)),
        policy(),
        request(),
        scorecard(),
    ).passed
    assert evaluate_hard_gates(
        capabilities(history_gaps=(irrelevant,)),
        policy(),
        request(),
        scorecard(),
    ).passed
    assert evaluate_hard_gates(
        capabilities(
            history_gaps=(
                replace(blocking, severity=GapSeverity.WARNING),
                replace(
                    blocking,
                    resolution_status=GapResolutionStatus.RESOLVED,
                ),
            )
        ),
        policy(),
        request(),
        scorecard(),
    ).passed


def test_overdue_prohibited_post_termination_retention_fails_closed() -> None:
    termination = NOW - timedelta(days=10)
    deadline = NOW - timedelta(days=1)
    result = evaluate_hard_gates(
        capabilities(),
        policy(),
        request(
            termination_lifecycle=lifecycle(
                at=termination,
                deadline=deadline,
                raw=DeletionState.OVERDUE,
                backup=DeletionState.OVERDUE,
                fixture=DeletionState.OVERDUE,
            )
        ),
        scorecard(),
    )
    assert ReasonCode.AGREEMENT_EXPIRED in result.reasons
    assert ReasonCode.TERMINATION_DELETION_OVERDUE in result.reasons


def test_permitted_derived_and_audit_retention_do_not_create_overdue_reason() -> None:
    termination = NOW - timedelta(days=10)
    deadline = NOW - timedelta(days=1)
    result = evaluate_hard_gates(
        capabilities(),
        policy(),
        request(
            termination_lifecycle=lifecycle(
                at=termination,
                deadline=deadline,
                raw=DeletionState.COMPLETED,
                backup=DeletionState.COMPLETED,
                fixture=DeletionState.COMPLETED,
            )
        ),
        scorecard(),
    )
    assert ReasonCode.AGREEMENT_EXPIRED in result.reasons
    assert ReasonCode.TERMINATION_DELETION_OVERDUE not in result.reasons


def test_deletion_due_state_is_valid_at_exact_deadline() -> None:
    result = evaluate_hard_gates(
        capabilities(),
        policy(),
        request(
            termination_lifecycle=lifecycle(
                at=NOW - timedelta(days=1),
                deadline=NOW,
                raw=DeletionState.DUE,
                backup=DeletionState.DUE,
                fixture=DeletionState.DUE,
            )
        ),
        scorecard(),
    )
    assert ReasonCode.AGREEMENT_EXPIRED in result.reasons
    assert ReasonCode.TERMINATION_DELETION_OVERDUE not in result.reasons


def test_envelope_gate_checks_bindings_schema_and_payload() -> None:
    payload = b"SYNTHETIC-PAYLOAD"
    digest = "sha256:c5b86bf2eb1a69ebc2991ed5fc9ef48dcf074462bd978490708d43386444d6a2"
    envelope = ProviderResponseEnvelope(
        provider_id="SYNTHETIC-PROVIDER",
        product="SYNTHETIC-PRODUCT",
        product_version="SYNTHETIC-1",
        request_id="SYNTHETIC-REQUEST",
        source_record_id="SYNTHETIC-SOURCE",
        retrieved_at=NOW,
        published_at=NOW - timedelta(minutes=1),
        payload_schema_version="SYNTHETIC-SCHEMA-1",
        content_type="application/json",
        immutable_payload_hash=digest,
        policy_id="SYNTHETIC-POLICY",
        intended_usage_purpose=UsagePurpose.PRIVATE_HOUSEHOLD_RESEARCH,
    )
    assert validate_provider_envelope(
        envelope,
        payload,
        capabilities(),
        policy(),
        request(),
        frozenset({"SYNTHETIC-SCHEMA-1"}),
    ).passed
    mismatches = (
        replace(envelope, provider_id="SYNTHETIC-OTHER"),
        replace(envelope, product="SYNTHETIC-OTHER"),
        replace(envelope, policy_id="SYNTHETIC-OTHER"),
        replace(
            envelope,
            intended_usage_purpose=UsagePurpose.BACKTESTING,
        ),
    )
    for candidate in mismatches:
        result = validate_provider_envelope(
            candidate,
            payload,
            capabilities(),
            policy(),
            request(),
            frozenset({"SYNTHETIC-SCHEMA-1"}),
        )
        assert ReasonCode.ENVELOPE_MISMATCH in result.reasons
    schema_result = validate_provider_envelope(
        replace(envelope, payload_schema_version="SYNTHETIC-SCHEMA-2"),
        payload,
        capabilities(),
        policy(),
        request(),
        frozenset({"SYNTHETIC-SCHEMA-1"}),
    )
    assert ReasonCode.SCHEMA_NOT_ALLOWED in schema_result.reasons
    payload_result = validate_provider_envelope(
        envelope,
        b"SYNTHETIC-CORRUPTED",
        capabilities(),
        policy(),
        request(),
        frozenset({"SYNTHETIC-SCHEMA-1"}),
    )
    assert ReasonCode.EVIDENCE_INTEGRITY_FAILURE in payload_result.reasons
    expired_result = validate_provider_envelope(
        replace(
            envelope,
            retrieved_at=NOW + timedelta(days=121),
            published_at=NOW + timedelta(days=120),
        ),
        payload,
        capabilities(),
        policy(),
        request(at=NOW + timedelta(days=121)),
        frozenset({"SYNTHETIC-SCHEMA-1"}),
    )
    assert ReasonCode.AGREEMENT_EXPIRED in expired_result.reasons


@pytest.mark.parametrize(
    ("candidate", "expected"),
    [
        (
            conflict(ConflictResolutionStatus.UNRESOLVED),
            PublicationStatus.QUARANTINED,
        ),
        (
            conflict(ConflictResolutionStatus.INVALID_NON_REMEDIABLE),
            PublicationStatus.REJECTED,
        ),
        (
            conflict(ConflictResolutionStatus.RESOLVED_APPROVED),
            PublicationStatus.ACCEPTED_WITH_WARNINGS,
        ),
        (
            conflict(
                ConflictResolutionStatus.UNRESOLVED,
                severity=GapSeverity.WARNING,
            ),
            PublicationStatus.ACCEPTED_WITH_WARNINGS,
        ),
    ],
)
def test_reconciliation_publication_transitions(
    candidate: ReconciliationConflict,
    expected: PublicationStatus,
) -> None:
    decision = publication_gate(
        provider_gate=GateResult(
            True,
            (),
            Decimal("80"),
            DEFAULT_SCORECARD_VERSION,
        ),
        stale=False,
        critical_missing=False,
        reconciliation_conflicts=(candidate,),
    )
    assert decision.status is expected
    assert decision.reconciliation_conflicts == (candidate,)


def test_no_conflict_uses_normal_publication_path() -> None:
    decision = publication_gate(
        provider_gate=GateResult(
            True,
            (),
            Decimal("80"),
            DEFAULT_SCORECARD_VERSION,
        ),
        stale=False,
        critical_missing=False,
    )
    assert decision.status is PublicationStatus.ACCEPTED


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
            values=(
                base.values[0],
                replace(base.values[1], value="100.00"),
            ),
        )


def test_reconciliation_requires_nonblank_values_and_review_evidence() -> None:
    base = conflict(ConflictResolutionStatus.UNRESOLVED)
    with pytest.raises(ValueError):
        replace(base.values[0], semantic_basis="")
    with pytest.raises(ValueError, match="evidence"):
        replace(
            base,
            resolution_status=ConflictResolutionStatus.RESOLVED_APPROVED,
            reviewer_evidence=None,
            reviewed_at=NOW,
        )
    with pytest.raises(ValueError, match="cannot carry"):
        replace(base, reviewer_evidence=EVIDENCE, reviewed_at=NOW)


@pytest.mark.parametrize(
    "changes",
    [
        {"permitted_users": ("",)},
        {"permitted_processing_geographies": ("",)},
        {"approved_at": NOW + timedelta(days=121)},
        {"review_due_at": NOW - timedelta(days=21)},
        {
            "approval_status": ApprovalStatus.REJECTED,
            "approved_at": NOW - timedelta(days=1),
            "rejected_at": NOW,
            "review_due_at": None,
        },
        {
            "approval_status": ApprovalStatus.REJECTED,
            "approved_at": None,
            "rejected_at": NOW + timedelta(days=121),
            "review_due_at": None,
        },
        {"evidence_references": ()},
    ],
)
def test_invalid_policy_invariants_fail_at_construction(
    changes: dict[str, object],
) -> None:
    with pytest.raises((TypeError, ValueError)):
        replace(policy(), **changes)


def test_permission_map_requires_permission_enum_members() -> None:
    invalid: dict[UsagePurpose, Permission] = dict(policy().permitted_purposes)
    invalid[UsagePurpose.PRIVATE_HOUSEHOLD_RESEARCH] = "PERMITTED"  # type: ignore[assignment]
    with pytest.raises(TypeError, match="Permission"):
        replace(policy(), permitted_purposes=invalid)


@pytest.mark.parametrize("value", [Decimal("NaN"), Decimal("Infinity")])
def test_non_finite_scores_fail(value: Decimal) -> None:
    with pytest.raises(ValueError):
        scorecard(raw_score=value)


def test_invalid_weight_total_fails() -> None:
    invalid = dict(DEFAULT_WEIGHTS)
    invalid[ScoreDimension.COST] = Decimal("0.06")
    with pytest.raises(ValueError, match="sum exactly"):
        scorecard(weights=invalid)


def test_scorecard_requires_exact_dimensions_and_evidence() -> None:
    valid = scorecard()
    with pytest.raises(ValueError, match="complete"):
        replace(valid, entries=valid.entries[:-1])
    with pytest.raises(ValueError, match="evidence"):
        replace(valid.entries[0], evidence_references=())


def test_deterministic_report_has_explicit_schema_and_versions() -> None:
    gate = evaluate_hard_gates(
        capabilities(),
        policy(),
        request(),
        scorecard(),
    )
    sections = {
        "schema_mapping_report": {"mapped": ["SYNTHETIC-ID"]},
        "missing_field_report": {"missing": []},
        "temporal_capability_report": {"pit": "SUPPORTED"},
        "licensing_capability_report": {"purpose": "PERMITTED"},
        "identity_conflict_report": {"conflicts": []},
        "action_completeness_report": {"complete": True},
    }
    first = deterministic_report("SYNTHETIC-PROVIDER", gate, sections)
    second = deterministic_report("SYNTHETIC-PROVIDER", gate, sections)
    assert first == second
    payload = __import__("json").loads(first[0])
    assert payload["report_schema_version"] == REPORT_SCHEMA_VERSION
    assert payload["hard_gate"]["scorecard_version"] == DEFAULT_SCORECARD_VERSION
