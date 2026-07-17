"""Fail-closed, provider-neutral contracts for Phase 1 Task 2."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime
from decimal import ROUND_HALF_EVEN, Decimal
from enum import StrEnum
from types import MappingProxyType

from .models import Contract, require_finite, require_text, require_utc

PROVIDER_POLICY_SCHEMA_VERSION = "3.0.0"


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


class GeographyScope(StrEnum):
    JURISDICTIONS = "JURISDICTIONS"
    WORLDWIDE = "WORLDWIDE"


class DataCategory(StrEnum):
    RAW_DATA = "RAW_DATA"
    BACKUPS = "BACKUPS"
    TEST_FIXTURES = "TEST_FIXTURES"
    DERIVED_DATA = "DERIVED_DATA"
    AUDIT_EVIDENCE = "AUDIT_EVIDENCE"


class DispositionState(StrEnum):
    NOT_DUE = "NOT_DUE"
    DUE = "DUE"
    COMPLETED = "COMPLETED"
    OVERDUE = "OVERDUE"
    RETAINED = "RETAINED"


class MembershipState(StrEnum):
    MEMBER = "MEMBER"
    NON_MEMBER = "NON_MEMBER"


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


class RemediationAction(StrEnum):
    CORRECTION = "CORRECTION"
    REPUBLICATION = "REPUBLICATION"


class RemediationStatus(StrEnum):
    NOT_REQUIRED = "NOT_REQUIRED"
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    INVALID = "INVALID"


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


def _canonical_jurisdiction(value: str, name: str) -> str:
    require_text(value, name)
    canonical = value.strip().upper()
    if value != canonical:
        raise ValueError(f"{name} must be canonical uppercase without surrounding whitespace")
    return canonical


def contract_snapshot_id(contract: Contract) -> str:
    """Return a deterministic content address for an immutable contract snapshot."""

    payload = json.dumps(contract.to_dict(), sort_keys=True, separators=(",", ":"))
    return f"sha256:{hashlib.sha256(payload.encode('utf-8')).hexdigest()}"


@dataclass(frozen=True, slots=True)
class ProviderPolicyContract(Contract):
    schema_version: str = field(default=PROVIDER_POLICY_SCHEMA_VERSION, kw_only=True)


@dataclass(frozen=True, slots=True)
class EvidenceReference(ProviderPolicyContract):
    reference: str
    version: str
    available_at: datetime | None = None

    def __post_init__(self) -> None:
        Contract.__post_init__(self)
        require_text(self.reference, "reference")
        require_text(self.version, "version")
        if self.available_at is not None:
            require_utc(self.available_at, "available_at")


@dataclass(frozen=True, slots=True)
class ProcessingGeographyGrant(ProviderPolicyContract):
    scope: GeographyScope
    jurisdiction_ids: tuple[str, ...]
    evidence_references: tuple[EvidenceReference, ...]

    def __post_init__(self) -> None:
        Contract.__post_init__(self)
        if not isinstance(self.scope, GeographyScope):
            raise TypeError("scope must be a GeographyScope member")
        for jurisdiction in self.jurisdiction_ids:
            _canonical_jurisdiction(jurisdiction, "jurisdiction_id")
        if len(set(self.jurisdiction_ids)) != len(self.jurisdiction_ids):
            raise ValueError("jurisdiction_ids must be unique")
        if self.scope is GeographyScope.JURISDICTIONS and not self.jurisdiction_ids:
            raise ValueError("jurisdiction scope requires at least one jurisdiction")
        if self.scope is GeographyScope.WORLDWIDE and self.jurisdiction_ids:
            raise ValueError("worldwide scope cannot carry jurisdiction identifiers")
        if not self.evidence_references:
            raise ValueError("processing geography permission requires evidence")


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


@dataclass(frozen=True, slots=True)
class UniverseMembershipEvidence(ProviderPolicyContract):
    security_id: str
    universe_scope: str
    effective_from: datetime
    effective_until: datetime
    state: MembershipState
    evidence: EvidenceReference

    def __post_init__(self) -> None:
        Contract.__post_init__(self)
        require_text(self.security_id, "security_id")
        require_text(self.universe_scope, "universe_scope")
        require_utc(self.effective_from, "effective_from")
        require_utc(self.effective_until, "effective_until")
        if self.effective_until < self.effective_from:
            raise ValueError("membership effective_until must not precede effective_from")
        if not isinstance(self.state, MembershipState):
            raise TypeError("state must be a MembershipState member")


@dataclass(frozen=True, slots=True, kw_only=True)
class ProviderCapabilityRegistry(ProviderPolicyContract):
    provider_id: str
    product: str
    version: str
    capabilities: Mapping[str, CapabilityState]
    historical_start: datetime | None
    historical_end: datetime | None
    history_gaps: tuple[HistoryGap, ...]
    capability_evidence: Mapping[str, tuple[EvidenceReference, ...]]

    def __post_init__(self) -> None:
        Contract.__post_init__(self)
        for name in ("provider_id", "product", "version"):
            require_text(getattr(self, name), name)
        capability_copy = dict(self.capabilities)
        evidence_copy = {name: tuple(items) for name, items in self.capability_evidence.items()}
        if set(capability_copy) != set(CAPABILITY_NAMES):
            raise ValueError("every capability must be explicitly declared")
        if not all(isinstance(value, CapabilityState) for value in capability_copy.values()):
            raise TypeError("capability values must be CapabilityState members")
        if set(evidence_copy) != set(CAPABILITY_NAMES):
            raise ValueError("every capability requires an evidence declaration")
        for name, state in capability_copy.items():
            if state is CapabilityState.SUPPORTED and not evidence_copy[name]:
                raise ValueError(f"supported capability {name} requires evidence")
        object.__setattr__(self, "capabilities", MappingProxyType(capability_copy))
        object.__setattr__(self, "capability_evidence", MappingProxyType(evidence_copy))
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
    termination_event_id: str | None
    termination_at: datetime | None
    early_termination_amendment: EvidenceReference | None
    permitted_users: tuple[str, ...]
    permitted_purposes: Mapping[UsagePurpose, Permission]
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
    processing_geography: ProcessingGeographyGrant
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
        termination_fields = (self.termination_event_id, self.termination_at)
        if any(value is None for value in termination_fields) != all(
            value is None for value in termination_fields
        ):
            raise ValueError("termination event ID and timestamp must be declared together")
        if self.effective_until is not None and self.termination_at is None:
            raise ValueError("finite agreements require an explicit termination event")
        if self.termination_event_id is not None:
            require_text(self.termination_event_id, "termination_event_id")
        if self.termination_at is not None:
            require_utc(self.termination_at, "termination_at")
            if self.termination_at <= self.effective_from:
                raise ValueError("termination_at must follow effective_from")
            if self.effective_until is not None and self.termination_at > self.effective_until:
                raise ValueError("termination_at cannot follow effective_until")
            early = self.effective_until is None or self.termination_at < self.effective_until
            if early and self.early_termination_amendment is None:
                raise ValueError("early termination requires amendment evidence")
            if not early and self.early_termination_amendment is not None:
                raise ValueError("scheduled termination cannot claim an early amendment")
        elif self.early_termination_amendment is not None:
            raise ValueError("termination amendment requires a termination event")
        purpose_copy = dict(self.permitted_purposes)
        if set(purpose_copy) != set(UsagePurpose):
            raise ValueError("every intended purpose must be explicitly declared")
        if not all(
            isinstance(key, UsagePurpose) and isinstance(value, Permission)
            for key, value in purpose_copy.items()
        ):
            raise TypeError("permission map must contain UsagePurpose and Permission members")
        object.__setattr__(self, "permitted_purposes", MappingProxyType(purpose_copy))
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
        if len(set(self.permitted_users)) != len(self.permitted_users):
            raise ValueError("permitted_users must be unique")
        restrictions = tuple(
            _canonical_jurisdiction(value, "geographical_restriction")
            for value in self.geographical_restrictions
        )
        if len(set(restrictions)) != len(restrictions):
            raise ValueError("geographical_restrictions must be unique")
        if self.processing_geography.scope is GeographyScope.WORLDWIDE and restrictions:
            raise ValueError("worldwide processing cannot also declare restrictions")
        overlap = set(self.processing_geography.jurisdiction_ids) & set(restrictions)
        if overlap:
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
class DeletionEvidenceReference(ProviderPolicyContract):
    category: DataCategory
    evidence: EvidenceReference

    def __post_init__(self) -> None:
        Contract.__post_init__(self)
        if not isinstance(self.category, DataCategory):
            raise TypeError("category must be a DataCategory member")


@dataclass(frozen=True, slots=True)
class DeletionDisposition(ProviderPolicyContract):
    category: DataCategory
    contractual_permission: Permission
    state: DispositionState
    applicable_deadline: datetime
    completion_at: datetime | None
    evidence_references: tuple[DeletionEvidenceReference, ...]
    verifier: str | None
    record_version: str

    def __post_init__(self) -> None:
        Contract.__post_init__(self)
        if not isinstance(self.category, DataCategory):
            raise TypeError("category must be a DataCategory member")
        if not isinstance(self.contractual_permission, Permission):
            raise TypeError("contractual_permission must be a Permission member")
        if not isinstance(self.state, DispositionState):
            raise TypeError("state must be a DispositionState member")
        require_utc(self.applicable_deadline, "applicable_deadline")
        require_text(self.record_version, "record_version")
        if any(item.category is not self.category for item in self.evidence_references):
            raise ValueError("deletion evidence must match the governed category")
        if self.state is DispositionState.COMPLETED:
            if self.completion_at is None or not self.evidence_references or self.verifier is None:
                raise ValueError(
                    "completed deletion requires category-specific completion evidence"
                )
            require_utc(self.completion_at, "completion_at")
            require_text(self.verifier, "verifier")
        elif self.state is DispositionState.RETAINED:
            if self.contractual_permission is not Permission.PERMITTED:
                raise ValueError("retention requires explicit category permission")
            if self.completion_at is not None:
                raise ValueError("retained data cannot carry deletion completion time")
            if not self.evidence_references or self.verifier is None:
                raise ValueError("retention requires category-specific evidence and verifier")
            require_text(self.verifier, "verifier")
        elif (
            self.completion_at is not None or self.evidence_references or self.verifier is not None
        ):
            raise ValueError("non-completed deletion state cannot carry completion evidence")


@dataclass(frozen=True, slots=True)
class TerminationDeletionLifecycle(ProviderPolicyContract):
    lifecycle_id: str
    provider_id: str
    product: str
    policy_id: str
    agreement_version: str
    termination_event_id: str
    termination_at: datetime
    dispositions: tuple[DeletionDisposition, ...]
    record_version: str

    def __post_init__(self) -> None:
        Contract.__post_init__(self)
        for name in (
            "lifecycle_id",
            "provider_id",
            "product",
            "policy_id",
            "agreement_version",
            "termination_event_id",
            "record_version",
        ):
            require_text(getattr(self, name), name)
        require_utc(self.termination_at, "termination_at")
        categories = tuple(item.category for item in self.dispositions)
        if len(set(categories)) != len(categories):
            raise ValueError("lifecycle disposition categories must be unique")
        if set(categories) != set(DataCategory):
            raise ValueError("lifecycle requires exactly one disposition per governed category")
        if any(item.applicable_deadline < self.termination_at for item in self.dispositions):
            raise ValueError("deletion deadlines cannot precede termination")
        if any(
            item.completion_at is not None and item.completion_at < self.termination_at
            for item in self.dispositions
        ):
            raise ValueError("deletion completion cannot precede termination")


@dataclass(frozen=True, slots=True)
class TerminationLifecycleRegistry(ProviderPolicyContract):
    registry_version: str
    records: tuple[TerminationDeletionLifecycle, ...]

    def __post_init__(self) -> None:
        Contract.__post_init__(self)
        require_text(self.registry_version, "registry_version")
        keys = tuple(
            (
                item.provider_id,
                item.product,
                item.policy_id,
                item.agreement_version,
                item.termination_event_id,
            )
            for item in self.records
        )
        if len(set(keys)) != len(keys):
            raise ValueError("lifecycle registry agreement identities must be unique")

    def exact_record(self, policy: DataUsagePolicy) -> TerminationDeletionLifecycle | None:
        if policy.termination_event_id is None:
            return None
        key = (
            policy.provider_id,
            policy.product,
            policy.policy_id,
            policy.agreement_version,
            policy.termination_event_id,
        )
        return next(
            (
                item
                for item in self.records
                if (
                    item.provider_id,
                    item.product,
                    item.policy_id,
                    item.agreement_version,
                    item.termination_event_id,
                )
                == key
            ),
            None,
        )


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
    agreement_version: str
    policy_snapshot_id: str
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
            "agreement_version",
            "policy_snapshot_id",
            "payload_schema_version",
        ):
            require_text(getattr(self, name), name)
        require_utc(self.retrieved_at, "retrieved_at")
        require_utc(self.published_at, "published_at")
        if self.published_at > self.retrieved_at:
            raise ValueError("published_at cannot follow retrieved_at")
        if not isinstance(self.intended_usage_purpose, UsagePurpose):
            raise TypeError("intended_usage_purpose must be a UsagePurpose member")
        for value, name in (
            (self.immutable_payload_hash, "immutable_payload_hash"),
            (self.policy_snapshot_id, "policy_snapshot_id"),
        ):
            if not value.startswith("sha256:") or len(value.removeprefix("sha256:")) != 64:
                raise ValueError(f"{name} must be SHA-256")
            try:
                int(value.removeprefix("sha256:"), 16)
            except ValueError as error:
                raise ValueError(f"{name} must be SHA-256") from error


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
class RemediationExecution(ProviderPolicyContract):
    action: RemediationAction
    status: RemediationStatus
    completed_at: datetime | None = None
    completion_evidence: tuple[EvidenceReference, ...] = ()
    verifier: str | None = None

    def __post_init__(self) -> None:
        Contract.__post_init__(self)
        if not isinstance(self.action, RemediationAction):
            raise TypeError("action must be a RemediationAction member")
        if not isinstance(self.status, RemediationStatus):
            raise TypeError("status must be a RemediationStatus member")
        if self.status is RemediationStatus.COMPLETED:
            if self.completed_at is None or not self.completion_evidence or self.verifier is None:
                raise ValueError("completed remediation requires evidence, time, and verifier")
            require_utc(self.completed_at, "completed_at")
            require_text(self.verifier, "verifier")
        elif self.completed_at is not None or self.completion_evidence or self.verifier is not None:
            raise ValueError("incomplete remediation cannot carry completion evidence")


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
    correction_execution: RemediationExecution
    republication_execution: RemediationExecution
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
        if len({value.value for value in self.values}) < 2:
            raise ValueError("conflict requires at least two distinct competing values")
        if self.correction_execution.action is not RemediationAction.CORRECTION:
            raise ValueError("correction_execution must describe correction")
        if self.republication_execution.action is not RemediationAction.REPUBLICATION:
            raise ValueError("republication_execution must describe republication")
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
        requires_correction = self.correction_requirement in (
            CorrectionRequirement.CORRECTION_REQUIRED,
            CorrectionRequirement.CORRECTION_AND_REPUBLICATION_REQUIRED,
        )
        requires_republication = self.correction_requirement in (
            CorrectionRequirement.REPUBLICATION_REQUIRED,
            CorrectionRequirement.CORRECTION_AND_REPUBLICATION_REQUIRED,
        )
        for required, execution, label in (
            (requires_correction, self.correction_execution, "correction"),
            (requires_republication, self.republication_execution, "republication"),
        ):
            if required and execution.status is RemediationStatus.NOT_REQUIRED:
                raise ValueError(f"required {label} cannot be NOT_REQUIRED")
            if not required and execution.status is not RemediationStatus.NOT_REQUIRED:
                raise ValueError(f"unrequired {label} must be NOT_REQUIRED")
        if (
            self.resolution_status is ConflictResolutionStatus.UNRESOLVED
            and self.correction_requirement is CorrectionRequirement.NONE
        ):
            raise ValueError("unresolved conflicts require an explicit remediation action")
        if self.resolution_status is ConflictResolutionStatus.INVALID_NON_REMEDIABLE:
            if self.correction_requirement is not CorrectionRequirement.NONE:
                raise ValueError("non-remediable conflicts cannot require remediation")


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
        if any(item.available_at is None for item in self.evidence_references):
            raise ValueError("scorecard evidence requires availability timestamps")
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
    policy_id: str
    agreement_version: str
    policy_snapshot_id: str
    scorecard_version: str
    methodology_version: str
    assessed_at: datetime
    evidence_references: tuple[EvidenceReference, ...]
    entries: tuple[ScorecardEntry, ...]

    def __post_init__(self) -> None:
        Contract.__post_init__(self)
        for name in (
            "provider_id",
            "product",
            "product_version",
            "policy_id",
            "agreement_version",
            "policy_snapshot_id",
            "scorecard_version",
            "methodology_version",
        ):
            require_text(getattr(self, name), name)
        require_utc(self.assessed_at, "assessed_at")
        if not self.evidence_references:
            raise ValueError("scorecard-level evidence is required")
        if any(item.available_at is None for item in self.evidence_references):
            raise ValueError("scorecard-level evidence requires availability timestamps")
        dimensions = tuple(entry.dimension for entry in self.entries)
        if len(set(dimensions)) != len(dimensions):
            raise ValueError("scorecard dimensions must be unique")
        if set(dimensions) != set(ScoreDimension):
            raise ValueError("scorecard requires the exact complete dimension set")
        if any(entry.method_version != self.methodology_version for entry in self.entries):
            raise ValueError("entry method versions must match scorecard methodology")
        if any(entry.assessed_at > self.assessed_at for entry in self.entries):
            raise ValueError("entry assessment cannot follow scorecard assessment")
        weight_total = sum((entry.weight for entry in self.entries), Decimal())
        if weight_total != Decimal("1"):
            raise ValueError("scorecard weights must sum exactly to 1")

    def weighted_score(self) -> Decimal:
        value = sum((entry.raw_score * entry.weight for entry in self.entries), Decimal())
        return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN)
