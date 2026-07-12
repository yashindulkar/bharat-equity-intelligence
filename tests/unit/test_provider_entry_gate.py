from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from bharat_equity.application.provider_evaluation import (
    DEFAULT_WEIGHTS,
    EvaluationRequest,
    GateResult,
    deterministic_report,
    evaluate_hard_gates,
    publication_gate,
)
from bharat_equity.domain.errors import ReasonCode
from bharat_equity.domain.provider_policy import (
    CAPABILITY_NAMES,
    ApprovalStatus,
    CapabilityState,
    DataUsagePolicy,
    Permission,
    ProviderCapabilityRegistry,
    PublicationStatus,
    StructuredReason,
    UsagePurpose,
)

NOW = datetime(2026, 7, 13, tzinfo=UTC)


def capabilities(**changes: CapabilityState) -> ProviderCapabilityRegistry:
    values = {name: CapabilityState.SUPPORTED for name in CAPABILITY_NAMES}
    values.update(changes)
    return ProviderCapabilityRegistry(
        provider_id="SYNTHETIC-PROVIDER",
        product="SYNTHETIC-PRODUCT",
        version="1",
        capabilities=values,
        historical_start=NOW - timedelta(days=3650),
        historical_end=NOW + timedelta(days=1),
        known_history_gaps=(),
        capability_evidence={name: (f"SYNTHETIC-EVIDENCE-{name}",) for name in CAPABILITY_NAMES},
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
    return DataUsagePolicy(
        policy_id="SYNTHETIC-POLICY",
        provider_id="SYNTHETIC-PROVIDER",
        product="SYNTHETIC-PRODUCT",
        agreement_version="SYNTHETIC-1",
        effective_from=NOW - timedelta(days=30),
        effective_until=until or NOW + timedelta(days=30),
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
        post_termination_retention=Permission.PROHIBITED,
        deletion_obligations="SYNTHETIC deletion required",
        permitted_processing_geographies=("SYNTHETIC-JURISDICTION",),
        geographical_restrictions=("SYNTHETIC-FORBIDDEN-JURISDICTION",),
        evidence_reference="SYNTHETIC-EVIDENCE",
        reviewer="SYNTHETIC-REVIEWER",
        approved_at=NOW - timedelta(days=1),
        review_due_at=NOW + timedelta(days=10),
        external_ai_processing=Permission.PROHIBITED,
        approval_status=approval,
    )


def request(**changes: object) -> EvaluationRequest:
    values: dict[str, object] = {
        "at": NOW,
        "purpose": UsagePurpose.PRIVATE_HOUSEHOLD_RESEARCH,
        "user": "SYNTHETIC-OPERATOR",
        "processing_geography": "SYNTHETIC-JURISDICTION",
        "required_history_start": NOW - timedelta(days=1000),
    }
    values.update(changes)
    return EvaluationRequest(**values)  # type: ignore[arg-type]


def scores() -> dict[str, Decimal]:
    return {name: Decimal("80") for name in DEFAULT_WEIGHTS}


@pytest.mark.parametrize(
    ("candidate", "expected"),
    [
        (policy(purpose=Permission.UNKNOWN), ReasonCode.PERMISSION_UNKNOWN),
        (policy(purpose=Permission.PROHIBITED), ReasonCode.PURPOSE_NOT_PERMITTED),
        (policy(until=NOW - timedelta(seconds=1)), ReasonCode.AGREEMENT_EXPIRED),
        (policy(raw=Permission.PROHIBITED), ReasonCode.RAW_RETENTION_FORBIDDEN),
        (policy(approval=ApprovalStatus.PENDING), ReasonCode.PROVIDER_NOT_APPROVED),
    ],
)
def test_policy_hard_gates(candidate: DataUsagePolicy, expected: ReasonCode) -> None:
    result = evaluate_hard_gates(capabilities(), candidate, request(), scores())
    assert not result.passed
    assert expected in result.reasons
    assert result.weighted_score is None


def test_missing_pit_revision_delisted_history_and_identity_fail_closed() -> None:
    registry = capabilities(
        exact_publication_timestamps=CapabilityState.UNKNOWN,
        revisions_and_restatements=CapabilityState.UNKNOWN,
        delisted_coverage=CapabilityState.UNSUPPORTED,
    )
    result = evaluate_hard_gates(
        registry,
        policy(),
        request(critical_history_available=False, identifiers_unambiguous=False),
        scores(),
    )
    assert set(result.reasons) >= {
        ReasonCode.PIT_UNSUPPORTED,
        ReasonCode.REVISION_HANDLING_UNKNOWN,
        ReasonCode.DELISTED_COVERAGE_MISSING,
        ReasonCode.INSUFFICIENT_HISTORY,
        ReasonCode.IDENTITY_CONFLICT,
    }
    assert result.weighted_score is None


def test_score_exists_only_after_all_hard_gates_pass() -> None:
    result = evaluate_hard_gates(capabilities(), policy(), request(), scores())
    assert result.passed
    assert result.weighted_score == Decimal("80.00")


@pytest.mark.parametrize(
    "changes",
    [
        {"user": "SYNTHETIC-STRANGER"},
        {"processing_geography": "SYNTHETIC-OTHER"},
        {"use_external_ai": True},
        {"require_backup": True},
        {"agreement_terminated": True, "deletion_completed": False},
    ],
)
def test_user_geography_processing_and_termination_fail_closed(changes: dict[str, object]) -> None:
    assert not evaluate_hard_gates(capabilities(), policy(), request(**changes), scores()).passed


def test_provider_product_mismatch_and_history_gaps_fail() -> None:
    registry = capabilities()
    mismatched = ProviderCapabilityRegistry(
        provider_id="SYNTHETIC-OTHER",
        product=registry.product,
        version=registry.version,
        capabilities=registry.capabilities,
        historical_start=registry.historical_start,
        historical_end=registry.historical_end,
        known_history_gaps=("SYNTHETIC-GAP",),
        capability_evidence=registry.capability_evidence,
    )
    result = evaluate_hard_gates(mismatched, policy(), request(), scores())
    assert ReasonCode.PROVIDER_NOT_APPROVED in result.reasons
    assert ReasonCode.INSUFFICIENT_HISTORY in result.reasons


def test_publication_statuses_preserve_conflicts_and_block_stale_or_unapproved() -> None:
    conflict = StructuredReason(
        "FIELD_CONFLICT",
        "Competing close values",
        "close",
        ("SYNTHETIC-A", "SYNTHETIC-B"),
    )
    passed = GateResult(True, (), Decimal("80"))
    failed = GateResult(False, (ReasonCode.PROVIDER_NOT_APPROVED,), None)
    quarantined = publication_gate(
        provider_gate=passed, stale=False, critical_missing=True, conflicts=(conflict,)
    )
    assert quarantined.status is PublicationStatus.QUARANTINED
    assert quarantined.reasons[0].source_record_ids == ("SYNTHETIC-A", "SYNTHETIC-B")
    assert (
        publication_gate(provider_gate=passed, stale=True, critical_missing=False).status
        is PublicationStatus.REJECTED
    )
    assert (
        publication_gate(provider_gate=failed, stale=False, critical_missing=False).status
        is PublicationStatus.REJECTED
    )


def test_reports_are_deterministic_and_offline(monkeypatch: pytest.MonkeyPatch) -> None:
    def deny_network(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("network access forbidden")

    monkeypatch.setattr("socket.socket.connect", deny_network)
    gate = evaluate_hard_gates(capabilities(), policy(), request(), scores())
    sections = {
        "schema_mapping_report": {"mapped": ["SYNTHETIC-ID"]},
        "missing_field_report": {"missing": []},
        "temporal_capability_report": {"pit": "SUPPORTED"},
        "licensing_capability_report": {"purpose": "PERMITTED"},
        "identity_conflict_report": {"conflicts": []},
        "action_completeness_report": {"complete": True},
    }
    assert deterministic_report("SYNTHETIC-PROVIDER", gate, sections) == deterministic_report(
        "SYNTHETIC-PROVIDER", gate, sections
    )
