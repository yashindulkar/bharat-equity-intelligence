"""Fail-closed, provider-neutral contracts for Phase 1 Task 2."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum

from .models import Contract, require_text, require_utc


class CapabilityState(StrEnum):
    SUPPORTED = "SUPPORTED"
    UNSUPPORTED = "UNSUPPORTED"
    UNKNOWN = "UNKNOWN"


class Permission(StrEnum):
    PERMITTED = "PERMITTED"
    PROHIBITED = "PROHIBITED"
    UNKNOWN = "UNKNOWN"


class ApprovalStatus(StrEnum):
    APPROVED = "APPROVED"
    PENDING = "PENDING"
    REJECTED = "REJECTED"


class UsagePurpose(StrEnum):
    PRIVATE_HOUSEHOLD_RESEARCH = "PRIVATE_HOUSEHOLD_RESEARCH"
    BACKTESTING = "BACKTESTING"
    MODEL_TRAINING = "MODEL_TRAINING"
    INTERNAL_DISPLAY = "INTERNAL_DISPLAY"
    TEST_FIXTURES = "TEST_FIXTURES"


CAPABILITY_NAMES = (
    "historical_depth",
    "delisted_coverage",
    "historical_symbol_support",
    "exact_publication_timestamps",
    "revisions_and_restatements",
    "historical_constituents",
    "total_return_benchmarks",
    "corporate_action_terms",
    "stable_identifiers",
    "raw_retention_support",
    "derived_feature_support",
    "backtesting_support",
    "backup_support",
    "test_fixture_support",
    "display_support",
    "model_training_support",
)


@dataclass(frozen=True, slots=True, kw_only=True)
class ProviderCapabilityRegistry(Contract):
    provider_id: str
    product: str
    version: str
    capabilities: dict[str, CapabilityState]
    historical_start: datetime | None
    historical_end: datetime | None
    known_history_gaps: tuple[str, ...]
    capability_evidence: dict[str, tuple[str, ...]]

    def __post_init__(self) -> None:
        Contract.__post_init__(self)
        for name in ("provider_id", "product", "version"):
            require_text(getattr(self, name), name)
        if set(self.capabilities) != set(CAPABILITY_NAMES):
            raise ValueError("every capability must be explicitly declared")
        if set(self.capability_evidence) != set(CAPABILITY_NAMES):
            raise ValueError("every capability requires an evidence declaration")
        for name, state in self.capabilities.items():
            evidence = self.capability_evidence[name]
            if state is CapabilityState.SUPPORTED and not evidence:
                raise ValueError(f"supported capability {name} requires evidence")
            for reference in evidence:
                require_text(reference, f"{name}_evidence")
        if self.historical_start is not None:
            require_utc(self.historical_start, "historical_start")
        if self.historical_end is not None:
            require_utc(self.historical_end, "historical_end")


@dataclass(frozen=True, slots=True, kw_only=True)
class DataUsagePolicy(Contract):
    policy_id: str
    provider_id: str
    product: str
    agreement_version: str
    effective_from: datetime
    effective_until: datetime | None
    permitted_users: tuple[str, ...]
    permitted_purposes: dict[UsagePurpose, Permission]
    raw_retention: Permission
    derived_data: Permission
    backtesting: Permission
    model_training: Permission
    display: Permission
    citation: Permission
    backup: Permission
    fixtures: Permission
    post_termination_retention: Permission
    deletion_obligations: str
    permitted_processing_geographies: tuple[str, ...]
    geographical_restrictions: tuple[str, ...]
    evidence_reference: str
    reviewer: str
    approved_at: datetime | None
    review_due_at: datetime | None
    external_ai_processing: Permission
    approval_status: ApprovalStatus

    def __post_init__(self) -> None:
        Contract.__post_init__(self)
        for name in (
            "policy_id",
            "provider_id",
            "product",
            "agreement_version",
            "deletion_obligations",
            "evidence_reference",
            "reviewer",
        ):
            require_text(getattr(self, name), name)
        require_utc(self.effective_from, "effective_from")
        if self.effective_until is not None:
            require_utc(self.effective_until, "effective_until")
            if self.effective_until <= self.effective_from:
                raise ValueError("effective_until must follow effective_from")
        if set(self.permitted_purposes) != set(UsagePurpose):
            raise ValueError("every intended purpose must be explicitly declared")
        if not self.permitted_users:
            raise ValueError("permitted_users must be explicit")
        if self.approval_status is ApprovalStatus.APPROVED and self.approved_at is None:
            raise ValueError("approved policy requires approved_at")
        for name in ("approved_at", "review_due_at"):
            value = getattr(self, name)
            if value is not None:
                require_utc(value, name)


@dataclass(frozen=True, slots=True, kw_only=True)
class ProviderResponseEnvelope(Contract):
    provider_id: str
    product_version: str
    request_id: str
    source_record_id: str
    retrieved_at: datetime
    published_at: datetime
    payload_schema_version: str
    content_type: str
    immutable_payload_hash: str
    license_policy_id: str
    intended_usage_purpose: UsagePurpose

    def __post_init__(self) -> None:
        Contract.__post_init__(self)
        for name in (
            "provider_id",
            "product_version",
            "request_id",
            "source_record_id",
            "content_type",
            "license_policy_id",
            "payload_schema_version",
        ):
            require_text(getattr(self, name), name)
        require_utc(self.retrieved_at, "retrieved_at")
        require_utc(self.published_at, "published_at")
        if not self.immutable_payload_hash.startswith("sha256:"):
            raise ValueError("immutable_payload_hash must be SHA-256")
        digest = self.immutable_payload_hash.removeprefix("sha256:")
        if len(digest) != 64:
            raise ValueError("immutable_payload_hash must be SHA-256")
        try:
            int(digest, 16)
        except ValueError as error:
            raise ValueError("immutable_payload_hash must be SHA-256") from error


class PublicationStatus(StrEnum):
    ACCEPTED = "ACCEPTED"
    ACCEPTED_WITH_WARNINGS = "ACCEPTED_WITH_WARNINGS"
    QUARANTINED = "QUARANTINED"
    REJECTED = "REJECTED"


@dataclass(frozen=True, slots=True)
class StructuredReason(Contract):
    code: str
    detail: str
    field: str | None = None
    source_record_ids: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class CompetingValue(Contract):
    source_record_id: str
    value: str
    semantic_basis: str
    evidence_reference: str
    confidence: str


@dataclass(frozen=True, slots=True)
class ReconciliationConflict(Contract):
    conflict_id: str
    field: str
    values: tuple[CompetingValue, ...]
    tolerance_rule: str
    tolerance_version: str
    measured_difference: str
    resolution_status: str
    reviewer_evidence: str | None = None
    reviewed_at: datetime | None = None
    correction_or_republication: str | None = None

    def __post_init__(self) -> None:
        Contract.__post_init__(self)
        if len(self.values) < 2:
            raise ValueError("conflict must preserve at least two values")
        for name in (
            "conflict_id",
            "field",
            "tolerance_rule",
            "tolerance_version",
            "measured_difference",
            "resolution_status",
        ):
            require_text(getattr(self, name), name)
        if self.reviewed_at is not None:
            require_utc(self.reviewed_at, "reviewed_at")


@dataclass(frozen=True, slots=True)
class PublicationDecision(Contract):
    status: PublicationStatus
    reasons: tuple[StructuredReason, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        Contract.__post_init__(self)
        if self.status in (PublicationStatus.QUARANTINED, PublicationStatus.REJECTED):
            if not self.reasons:
                raise ValueError("blocked publication requires reasons")
        if self.status is PublicationStatus.ACCEPTED and self.reasons:
            raise ValueError("accepted publication cannot carry reasons")
        if self.status is PublicationStatus.ACCEPTED_WITH_WARNINGS and not self.reasons:
            raise ValueError("accepted-with-warnings requires reasons")
