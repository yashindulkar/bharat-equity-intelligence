"""Executable real-data entry gates and deterministic synthetic evaluation reports."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from bharat_equity.domain.errors import ReasonCode
from bharat_equity.domain.provider_policy import (
    ApprovalStatus,
    CapabilityState,
    DataUsagePolicy,
    Permission,
    ProviderCapabilityRegistry,
    PublicationDecision,
    PublicationStatus,
    ReconciliationConflict,
    StructuredReason,
    UsagePurpose,
)

DEFAULT_WEIGHTS = {
    "corporate_actions": Decimal("0.10"),
    "cost": Decimal("0.05"),
    "financial_statements": Decimal("0.10"),
    "history_and_delistings": Decimal("0.10"),
    "licensing_and_retention": Decimal("0.20"),
    "pit_correctness": Decimal("0.25"),
    "reliability_support": Decimal("0.05"),
    "security_master": Decimal("0.15"),
}


@dataclass(frozen=True, slots=True)
class EvaluationRequest:
    at: datetime
    purpose: UsagePurpose
    user: str
    processing_geography: str
    required_history_start: datetime | None = None
    use_external_ai: bool = False
    create_derived_data: bool = False
    require_backup: bool = False
    require_citation: bool = False
    agreement_terminated: bool = False
    deletion_completed: bool = True
    require_historical: bool = True
    require_raw_retention: bool = True
    require_delisted: bool = True
    critical_history_available: bool = True
    identifiers_unambiguous: bool = True


@dataclass(frozen=True, slots=True)
class GateResult:
    passed: bool
    reasons: tuple[ReasonCode, ...]
    weighted_score: Decimal | None

    def __post_init__(self) -> None:
        if self.passed and (self.reasons or self.weighted_score is None):
            raise ValueError("passing gate requires a score and no reasons")
        if not self.passed and (not self.reasons or self.weighted_score is not None):
            raise ValueError("failed gate requires reasons and no score")


def evaluate_hard_gates(
    capabilities: ProviderCapabilityRegistry,
    policy: DataUsagePolicy,
    request: EvaluationRequest,
    quality_scores: dict[str, Decimal] | None = None,
) -> GateResult:
    reasons: set[ReasonCode] = set()
    if request.at.tzinfo is None or request.at.utcoffset() != UTC.utcoffset(request.at):
        reasons.add(ReasonCode.INVALID_TIMESTAMP)
        return GateResult(False, tuple(sorted(reasons, key=str)), None)
    if (capabilities.provider_id, capabilities.product) != (policy.provider_id, policy.product):
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
        or capabilities.known_history_gaps
        or (
            request.required_history_start is not None
            and capabilities.historical_start > request.required_history_start
        )
        or capabilities.historical_end < request.at
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
    if request.agreement_terminated:
        reasons.add(ReasonCode.AGREEMENT_EXPIRED)
    ordered = tuple(sorted(reasons, key=str))
    if ordered:
        return GateResult(False, ordered, None)
    scores = quality_scores or {}
    if set(scores) != set(DEFAULT_WEIGHTS) or any(
        not Decimal("0") <= v <= Decimal("100") for v in scores.values()
    ):
        raise ValueError("all quality dimensions require scores from 0 to 100")
    score = sum((scores[key] * DEFAULT_WEIGHTS[key] for key in sorted(DEFAULT_WEIGHTS)), Decimal())
    return GateResult(True, (), score.quantize(Decimal("0.01")))


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
    reasons.extend(
        StructuredReason(
            "RECONCILIATION_CONFLICT",
            conflict.conflict_id,
            conflict.field,
            tuple(value.source_record_id for value in conflict.values),
        )
        for conflict in reconciliation_conflicts
    )
    if not provider_gate.passed:
        reasons.extend(
            StructuredReason(code.value, "Provider hard gate failed")
            for code in provider_gate.reasons
        )
    if stale:
        reasons.append(StructuredReason("DATA_STALE", "Freshness threshold exceeded"))
    if critical_missing:
        reasons.append(StructuredReason("CRITICAL_FIELD_MISSING", "Critical field absent"))
    if not provider_gate.passed or stale:
        return PublicationDecision(PublicationStatus.REJECTED, tuple(reasons))
    if critical_missing or conflicts or reconciliation_conflicts:
        return PublicationDecision(PublicationStatus.QUARANTINED, tuple(reasons))
    if warnings:
        return PublicationDecision(PublicationStatus.ACCEPTED_WITH_WARNINGS, tuple(reasons))
    return PublicationDecision(PublicationStatus.ACCEPTED)


def deterministic_report(name: str, gate: GateResult, sections: dict[str, Any]) -> tuple[str, str]:
    payload = {
        "provider": name,
        "scope": "SYNTHETIC_ONLY",
        **sections,
        "hard_gate": {
            "passed": gate.passed,
            "reasons": [r.value for r in gate.reasons],
            "weighted_score": None if gate.weighted_score is None else str(gate.weighted_score),
        },
    }
    machine = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    human = "\n".join(
        (
            f"Synthetic provider evaluation: {name}",
            f"Hard gate: {'PASS' if gate.passed else 'FAIL'}",
            f"Reasons: {', '.join(r.value for r in gate.reasons) or 'none'}",
            "Weighted score: "
            f"{gate.weighted_score if gate.weighted_score is not None else 'not calculated'}",
        )
    )
    return machine, human
