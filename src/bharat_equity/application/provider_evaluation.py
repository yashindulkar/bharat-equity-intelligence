"""Executable real-data entry gates and deterministic synthetic evaluation reports."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any

from bharat_equity.domain.errors import ReasonCode
from bharat_equity.domain.models import require_text, require_utc
from bharat_equity.domain.provider_policy import (
    ApprovalStatus,
    CapabilityState,
    ConflictResolutionStatus,
    DataDomain,
    DataUsagePolicy,
    DeletionState,
    GapResolutionStatus,
    GapSeverity,
    HistoryGap,
    Permission,
    ProviderCapabilityRegistry,
    ProviderResponseEnvelope,
    ProviderScorecard,
    PublicationDecision,
    PublicationStatus,
    ReconciliationConflict,
    ScoreDimension,
    StructuredReason,
    TerminationDeletionLifecycle,
    UsagePurpose,
)

REPORT_SCHEMA_VERSION = "1.1.0"
DEFAULT_SCORECARD_VERSION = "research-defaults-1.0.0"
DEFAULT_WEIGHTS: dict[ScoreDimension, Decimal] = {
    ScoreDimension.PIT_CORRECTNESS: Decimal("0.25"),
    ScoreDimension.LICENSING_AND_RETENTION: Decimal("0.20"),
    ScoreDimension.SECURITY_MASTER: Decimal("0.15"),
    ScoreDimension.CORPORATE_ACTIONS: Decimal("0.10"),
    ScoreDimension.FINANCIAL_STATEMENTS: Decimal("0.10"),
    ScoreDimension.HISTORY_AND_DELISTINGS: Decimal("0.10"),
    ScoreDimension.RELIABILITY_SUPPORT: Decimal("0.05"),
    ScoreDimension.COST: Decimal("0.05"),
}


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
    use_external_ai: bool = False
    create_derived_data: bool = False
    require_backup: bool = False
    require_citation: bool = False
    require_historical: bool = True
    require_raw_retention: bool = True
    require_delisted: bool = True
    critical_history_available: bool = True
    identifiers_unambiguous: bool = True
    termination_lifecycle: TerminationDeletionLifecycle | None = None

    def __post_init__(self) -> None:
        for name in ("at", "required_history_start", "latest_required_session"):
            require_utc(getattr(self, name), name)
        for name in ("user", "processing_geography", "required_venue"):
            require_text(getattr(self, name), name)
        if self.latest_required_session < self.required_history_start:
            raise ValueError("latest_required_session must not precede required_history_start")
        for security_id in self.required_security_ids:
            require_text(security_id, "required_security_id")
        if len(set(self.required_security_ids)) != len(self.required_security_ids):
            raise ValueError("required_security_ids must be unique")
        if self.required_universe_scope is not None:
            require_text(self.required_universe_scope, "required_universe_scope")


@dataclass(frozen=True, slots=True)
class GateResult:
    passed: bool
    reasons: tuple[ReasonCode, ...]
    weighted_score: Decimal | None
    scorecard_version: str | None

    def __post_init__(self) -> None:
        if self.passed and (
            self.reasons or self.weighted_score is None or self.scorecard_version is None
        ):
            raise ValueError("passing gate requires score metadata and no reasons")
        if not self.passed and (
            not self.reasons
            or self.weighted_score is not None
            or self.scorecard_version is not None
        ):
            raise ValueError("failed gate requires reasons and no score metadata")


@dataclass(frozen=True, slots=True)
class EnvelopeGateResult:
    passed: bool
    reasons: tuple[ReasonCode, ...]

    def __post_init__(self) -> None:
        if self.passed and self.reasons:
            raise ValueError("passing envelope gate cannot carry reasons")
        if not self.passed and not self.reasons:
            raise ValueError("failed envelope gate requires reasons")


def _gap_intersects_request(gap: HistoryGap, request: EvaluationRequest) -> bool:
    if gap.data_domain is not request.required_data_domain:
        return False
    if gap.affected_venue != request.required_venue:
        return False
    if (
        gap.ends_at < request.required_history_start
        or gap.starts_at > request.latest_required_session
    ):
        return False
    security_match = bool(set(gap.affected_security_ids) & set(request.required_security_ids))
    universe_match = (
        gap.affected_universe_scope is not None
        and gap.affected_universe_scope == request.required_universe_scope
    )
    return security_match or universe_match


def _termination_reasons(
    policy: DataUsagePolicy,
    request: EvaluationRequest,
) -> set[ReasonCode]:
    lifecycle = request.termination_lifecycle
    if lifecycle is None or request.at < lifecycle.termination_at:
        return set()
    reasons = {ReasonCode.AGREEMENT_EXPIRED}
    if (
        lifecycle.derived_data_retention_permission is not policy.post_termination_derived_data
        or lifecycle.audit_evidence_retention_permission
        is not policy.post_termination_audit_evidence
    ):
        reasons.add(ReasonCode.PURPOSE_NOT_PERMITTED)
    governed = (
        (policy.post_termination_raw_data, lifecycle.raw_data_status),
        (policy.post_termination_backup, lifecycle.backup_status),
        (policy.post_termination_fixtures, lifecycle.fixture_status),
        (policy.post_termination_derived_data, lifecycle.derived_data_status),
        (
            policy.post_termination_audit_evidence,
            lifecycle.audit_evidence_status,
        ),
    )
    for permission, status in governed:
        if permission is Permission.UNKNOWN:
            reasons.add(ReasonCode.PERMISSION_UNKNOWN)
            continue
        if permission is Permission.PERMITTED:
            if status in (DeletionState.DUE, DeletionState.OVERDUE):
                reasons.add(ReasonCode.PURPOSE_NOT_PERMITTED)
            continue
        if request.at > lifecycle.deletion_deadline:
            if status is not DeletionState.COMPLETED:
                reasons.add(ReasonCode.TERMINATION_DELETION_OVERDUE)
        elif request.at == lifecycle.deletion_deadline:
            if status not in (DeletionState.DUE, DeletionState.COMPLETED):
                reasons.add(ReasonCode.TERMINATION_DELETION_OVERDUE)
        elif status not in (DeletionState.NOT_DUE, DeletionState.COMPLETED):
            reasons.add(ReasonCode.PURPOSE_NOT_PERMITTED)
    return reasons


def evaluate_hard_gates(
    capabilities: ProviderCapabilityRegistry,
    policy: DataUsagePolicy,
    request: EvaluationRequest,
    scorecard: ProviderScorecard,
) -> GateResult:
    reasons: set[ReasonCode] = set()
    if (capabilities.provider_id, capabilities.product) != (
        policy.provider_id,
        policy.product,
    ):
        reasons.add(ReasonCode.PROVIDER_NOT_APPROVED)
    if (
        scorecard.provider_id,
        scorecard.product,
        scorecard.product_version,
    ) != (capabilities.provider_id, capabilities.product, capabilities.version):
        reasons.add(ReasonCode.PROVIDER_NOT_APPROVED)
    if request.user not in policy.permitted_users:
        reasons.add(ReasonCode.PURPOSE_NOT_PERMITTED)
    if (
        policy.permitted_processing_geographies
        and request.processing_geography not in policy.permitted_processing_geographies
    ):
        reasons.add(ReasonCode.PURPOSE_NOT_PERMITTED)
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
    if request.at < policy.effective_from or (
        policy.effective_until is not None and request.at >= policy.effective_until
    ):
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
        and _gap_intersects_request(gap, request)
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
    reasons.update(_termination_reasons(policy, request))
    ordered = tuple(sorted(reasons, key=str))
    if ordered:
        return GateResult(False, ordered, None, None)
    return GateResult(
        True,
        (),
        scorecard.weighted_score(),
        scorecard.scorecard_version,
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
    if (
        envelope.provider_id,
        envelope.product,
        envelope.policy_id,
    ) != (policy.provider_id, policy.product, policy.policy_id):
        reasons.add(ReasonCode.ENVELOPE_MISMATCH)
    if envelope.intended_usage_purpose is not request.purpose:
        reasons.add(ReasonCode.ENVELOPE_MISMATCH)
    if envelope.payload_schema_version not in allowed_schema_versions:
        reasons.add(ReasonCode.SCHEMA_NOT_ALLOWED)
    if envelope.retrieved_at < policy.effective_from or (
        policy.effective_until is not None and envelope.retrieved_at >= policy.effective_until
    ):
        reasons.add(ReasonCode.AGREEMENT_EXPIRED)
    if request.at < policy.effective_from or (
        policy.effective_until is not None and request.at >= policy.effective_until
    ):
        reasons.add(ReasonCode.AGREEMENT_EXPIRED)
    expected_hash = f"sha256:{hashlib.sha256(payload).hexdigest()}"
    if envelope.immutable_payload_hash != expected_hash:
        reasons.add(ReasonCode.EVIDENCE_INTEGRITY_FAILURE)
    ordered = tuple(sorted(reasons, key=str))
    return EnvelopeGateResult(False, ordered) if ordered else EnvelopeGateResult(True, ())


def publication_gate(
    *,
    provider_gate: GateResult,
    stale: bool,
    critical_missing: bool,
    conflicts: tuple[StructuredReason, ...] = (),
    reconciliation_conflicts: tuple[ReconciliationConflict, ...] = (),
    warnings: tuple[StructuredReason, ...] = (),
) -> PublicationDecision:
    reasons = [*conflicts, *warnings]
    if not provider_gate.passed:
        reasons.extend(
            StructuredReason(code.value, "Provider hard gate failed")
            for code in provider_gate.reasons
        )
    if stale:
        reasons.append(StructuredReason("DATA_STALE", "Freshness threshold exceeded"))
    if critical_missing:
        reasons.append(
            StructuredReason(
                "CRITICAL_FIELD_MISSING",
                "Critical field absent",
            )
        )
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
    if invalid_conflicts:
        reasons.append(
            StructuredReason(
                "INVALID_RECONCILIATION_CONFLICT",
                "A non-remediable conflict was rejected",
            )
        )
    elif unresolved_critical:
        reasons.append(
            StructuredReason(
                "UNRESOLVED_CRITICAL_CONFLICT",
                "A critical source conflict remains unresolved",
            )
        )
    elif reconciliation_conflicts:
        reasons.append(
            StructuredReason(
                "RECONCILIATION_AUDIT_WARNING",
                "Resolved or non-critical conflict evidence is preserved",
            )
        )
    if not provider_gate.passed or stale or invalid_conflicts:
        status = PublicationStatus.REJECTED
    elif critical_missing or conflicts or unresolved_critical:
        status = PublicationStatus.QUARANTINED
    elif warnings or reconciliation_conflicts:
        status = PublicationStatus.ACCEPTED_WITH_WARNINGS
    else:
        status = PublicationStatus.ACCEPTED
    return PublicationDecision(
        status,
        tuple(reasons),
        reconciliation_conflicts,
    )


def deterministic_report(
    name: str,
    gate: GateResult,
    sections: dict[str, Any],
) -> tuple[str, str]:
    payload = {
        "report_schema_version": REPORT_SCHEMA_VERSION,
        "provider": name,
        "scope": "SYNTHETIC_ONLY",
        **sections,
        "hard_gate": {
            "passed": gate.passed,
            "reasons": [reason.value for reason in gate.reasons],
            "scorecard_version": gate.scorecard_version,
            "weighted_score": (None if gate.weighted_score is None else str(gate.weighted_score)),
        },
    }
    machine = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    human = "\n".join(
        (
            f"Synthetic provider evaluation: {name}",
            f"Report schema: {REPORT_SCHEMA_VERSION}",
            f"Hard gate: {'PASS' if gate.passed else 'FAIL'}",
            f"Reasons: {', '.join(reason.value for reason in gate.reasons) or 'none'}",
            "Weighted score: "
            f"{gate.weighted_score if gate.weighted_score is not None else 'not calculated'}",
        )
    )
    return machine, human
