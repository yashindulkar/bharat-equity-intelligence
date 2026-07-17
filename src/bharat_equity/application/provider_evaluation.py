"""Executable real-data entry gates and deterministic synthetic evaluation reports."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from types import MappingProxyType
from typing import Any

from bharat_equity.domain.errors import ReasonCode
from bharat_equity.domain.models import require_text, require_utc
from bharat_equity.domain.provider_policy import (
    ApprovalStatus,
    CapabilityState,
    ConflictResolutionStatus,
    DataCategory,
    DataDomain,
    DataUsagePolicy,
    DispositionState,
    GapResolutionStatus,
    GapSeverity,
    GeographyScope,
    HistoryGap,
    MembershipState,
    Permission,
    ProviderCapabilityRegistry,
    ProviderResponseEnvelope,
    ProviderScorecard,
    PublicationDecision,
    PublicationStatus,
    ReconciliationConflict,
    RemediationStatus,
    ScoreDimension,
    StructuredReason,
    TerminationDeletionLifecycle,
    TerminationLifecycleRegistry,
    UniverseMembershipEvidence,
    UsagePurpose,
    contract_snapshot_id,
)

REPORT_SCHEMA_VERSION = "2.0.0"
EVALUATION_ARTIFACT_SCHEMA_VERSION = "1.0.0"
DEFAULT_SCORECARD_VERSION = "research-defaults-1.0.0"
DEFAULT_WEIGHTS: Mapping[ScoreDimension, Decimal] = MappingProxyType(
    {
        ScoreDimension.PIT_CORRECTNESS: Decimal("0.25"),
        ScoreDimension.LICENSING_AND_RETENTION: Decimal("0.20"),
        ScoreDimension.SECURITY_MASTER: Decimal("0.15"),
        ScoreDimension.CORPORATE_ACTIONS: Decimal("0.10"),
        ScoreDimension.FINANCIAL_STATEMENTS: Decimal("0.10"),
        ScoreDimension.HISTORY_AND_DELISTINGS: Decimal("0.10"),
        ScoreDimension.RELIABILITY_SUPPORT: Decimal("0.05"),
        ScoreDimension.COST: Decimal("0.05"),
    }
)


@dataclass(frozen=True, slots=True)
class EvaluationRequest:
    at: datetime
    purpose: UsagePurpose
    user: str
    processing_geography: str
    required_history_start: datetime
    latest_required_session: datetime
    required_data_domain: DataDomain = DataDomain.EOD_MARKET_DATA
    required_venue: str = "NSE"
    required_security_ids: tuple[str, ...] = ()
    required_universe_scope: str | None = "NIFTY_200"
    universe_membership_evidence: tuple[UniverseMembershipEvidence, ...] = ()
    use_external_ai: bool = False
    create_derived_data: bool = False
    require_backup: bool = False
    require_citation: bool = False
    require_historical: bool = True
    require_raw_retention: bool = True
    require_delisted: bool = True
    critical_history_available: bool = True
    identifiers_unambiguous: bool = True

    def __post_init__(self) -> None:
        for name in ("at", "required_history_start", "latest_required_session"):
            require_utc(getattr(self, name), name)
        for name in ("user", "processing_geography", "required_venue"):
            require_text(getattr(self, name), name)
        if self.processing_geography != self.processing_geography.strip().upper():
            raise ValueError("processing_geography must be canonical uppercase")
        if self.latest_required_session < self.required_history_start:
            raise ValueError("latest_required_session must not precede required_history_start")
        for security_id in self.required_security_ids:
            require_text(security_id, "required_security_id")
        if len(set(self.required_security_ids)) != len(self.required_security_ids):
            raise ValueError("required_security_ids must be unique")
        if self.required_universe_scope is not None:
            require_text(self.required_universe_scope, "required_universe_scope")


def _request_snapshot_id(request: EvaluationRequest) -> str:
    payload = {
        "at": request.at.isoformat(),
        "purpose": request.purpose.value,
        "user": request.user,
        "processing_geography": request.processing_geography,
        "required_history_start": request.required_history_start.isoformat(),
        "latest_required_session": request.latest_required_session.isoformat(),
        "required_data_domain": request.required_data_domain.value,
        "required_venue": request.required_venue,
        "required_security_ids": list(request.required_security_ids),
        "required_universe_scope": request.required_universe_scope,
        "universe_membership_evidence": [
            contract_snapshot_id(item) for item in request.universe_membership_evidence
        ],
        "use_external_ai": request.use_external_ai,
        "create_derived_data": request.create_derived_data,
        "require_backup": request.require_backup,
        "require_citation": request.require_citation,
        "require_historical": request.require_historical,
        "require_raw_retention": request.require_raw_retention,
        "require_delisted": request.require_delisted,
        "critical_history_available": request.critical_history_available,
        "identifiers_unambiguous": request.identifiers_unambiguous,
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return f"sha256:{hashlib.sha256(canonical.encode('utf-8')).hexdigest()}"


@dataclass(frozen=True, slots=True, init=False)
class EvaluationArtifact:
    """Deterministic, content-addressed audit record of hard-gate evaluation."""

    schema_version: str
    artifact_id: str
    passed: bool
    reasons: tuple[ReasonCode, ...]
    weighted_score: Decimal | None
    scorecard_version: str | None
    capability_snapshot_id: str
    policy_snapshot_id: str
    lifecycle_registry_snapshot_id: str
    lifecycle_snapshot_id: str | None
    scorecard_snapshot_id: str
    request_snapshot_id: str
    evaluated_at: datetime

    def __init__(self) -> None:
        raise TypeError("EvaluationArtifact can only be created by evaluate_hard_gates")


@dataclass(frozen=True, slots=True)
class EnvelopeGateResult:
    passed: bool
    reasons: tuple[ReasonCode, ...]

    def __post_init__(self) -> None:
        if self.passed and self.reasons:
            raise ValueError("passing envelope gate cannot carry reasons")
        if not self.passed and not self.reasons:
            raise ValueError("failed envelope gate requires reasons")


def _overlaps(
    left_start: datetime, left_end: datetime, right_start: datetime, right_end: datetime
) -> bool:
    """Closed intervals overlap when they share any instant, including either boundary."""

    return left_start <= right_end and right_start <= left_end


def _proven_nonmember(
    security_id: str,
    universe_scope: str,
    starts_at: datetime,
    ends_at: datetime,
    request: EvaluationRequest,
) -> bool:
    records = tuple(
        item
        for item in request.universe_membership_evidence
        if item.security_id == security_id
        and item.universe_scope == universe_scope
        and item.evidence.available_at is not None
        and item.evidence.available_at <= request.at
        and _overlaps(item.effective_from, item.effective_until, starts_at, ends_at)
    )
    if any(item.state is MembershipState.MEMBER for item in records):
        return False
    intervals = sorted(
        (
            (max(item.effective_from, starts_at), min(item.effective_until, ends_at))
            for item in records
            if item.state is MembershipState.NON_MEMBER
        ),
        key=lambda item: (item[0], item[1]),
    )
    if not intervals or intervals[0][0] > starts_at:
        return False
    covered_until = intervals[0][1]
    for interval_start, interval_end in intervals[1:]:
        if interval_start > covered_until:
            return False
        covered_until = max(covered_until, interval_end)
    return covered_until >= ends_at


def history_gap_relevant(gap: HistoryGap, request: EvaluationRequest) -> bool:
    """Return true unless trustworthy request-cutoff evidence proves gap disjointness."""

    if gap.data_domain is not request.required_data_domain:
        return False
    if gap.affected_venue != request.required_venue:
        return False
    if not _overlaps(
        gap.starts_at,
        gap.ends_at,
        request.required_history_start,
        request.latest_required_session,
    ):
        return False
    overlap_start = max(gap.starts_at, request.required_history_start)
    overlap_end = min(gap.ends_at, request.latest_required_session)
    gap_securities = set(gap.affected_security_ids)
    request_securities = set(request.required_security_ids)
    if gap_securities & request_securities:
        return True
    if gap.affected_universe_scope is not None:
        if gap.affected_universe_scope == request.required_universe_scope:
            return True
        if not request_securities:
            return True
        if any(
            not _proven_nonmember(
                security_id,
                gap.affected_universe_scope,
                overlap_start,
                overlap_end,
                request,
            )
            for security_id in request_securities
        ):
            return True
    if request.required_universe_scope is not None and gap_securities:
        if any(
            not _proven_nonmember(
                security_id,
                request.required_universe_scope,
                overlap_start,
                overlap_end,
                request,
            )
            for security_id in gap_securities
        ):
            return True
    if not gap_securities and gap.affected_universe_scope is None:
        return True
    if not request_securities and request.required_universe_scope is None:
        return True
    return False


def _policy_category_permissions(policy: DataUsagePolicy) -> Mapping[DataCategory, Permission]:
    return {
        DataCategory.RAW_DATA: policy.post_termination_raw_data,
        DataCategory.BACKUPS: policy.post_termination_backup,
        DataCategory.TEST_FIXTURES: policy.post_termination_fixtures,
        DataCategory.DERIVED_DATA: policy.post_termination_derived_data,
        DataCategory.AUDIT_EVIDENCE: policy.post_termination_audit_evidence,
    }


def _termination_reasons(
    policy: DataUsagePolicy,
    lifecycle_registry: TerminationLifecycleRegistry,
    request: EvaluationRequest,
) -> tuple[set[ReasonCode], TerminationDeletionLifecycle | None]:
    if policy.termination_at is None or request.at < policy.termination_at:
        return set(), None
    reasons = {ReasonCode.AGREEMENT_EXPIRED}
    lifecycle = lifecycle_registry.exact_record(policy)
    if lifecycle is None:
        substitution = any(
            item.policy_id == policy.policy_id
            or item.termination_event_id == policy.termination_event_id
            for item in lifecycle_registry.records
        )
        reasons.add(
            ReasonCode.TERMINATION_LIFECYCLE_MISMATCH
            if substitution
            else ReasonCode.TERMINATION_LIFECYCLE_MISSING
        )
        return reasons, None
    if lifecycle.termination_at != policy.termination_at:
        reasons.add(ReasonCode.TERMINATION_LIFECYCLE_MISMATCH)
        return reasons, lifecycle
    expected_permissions = _policy_category_permissions(policy)
    for disposition in lifecycle.dispositions:
        expected = expected_permissions[disposition.category]
        if disposition.contractual_permission is not expected:
            reasons.add(ReasonCode.TERMINATION_LIFECYCLE_MISMATCH)
            continue
        if expected is Permission.UNKNOWN:
            reasons.add(ReasonCode.PERMISSION_UNKNOWN)
            continue
        if expected is Permission.PERMITTED:
            if disposition.state not in (
                DispositionState.RETAINED,
                DispositionState.COMPLETED,
            ):
                reasons.add(ReasonCode.TERMINATION_DELETION_EVIDENCE_MISSING)
            continue
        if request.at > disposition.applicable_deadline:
            if disposition.state is not DispositionState.COMPLETED:
                reasons.add(ReasonCode.TERMINATION_DELETION_OVERDUE)
        elif request.at == disposition.applicable_deadline:
            if disposition.state not in (DispositionState.DUE, DispositionState.COMPLETED):
                reasons.add(ReasonCode.TERMINATION_DELETION_EVIDENCE_MISSING)
        elif disposition.state not in (DispositionState.NOT_DUE, DispositionState.COMPLETED):
            reasons.add(ReasonCode.TERMINATION_DELETION_EVIDENCE_MISSING)
    return reasons, lifecycle


def _artifact_content(
    *,
    passed: bool,
    reasons: tuple[ReasonCode, ...],
    weighted_score: Decimal | None,
    scorecard_version: str | None,
    capability_snapshot_id: str,
    policy_snapshot_id: str,
    lifecycle_registry_snapshot_id: str,
    lifecycle_snapshot_id: str | None,
    scorecard_snapshot_id: str,
    request_snapshot_id: str,
    evaluated_at: datetime,
) -> dict[str, Any]:
    return {
        "schema_version": EVALUATION_ARTIFACT_SCHEMA_VERSION,
        "passed": passed,
        "reasons": [reason.value for reason in reasons],
        "weighted_score": None if weighted_score is None else str(weighted_score),
        "scorecard_version": scorecard_version,
        "capability_snapshot_id": capability_snapshot_id,
        "policy_snapshot_id": policy_snapshot_id,
        "lifecycle_registry_snapshot_id": lifecycle_registry_snapshot_id,
        "lifecycle_snapshot_id": lifecycle_snapshot_id,
        "scorecard_snapshot_id": scorecard_snapshot_id,
        "request_snapshot_id": request_snapshot_id,
        "evaluated_at": evaluated_at.isoformat(),
    }


def _artifact_id(content: dict[str, Any]) -> str:
    payload = json.dumps(content, sort_keys=True, separators=(",", ":"))
    return f"sha256:{hashlib.sha256(payload.encode('utf-8')).hexdigest()}"


def _create_artifact(
    *,
    passed: bool,
    reasons: tuple[ReasonCode, ...],
    weighted_score: Decimal | None,
    scorecard_version: str | None,
    capabilities: ProviderCapabilityRegistry,
    policy: DataUsagePolicy,
    lifecycle_registry: TerminationLifecycleRegistry,
    lifecycle: TerminationDeletionLifecycle | None,
    scorecard: ProviderScorecard,
    request: EvaluationRequest,
) -> EvaluationArtifact:
    capability_snapshot_id = contract_snapshot_id(capabilities)
    policy_snapshot_id = contract_snapshot_id(policy)
    lifecycle_registry_snapshot_id = contract_snapshot_id(lifecycle_registry)
    lifecycle_snapshot_id = None if lifecycle is None else contract_snapshot_id(lifecycle)
    scorecard_snapshot_id = contract_snapshot_id(scorecard)
    request_snapshot_id = _request_snapshot_id(request)
    content = _artifact_content(
        passed=passed,
        reasons=reasons,
        weighted_score=weighted_score,
        scorecard_version=scorecard_version,
        capability_snapshot_id=capability_snapshot_id,
        policy_snapshot_id=policy_snapshot_id,
        lifecycle_registry_snapshot_id=lifecycle_registry_snapshot_id,
        lifecycle_snapshot_id=lifecycle_snapshot_id,
        scorecard_snapshot_id=scorecard_snapshot_id,
        request_snapshot_id=request_snapshot_id,
        evaluated_at=request.at,
    )
    artifact = object.__new__(EvaluationArtifact)
    values: dict[str, object] = {
        "schema_version": EVALUATION_ARTIFACT_SCHEMA_VERSION,
        "artifact_id": _artifact_id(content),
        "passed": passed,
        "reasons": reasons,
        "weighted_score": weighted_score,
        "scorecard_version": scorecard_version,
        "capability_snapshot_id": capability_snapshot_id,
        "policy_snapshot_id": policy_snapshot_id,
        "lifecycle_registry_snapshot_id": lifecycle_registry_snapshot_id,
        "lifecycle_snapshot_id": lifecycle_snapshot_id,
        "scorecard_snapshot_id": scorecard_snapshot_id,
        "request_snapshot_id": request_snapshot_id,
        "evaluated_at": request.at,
    }
    for name, value in values.items():
        object.__setattr__(artifact, name, value)
    return artifact


def evaluate_hard_gates(
    capabilities: ProviderCapabilityRegistry,
    policy: DataUsagePolicy,
    lifecycle_registry: TerminationLifecycleRegistry,
    request: EvaluationRequest,
    scorecard: ProviderScorecard,
) -> EvaluationArtifact:
    reasons: set[ReasonCode] = set()
    if (capabilities.provider_id, capabilities.product) != (policy.provider_id, policy.product):
        reasons.add(ReasonCode.PROVIDER_NOT_APPROVED)
    policy_snapshot = contract_snapshot_id(policy)
    if (
        scorecard.provider_id,
        scorecard.product,
        scorecard.product_version,
    ) != (capabilities.provider_id, capabilities.product, capabilities.version):
        reasons.add(ReasonCode.PROVIDER_NOT_APPROVED)
    if (
        scorecard.policy_id,
        scorecard.agreement_version,
        scorecard.policy_snapshot_id,
    ) != (policy.policy_id, policy.agreement_version, policy_snapshot):
        reasons.add(ReasonCode.SCORECARD_POLICY_MISMATCH)
    if scorecard.assessed_at > request.at or any(
        entry.assessed_at > request.at for entry in scorecard.entries
    ):
        reasons.add(ReasonCode.SCORECARD_FUTURE_ASSESSMENT)
    scorecard_evidence = (
        *scorecard.evidence_references,
        *(evidence for entry in scorecard.entries for evidence in entry.evidence_references),
    )
    if any(
        evidence.available_at is None or evidence.available_at > request.at
        for evidence in scorecard_evidence
    ):
        reasons.add(ReasonCode.SCORECARD_FUTURE_EVIDENCE)
    if request.user not in policy.permitted_users:
        reasons.add(ReasonCode.PURPOSE_NOT_PERMITTED)
    geography = policy.processing_geography
    if (
        geography.scope is GeographyScope.JURISDICTIONS
        and request.processing_geography not in geography.jurisdiction_ids
    ):
        reasons.add(ReasonCode.PROCESSING_GEOGRAPHY_UNKNOWN)
    if request.processing_geography in policy.geographical_restrictions:
        reasons.add(ReasonCode.PURPOSE_NOT_PERMITTED)
    permission = policy.permitted_purposes[request.purpose]
    if policy.approval_status is not ApprovalStatus.APPROVED:
        reasons.add(ReasonCode.PROVIDER_NOT_APPROVED)
    if policy.approved_at is None or policy.approved_at > request.at:
        reasons.add(ReasonCode.PROVIDER_NOT_APPROVED)
    if policy.review_due_at is not None and request.at >= policy.review_due_at:
        reasons.add(ReasonCode.PROVIDER_NOT_APPROVED)
    if permission is Permission.UNKNOWN:
        reasons.add(ReasonCode.PERMISSION_UNKNOWN)
    elif permission is Permission.PROHIBITED:
        reasons.add(ReasonCode.PURPOSE_NOT_PERMITTED)
    if request.at < policy.effective_from:
        reasons.add(ReasonCode.AGREEMENT_EXPIRED)
    if request.require_historical and any(
        capabilities.capabilities[name] is not CapabilityState.SUPPORTED
        for name in (
            "historical_depth",
            "historical_symbol_support",
            "exact_publication_timestamps",
            "historical_constituents",
            "stable_identifiers",
        )
    ):
        reasons.add(ReasonCode.PIT_UNSUPPORTED)
    if request.require_historical and (
        capabilities.historical_start is None
        or capabilities.historical_end is None
        or capabilities.historical_start > request.required_history_start
        or capabilities.historical_end < request.latest_required_session
    ):
        reasons.add(ReasonCode.INSUFFICIENT_HISTORY)
    if any(
        gap.severity is GapSeverity.CRITICAL
        and gap.resolution_status is GapResolutionStatus.OPEN
        and history_gap_relevant(gap, request)
        for gap in capabilities.history_gaps
    ):
        reasons.add(ReasonCode.INSUFFICIENT_HISTORY)
    if not request.critical_history_available:
        reasons.add(ReasonCode.INSUFFICIENT_HISTORY)
    if not request.identifiers_unambiguous:
        reasons.add(ReasonCode.IDENTITY_CONFLICT)
    if request.require_raw_retention and policy.raw_retention is not Permission.PERMITTED:
        reasons.add(ReasonCode.RAW_RETENTION_FORBIDDEN)
    if (
        request.require_raw_retention
        and capabilities.capabilities["raw_retention_support"] is not CapabilityState.SUPPORTED
    ):
        reasons.add(ReasonCode.RAW_RETENTION_FORBIDDEN)
    if capabilities.capabilities["revisions_and_restatements"] is not CapabilityState.SUPPORTED:
        reasons.add(ReasonCode.REVISION_HANDLING_UNKNOWN)
    if (
        request.require_delisted
        and capabilities.capabilities["delisted_coverage"] is not CapabilityState.SUPPORTED
    ):
        reasons.add(ReasonCode.DELISTED_COVERAGE_MISSING)
    specific_permission = {
        UsagePurpose.BACKTESTING: policy.backtesting,
        UsagePurpose.MODEL_TRAINING: policy.model_training,
        UsagePurpose.INTERNAL_DISPLAY: policy.display,
        UsagePurpose.TEST_FIXTURES: policy.fixtures,
        UsagePurpose.PRIVATE_HOUSEHOLD_RESEARCH: Permission.PERMITTED,
    }[request.purpose]
    if specific_permission is not Permission.PERMITTED:
        reasons.add(ReasonCode.PURPOSE_NOT_PERMITTED)
    purpose_capability = {
        UsagePurpose.BACKTESTING: "backtesting_support",
        UsagePurpose.MODEL_TRAINING: "model_training_support",
        UsagePurpose.INTERNAL_DISPLAY: "display_support",
        UsagePurpose.TEST_FIXTURES: "test_fixture_support",
        UsagePurpose.PRIVATE_HOUSEHOLD_RESEARCH: None,
    }[request.purpose]
    if (
        purpose_capability is not None
        and capabilities.capabilities[purpose_capability] is not CapabilityState.SUPPORTED
    ):
        reasons.add(ReasonCode.PURPOSE_NOT_PERMITTED)
    if request.create_derived_data and policy.derived_data is not Permission.PERMITTED:
        reasons.add(ReasonCode.PURPOSE_NOT_PERMITTED)
    if (
        request.create_derived_data
        and capabilities.capabilities["derived_feature_support"] is not CapabilityState.SUPPORTED
    ):
        reasons.add(ReasonCode.PURPOSE_NOT_PERMITTED)
    if request.require_backup and policy.backup is not Permission.PERMITTED:
        reasons.add(ReasonCode.PURPOSE_NOT_PERMITTED)
    if (
        request.require_backup
        and capabilities.capabilities["backup_support"] is not CapabilityState.SUPPORTED
    ):
        reasons.add(ReasonCode.PURPOSE_NOT_PERMITTED)
    if request.require_citation and policy.citation is not Permission.PERMITTED:
        reasons.add(ReasonCode.PURPOSE_NOT_PERMITTED)
    if request.use_external_ai and policy.external_ai_processing is not Permission.PERMITTED:
        reasons.add(ReasonCode.PURPOSE_NOT_PERMITTED)
    termination_reasons, lifecycle = _termination_reasons(policy, lifecycle_registry, request)
    reasons.update(termination_reasons)
    ordered = tuple(sorted(reasons, key=str))
    if ordered:
        return _create_artifact(
            passed=False,
            reasons=ordered,
            weighted_score=None,
            scorecard_version=None,
            capabilities=capabilities,
            policy=policy,
            lifecycle_registry=lifecycle_registry,
            lifecycle=lifecycle,
            scorecard=scorecard,
            request=request,
        )
    return _create_artifact(
        passed=True,
        reasons=(),
        weighted_score=scorecard.weighted_score(),
        scorecard_version=scorecard.scorecard_version,
        capabilities=capabilities,
        policy=policy,
        lifecycle_registry=lifecycle_registry,
        lifecycle=None,
        scorecard=scorecard,
        request=request,
    )


def validate_provider_envelope(
    envelope: ProviderResponseEnvelope,
    payload: bytes,
    capabilities: ProviderCapabilityRegistry,
    policy: DataUsagePolicy,
    request: EvaluationRequest,
    allowed_schema_versions: frozenset[str],
) -> EnvelopeGateResult:
    reasons: set[ReasonCode] = set()
    if (
        envelope.provider_id,
        envelope.product,
        envelope.product_version,
    ) != (capabilities.provider_id, capabilities.product, capabilities.version):
        reasons.add(ReasonCode.ENVELOPE_MISMATCH)
    if (envelope.provider_id, envelope.product, envelope.policy_id) != (
        policy.provider_id,
        policy.product,
        policy.policy_id,
    ):
        reasons.add(ReasonCode.ENVELOPE_MISMATCH)
    if envelope.agreement_version != policy.agreement_version:
        reasons.add(ReasonCode.ENVELOPE_AGREEMENT_MISMATCH)
    if envelope.policy_snapshot_id != contract_snapshot_id(policy):
        reasons.add(ReasonCode.ENVELOPE_POLICY_SNAPSHOT_MISMATCH)
    if envelope.intended_usage_purpose is not request.purpose:
        reasons.add(ReasonCode.ENVELOPE_MISMATCH)
    if envelope.payload_schema_version not in allowed_schema_versions:
        reasons.add(ReasonCode.SCHEMA_NOT_ALLOWED)
    if envelope.retrieved_at < policy.effective_from or (
        policy.termination_at is not None and envelope.retrieved_at >= policy.termination_at
    ):
        reasons.add(ReasonCode.AGREEMENT_EXPIRED)
    if request.at < policy.effective_from or (
        policy.termination_at is not None and request.at >= policy.termination_at
    ):
        reasons.add(ReasonCode.AGREEMENT_EXPIRED)
    expected_hash = f"sha256:{hashlib.sha256(payload).hexdigest()}"
    if envelope.immutable_payload_hash != expected_hash:
        reasons.add(ReasonCode.EVIDENCE_INTEGRITY_FAILURE)
    ordered = tuple(sorted(reasons, key=str))
    return EnvelopeGateResult(False, ordered) if ordered else EnvelopeGateResult(True, ())


def _artifacts_match(artifact: EvaluationArtifact, authoritative: EvaluationArtifact) -> bool:
    if not isinstance(artifact, EvaluationArtifact):
        return False
    try:
        return all(
            getattr(artifact, name) == getattr(authoritative, name)
            for name in (
                "schema_version",
                "artifact_id",
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
        )
    except AttributeError:
        return False


def validate_evaluation_artifact(
    artifact: EvaluationArtifact,
    capabilities: ProviderCapabilityRegistry,
    policy: DataUsagePolicy,
    lifecycle_registry: TerminationLifecycleRegistry,
    request: EvaluationRequest,
    scorecard: ProviderScorecard,
) -> bool:
    """Recompute the authoritative result and compare every audit-artifact field."""

    authoritative = evaluate_hard_gates(
        capabilities,
        policy,
        lifecycle_registry,
        request,
        scorecard,
    )
    return _artifacts_match(artifact, authoritative)


def _remediation_incomplete(conflict: ReconciliationConflict) -> bool:
    return any(
        execution.status in (RemediationStatus.PENDING, RemediationStatus.INVALID)
        for execution in (conflict.correction_execution, conflict.republication_execution)
    )


def publication_gate(
    *,
    evaluation_artifact: EvaluationArtifact,
    capabilities: ProviderCapabilityRegistry,
    policy: DataUsagePolicy,
    lifecycle_registry: TerminationLifecycleRegistry,
    request: EvaluationRequest,
    scorecard: ProviderScorecard,
    stale: bool,
    critical_missing: bool,
    conflicts: tuple[StructuredReason, ...] = (),
    reconciliation_conflicts: tuple[ReconciliationConflict, ...] = (),
    warnings: tuple[StructuredReason, ...] = (),
) -> PublicationDecision:
    reasons = [*conflicts, *warnings]
    authoritative_artifact = evaluate_hard_gates(
        capabilities,
        policy,
        lifecycle_registry,
        request,
        scorecard,
    )
    valid_artifact = _artifacts_match(evaluation_artifact, authoritative_artifact)
    if not valid_artifact:
        reasons.append(
            StructuredReason(
                ReasonCode.EVALUATION_ARTIFACT_INVALID.value,
                "Evaluation artifact does not match current immutable inputs",
            )
        )
    elif not authoritative_artifact.passed:
        reasons.extend(
            StructuredReason(code.value, "Provider hard gate failed")
            for code in authoritative_artifact.reasons
        )
    if stale:
        reasons.append(StructuredReason("DATA_STALE", "Freshness threshold exceeded"))
    if critical_missing:
        reasons.append(StructuredReason("CRITICAL_FIELD_MISSING", "Critical field absent"))
    invalid_conflicts = tuple(
        conflict
        for conflict in reconciliation_conflicts
        if conflict.resolution_status is ConflictResolutionStatus.INVALID_NON_REMEDIABLE
    )
    unresolved_critical = tuple(
        conflict
        for conflict in reconciliation_conflicts
        if conflict.resolution_status is ConflictResolutionStatus.UNRESOLVED
        and conflict.severity is GapSeverity.CRITICAL
    )
    pending_remediation = tuple(
        conflict
        for conflict in reconciliation_conflicts
        if conflict.resolution_status is ConflictResolutionStatus.RESOLVED_APPROVED
        and _remediation_incomplete(conflict)
    )
    invalid_remediation = tuple(
        conflict
        for conflict in pending_remediation
        if any(
            execution.status is RemediationStatus.INVALID
            for execution in (conflict.correction_execution, conflict.republication_execution)
        )
    )
    if invalid_conflicts:
        reasons.append(
            StructuredReason(
                "INVALID_RECONCILIATION_CONFLICT",
                "A non-remediable conflict was rejected",
            )
        )
    if unresolved_critical:
        reasons.append(
            StructuredReason(
                "UNRESOLVED_CRITICAL_CONFLICT",
                "A critical source conflict remains unresolved",
            )
        )
    if pending_remediation:
        code = (
            ReasonCode.RECONCILIATION_REMEDIATION_INVALID
            if invalid_remediation
            else ReasonCode.RECONCILIATION_REMEDIATION_PENDING
        )
        reasons.append(
            StructuredReason(
                code.value,
                "Reviewer approval exists but required correction or republication is incomplete",
            )
        )
    if reconciliation_conflicts and not (
        invalid_conflicts or unresolved_critical or pending_remediation
    ):
        reasons.append(
            StructuredReason(
                "RECONCILIATION_AUDIT_WARNING",
                "Resolved or non-critical conflict evidence is preserved",
            )
        )
    if not valid_artifact or not authoritative_artifact.passed or stale or invalid_conflicts:
        status = PublicationStatus.REJECTED
    elif critical_missing or conflicts or unresolved_critical or pending_remediation:
        status = PublicationStatus.QUARANTINED
    elif warnings or reconciliation_conflicts:
        status = PublicationStatus.ACCEPTED_WITH_WARNINGS
    else:
        status = PublicationStatus.ACCEPTED
    return PublicationDecision(status, tuple(reasons), reconciliation_conflicts)


def deterministic_report(
    name: str,
    artifact: EvaluationArtifact,
    sections: dict[str, Any],
) -> tuple[str, str]:
    payload = {
        "report_schema_version": REPORT_SCHEMA_VERSION,
        "evaluation_artifact_schema_version": artifact.schema_version,
        "evaluation_artifact_id": artifact.artifact_id,
        "provider": name,
        "scope": "SYNTHETIC_ONLY",
        **sections,
        "hard_gate": {
            "passed": artifact.passed,
            "reasons": [reason.value for reason in artifact.reasons],
            "scorecard_version": artifact.scorecard_version,
            "weighted_score": (
                None if artifact.weighted_score is None else str(artifact.weighted_score)
            ),
        },
    }
    machine = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    weighted_score = (
        artifact.weighted_score if artifact.weighted_score is not None else "not calculated"
    )
    human = "\n".join(
        (
            f"Synthetic provider evaluation: {name}",
            f"Report schema: {REPORT_SCHEMA_VERSION}",
            f"Evaluation artifact: {artifact.artifact_id}",
            f"Hard gate: {'PASS' if artifact.passed else 'FAIL'}",
            f"Reasons: {', '.join(reason.value for reason in artifact.reasons) or 'none'}",
            f"Weighted score: {weighted_score}",
        )
    )
    return machine, human
