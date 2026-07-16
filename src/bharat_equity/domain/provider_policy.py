"""Fail-closed, provider-neutral contracts for Phase 1 Task 2."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from .models import Contract, require_finite, require_text, require_utc

PROVIDER_POLICY_SCHEMA_VERSION = "2.0.0"


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


class DataDomain(StrEnum):
    SECURITY_MASTER = "SECURITY_MASTER"
    EOD_MARKET_DATA = "EOD_MARKET_DATA"
    CORPORATE_ACTIONS = "CORPORATE_ACTIONS"
    FINANCIAL_FACTS = "FINANCIAL_FACTS"
    HISTORICAL_UNIVERSE = "HISTORICAL_UNIVERSE"
    BENCHMARK_TOTAL_RETURN = "BENCHMARK_TOTAL_RETURN"


class GapSeverity(StrEnum):
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class GapResolutionStatus(StrEnum):
    OPEN = "OPEN"
    RESOLVED = "RESOLVED"


class DeletionState(StrEnum):
    NOT_DUE = "NOT_DUE"
    DUE = "DUE"
    COMPLETED = "COMPLETED"
    OVERDUE = "OVERDUE"


class ConfidenceLevel(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class ConflictResolutionStatus(StrEnum):
    UNRESOLVED = "UNRESOLVED"
    RESOLVED_APPROVED = "RESOLVED_APPROVED"
    INVALID_NON_REMEDIABLE = "INVALID_NON_REMEDIABLE"


class CorrectionRequirement(StrEnum):
    NONE = "NONE"
    CORRECTION_REQUIRED = "CORRECTION_REQUIRED"
    REPUBLICATION_REQUIRED = "REPUBLICATION_REQUIRED"
    CORRECTION_AND_REPUBLICATION_REQUIRED = "CORRECTION_AND_REPUBLICATION_REQUIRED"


class PublicationStatus(StrEnum):
    ACCEPTED = "ACCEPTED"
    ACCEPTED_WITH_WARNINGS = "ACCEPTED_WITH_WARNINGS"
    QUARANTINED = "QUARANTINED"
    REJECTED = "REJECTED"


class ScoreDimension(StrEnum):
    PIT_CORRECTNESS = "pit_correctness"
    LICENSING_AND_RETENTION = "licensing_and_retention"
    SECURITY_MASTER = "security_master"
    CORPORATE_ACTIONS = "corporate_actions"
    FINANCIAL_STATEMENTS = "financial_statements"
    HISTORY_AND_DELISTINGS = "history_and_delistings"
    RELIABILITY_SUPPORT = "reliability_support"
    COST = "cost"


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


@dataclass(frozen=True, slots=True)
class ProviderPolicyContract(Contract):
    schema_version: str = field(
        default=PROVIDER_POLICY_SCHEMA_VERSION,
        kw_only=True,
    )


@dataclass(frozen=True, slots=True)
class EvidenceReference(ProviderPolicyContract):
    reference: str
    version: str

    def __post_init__(self) -> None:
        Contract.__post_init__(self)
        require_text(self.reference, "reference")
        require_text(self.version, "version")


@dataclass(frozen=True, slots=True)
class HistoryGap(ProviderPolicyContract):
    data_domain: DataDomain
    starts_at: datetime
    ends_at: datetime
    affected_venue: str
    affected_security_ids: tuple[str, ...]
    affected_universe_scope: str | None
    severity: GapSeverity
    evidence: EvidenceReference
    resolution_status: GapResolutionStatus

    def __post_init__(self) -> None:
        Contract.__post_init__(self)
        require_utc(self.starts_at, "starts_at")
        require_utc(self.ends_at, "ends_at")
        if self.ends_at < self.starts_at:
            raise ValueError("history gap ends_at must not precede starts_at")
        require_text(self.affected_venue, "affected_venue")
        for security_id in self.affected_security_ids:
            require_text(security_id, "affected_security_id")
        if len(set(self.affected_security_ids)) != len(self.affected_security_ids):
            raise ValueError("affected_security_ids must be unique")
        if self.affected_universe_scope is not None:
            require_text(self.affected_universe_scope, "affected_universe_scope")
        if not self.affected_security_ids and self.affected_universe_scope is None:
            raise ValueError("history gap requires a security or universe scope")


@dataclass(frozen=True, slots=True, kw_only=True)
class ProviderCapabilityRegistry(ProviderPolicyContract):
    provider_id: str
    product: str
    version: str
    capabilities: dict[str, CapabilityState]
    historical_start: datetime | None
    historical_end: datetime | None
    history_gaps: tuple[HistoryGap, ...]
    capability_evidence: dict[str, tuple[EvidenceReference, ...]]

    def __post_init__(self) -> None:
        Contract.__post_init__(self)
        for name in ("provider_id", "product", "version"):
            require_text(getattr(self, name), name)
        if set(self.capabilities) != set(CAPABILITY_NAMES):
            raise ValueError("every capability must be explicitly declared")
        if not all(isinstance(value, CapabilityState) for value in self.capabilities.values()):
            raise TypeError("capability values must be CapabilityState members")
        if set(self.capability_evidence) != set(CAPABILITY_NAMES):
            raise ValueError("every capability requires an evidence declaration")
        for name, state in self.capabilities.items():
            evidence = self.capability_evidence[name]
            if state is CapabilityState.SUPPORTED and not evidence:
                raise ValueError(f"supported capability {name} requires evidence")
        if self.historical_start is not None:
            require_utc(self.historical_start, "historical_start")
        if self.historical_end is not None:
            require_utc(self.historical_end, "historical_end")
        if (
            self.historical_start is not None
            and self.historical_end is not None
            and self.historical_end < self.historical_start
        ):
            raise ValueError("historical_end must not precede historical_start")


@dataclass(frozen=True, slots=True, kw_only=True)
class DataUsagePolicy(ProviderPolicyContract):
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
    post_termination_raw_data: Permission
    post_termination_backup: Permission
    post_termination_fixtures: Permission
    post_termination_derived_data: Permission
    post_termination_audit_evidence: Permission
    deletion_obligations: str
    permitted_processing_geographies: tuple[str, ...]
    geographical_restrictions: tuple[str, ...]
    evidence_references: tuple[EvidenceReference, ...]
    reviewer: str
    approved_at: datetime | None
    rejected_at: datetime | None
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
        if not all(
            isinstance(key, UsagePurpose) and isinstance(value, Permission)
            for key, value in self.permitted_purposes.items()
        ):
            raise TypeError("permission map must contain UsagePurpose and Permission members")
        permission_fields = (
            self.raw_retention,
            self.derived_data,
            self.backtesting,
            self.model_training,
            self.display,
            self.citation,
            self.backup,
            self.fixtures,
            self.post_termination_raw_data,
            self.post_termination_backup,
            self.post_termination_fixtures,
            self.post_termination_derived_data,
            self.post_termination_audit_evidence,
            self.external_ai_processing,
        )
        if not all(isinstance(value, Permission) for value in permission_fields):
            raise TypeError("policy permissions must be Permission members")
        if not self.permitted_users:
            raise ValueError("permitted_users must be explicit")
        for user in self.permitted_users:
            require_text(user, "permitted_user")
        for geography in (
            *self.permitted_processing_geographies,
            *self.geographical_restrictions,
        ):
            require_text(geography, "geography")
        if set(self.permitted_processing_geographies) & set(self.geographical_restrictions):
            raise ValueError("a geography cannot be both permitted and restricted")
        if not self.evidence_references:
            raise ValueError("policy evidence references are required")
        for name in ("approved_at", "rejected_at", "review_due_at"):
            value = getattr(self, name)
            if value is not None:
                require_utc(value, name)
        if self.approval_status is ApprovalStatus.APPROVED:
            if self.approved_at is None or self.rejected_at is not None:
                raise ValueError("approved policy requires only approved_at")
            if self.approved_at < self.effective_from or (
                self.effective_until is not None and self.approved_at >= self.effective_until
            ):
                raise ValueError("approved_at must be within the agreement interval")
            if self.review_due_at is not None and self.review_due_at <= self.approved_at:
                raise ValueError("review_due_at must follow approved_at")
        elif self.approval_status is ApprovalStatus.REJECTED:
            if self.rejected_at is None or self.approved_at is not None:
                raise ValueError("rejected policy requires only rejected_at")
            if self.rejected_at < self.effective_from or (
                self.effective_until is not None and self.rejected_at >= self.effective_until
            ):
                raise ValueError("rejected_at must be within the agreement interval")
            if self.review_due_at is not None:
                raise ValueError("rejected policy cannot have review_due_at")
        elif any(
            value is not None for value in (self.approved_at, self.rejected_at, self.review_due_at)
        ):
            raise ValueError("pending policy cannot carry decision timestamps")


@dataclass(frozen=True, slots=True)
class TerminationDeletionLifecycle(ProviderPolicyContract):
    termination_at: datetime
    deletion_deadline: datetime
    raw_data_status: DeletionState
    backup_status: DeletionState
    fixture_status: DeletionState
    derived_data_retention_permission: Permission
    derived_data_status: DeletionState
    audit_evidence_retention_permission: Permission
    audit_evidence_status: DeletionState
    deletion_verification_evidence: tuple[EvidenceReference, ...] = ()

    def __post_init__(self) -> None:
        Contract.__post_init__(self)
        require_utc(self.termination_at, "termination_at")
        require_utc(self.deletion_deadline, "deletion_deadline")
        if self.deletion_deadline < self.termination_at:
            raise ValueError("deletion_deadline must not precede termination_at")
        if not isinstance(self.derived_data_retention_permission, Permission) or not isinstance(
            self.audit_evidence_retention_permission, Permission
        ):
            raise TypeError("retention permissions must be Permission members")
        statuses = (
            self.raw_data_status,
            self.backup_status,
            self.fixture_status,
            self.derived_data_status,
            self.audit_evidence_status,
        )
        if not all(isinstance(status, DeletionState) for status in statuses):
            raise TypeError("deletion statuses must be DeletionState members")
        if any(status is DeletionState.COMPLETED for status in statuses):
            if not self.deletion_verification_evidence:
                raise ValueError("completed deletion requires verification evidence")


@dataclass(frozen=True, slots=True, kw_only=True)
class ProviderResponseEnvelope(ProviderPolicyContract):
    provider_id: str
    product: str
    product_version: str
    request_id: str
    source_record_id: str
    retrieved_at: datetime
    published_at: datetime
    payload_schema_version: str
    content_type: str
    immutable_payload_hash: str
    policy_id: str
    intended_usage_purpose: UsagePurpose

    def __post_init__(self) -> None:
        Contract.__post_init__(self)
        for name in (
            "provider_id",
            "product",
            "product_version",
            "request_id",
            "source_record_id",
            "content_type",
            "policy_id",
            "payload_schema_version",
        ):
            require_text(getattr(self, name), name)
        require_utc(self.retrieved_at, "retrieved_at")
        require_utc(self.published_at, "published_at")
        if self.published_at > self.retrieved_at:
            raise ValueError("published_at cannot follow retrieved_at")
        if not isinstance(self.intended_usage_purpose, UsagePurpose):
            raise TypeError("intended_usage_purpose must be a UsagePurpose member")
        if not self.immutable_payload_hash.startswith("sha256:"):
            raise ValueError("immutable_payload_hash must be SHA-256")
        digest = self.immutable_payload_hash.removeprefix("sha256:")
        if len(digest) != 64:
            raise ValueError("immutable_payload_hash must be SHA-256")
        try:
            int(digest, 16)
        except ValueError as error:
            raise ValueError("immutable_payload_hash must be SHA-256") from error


@dataclass(frozen=True, slots=True)
class StructuredReason(ProviderPolicyContract):
    code: str
    detail: str
    field: str | None = None
    source_record_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        Contract.__post_init__(self)
        require_text(self.code, "code")
        require_text(self.detail, "detail")
        if self.field is not None:
            require_text(self.field, "field")
        for source_record_id in self.source_record_ids:
            require_text(source_record_id, "source_record_id")


@dataclass(frozen=True, slots=True)
class CompetingValue(ProviderPolicyContract):
    source_record_id: str
    value: str
    semantic_basis: str
    evidence_reference: EvidenceReference
    confidence: ConfidenceLevel

    def __post_init__(self) -> None:
        Contract.__post_init__(self)
        for name in ("source_record_id", "value", "semantic_basis"):
            require_text(getattr(self, name), name)
        if not isinstance(self.confidence, ConfidenceLevel):
            raise TypeError("confidence must be a ConfidenceLevel member")


@dataclass(frozen=True, slots=True)
class ReconciliationConflict(ProviderPolicyContract):
    conflict_id: str
    field: str
    values: tuple[CompetingValue, ...]
    tolerance_rule: str
    tolerance_version: str
    measured_difference: str
    severity: GapSeverity
    resolution_status: ConflictResolutionStatus
    correction_requirement: CorrectionRequirement
    reviewer_evidence: EvidenceReference | None = None
    reviewed_at: datetime | None = None

    def __post_init__(self) -> None:
        Contract.__post_init__(self)
        for name in (
            "conflict_id",
            "field",
            "tolerance_rule",
            "tolerance_version",
            "measured_difference",
        ):
            require_text(getattr(self, name), name)
        if len(self.values) < 2:
            raise ValueError("conflict must preserve at least two values")
        source_ids = tuple(value.source_record_id for value in self.values)
        if len(set(source_ids)) != len(source_ids):
            raise ValueError("competing source_record_ids must be unique")
        distinct_values = {value.value for value in self.values}
        if len(distinct_values) < 2:
            raise ValueError("conflict requires at least two distinct competing values")
        reviewed = self.resolution_status in (
            ConflictResolutionStatus.RESOLVED_APPROVED,
            ConflictResolutionStatus.INVALID_NON_REMEDIABLE,
        )
        if reviewed:
            if self.reviewer_evidence is None or self.reviewed_at is None:
                raise ValueError("reviewed conflicts require evidence and reviewed_at")
            require_utc(self.reviewed_at, "reviewed_at")
        elif self.reviewer_evidence is not None or self.reviewed_at is not None:
            raise ValueError("unresolved conflicts cannot carry review completion evidence")
        if (
            self.resolution_status is ConflictResolutionStatus.UNRESOLVED
            and self.correction_requirement is CorrectionRequirement.NONE
        ):
            raise ValueError("unresolved conflicts require an explicit remediation action")
        if (
            self.resolution_status is ConflictResolutionStatus.INVALID_NON_REMEDIABLE
            and self.correction_requirement is not CorrectionRequirement.NONE
        ):
            raise ValueError("non-remediable conflicts cannot require correction or republication")


@dataclass(frozen=True, slots=True)
class PublicationDecision(ProviderPolicyContract):
    status: PublicationStatus
    reasons: tuple[StructuredReason, ...] = field(default_factory=tuple)
    reconciliation_conflicts: tuple[ReconciliationConflict, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        Contract.__post_init__(self)
        if self.status in (PublicationStatus.QUARANTINED, PublicationStatus.REJECTED):
            if not self.reasons:
                raise ValueError("blocked publication requires reasons")
        if self.status is PublicationStatus.ACCEPTED and (
            self.reasons or self.reconciliation_conflicts
        ):
            raise ValueError("accepted publication cannot carry findings")
        if self.status is PublicationStatus.ACCEPTED_WITH_WARNINGS and not (
            self.reasons or self.reconciliation_conflicts
        ):
            raise ValueError("accepted-with-warnings requires findings")


@dataclass(frozen=True, slots=True)
class ScorecardEntry(ProviderPolicyContract):
    dimension: ScoreDimension
    raw_score: Decimal
    weight: Decimal
    evidence_references: tuple[EvidenceReference, ...]
    assessor: str
    assessed_at: datetime
    method_version: str
    explanation: str
    confidence: ConfidenceLevel

    def __post_init__(self) -> None:
        Contract.__post_init__(self)
        require_finite(self.raw_score, "raw_score")
        require_finite(self.weight, "weight")
        if not Decimal("0") <= self.raw_score <= Decimal("100"):
            raise ValueError("raw_score must be between 0 and 100")
        if not Decimal("0") <= self.weight <= Decimal("1"):
            raise ValueError("weight must be between 0 and 1")
        if not self.evidence_references:
            raise ValueError("scorecard evidence is required")
        for name in ("assessor", "method_version", "explanation"):
            require_text(getattr(self, name), name)
        require_utc(self.assessed_at, "assessed_at")
        if not isinstance(self.dimension, ScoreDimension):
            raise TypeError("dimension must be a ScoreDimension member")
        if not isinstance(self.confidence, ConfidenceLevel):
            raise TypeError("confidence must be a ConfidenceLevel member")


@dataclass(frozen=True, slots=True, kw_only=True)
class ProviderScorecard(ProviderPolicyContract):
    provider_id: str
    product: str
    product_version: str
    scorecard_version: str
    entries: tuple[ScorecardEntry, ...]

    def __post_init__(self) -> None:
        Contract.__post_init__(self)
        for name in ("provider_id", "product", "product_version", "scorecard_version"):
            require_text(getattr(self, name), name)
        dimensions = tuple(entry.dimension for entry in self.entries)
        if len(set(dimensions)) != len(dimensions):
            raise ValueError("scorecard dimensions must be unique")
        if set(dimensions) != set(ScoreDimension):
            raise ValueError("scorecard requires the exact complete dimension set")
        weight_total = sum((entry.weight for entry in self.entries), Decimal())
        if weight_total != Decimal("1"):
            raise ValueError("scorecard weights must sum exactly to 1")

    def weighted_score(self) -> Decimal:
        value = sum(
            (entry.raw_score * entry.weight for entry in self.entries),
            Decimal(),
        )
        return value.quantize(Decimal("0.01"))
