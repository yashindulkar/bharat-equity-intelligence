"""Fail-closed Phase 1 research eligibility gates."""

from __future__ import annotations

from enum import StrEnum

from bharat_equity.domain.errors import ReasonCode
from bharat_equity.domain.models import (
    AbstentionReason,
    EligibilityStatus,
    ResearchEligibilityResult,
)


class ReasonSeverity(StrEnum):
    HARD_BLOCK = "HARD_BLOCK"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    WARNING = "WARNING"


REASON_CLASSIFICATION: dict[ReasonCode, ReasonSeverity] = {
    ReasonCode.DATA_STALE: ReasonSeverity.HARD_BLOCK,
    ReasonCode.CRITICAL_FIELD_MISSING: ReasonSeverity.HARD_BLOCK,
    ReasonCode.PROVIDER_CONFLICT: ReasonSeverity.HARD_BLOCK,
    ReasonCode.FUTURE_INFORMATION_REJECTED: ReasonSeverity.HARD_BLOCK,
    ReasonCode.UNSUPPORTED_CORPORATE_ACTION: ReasonSeverity.HARD_BLOCK,
    ReasonCode.DUPLICATE_CORPORATE_ACTION: ReasonSeverity.HARD_BLOCK,
    ReasonCode.INVALID_PRICE_BAR: ReasonSeverity.HARD_BLOCK,
    ReasonCode.INVALID_TIMESTAMP: ReasonSeverity.HARD_BLOCK,
    ReasonCode.IDENTITY_CONFLICT: ReasonSeverity.HARD_BLOCK,
    ReasonCode.INSUFFICIENT_HISTORY: ReasonSeverity.INSUFFICIENT_EVIDENCE,
    ReasonCode.DATA_BLOCKED: ReasonSeverity.HARD_BLOCK,
    ReasonCode.NO_SUITABLE_CANDIDATE: ReasonSeverity.INSUFFICIENT_EVIDENCE,
    ReasonCode.DUPLICATE_SOURCE_RECORD: ReasonSeverity.HARD_BLOCK,
    ReasonCode.EVIDENCE_INTEGRITY_FAILURE: ReasonSeverity.HARD_BLOCK,
    ReasonCode.PERMISSION_UNKNOWN: ReasonSeverity.HARD_BLOCK,
    ReasonCode.AGREEMENT_EXPIRED: ReasonSeverity.HARD_BLOCK,
    ReasonCode.PURPOSE_NOT_PERMITTED: ReasonSeverity.HARD_BLOCK,
    ReasonCode.PIT_UNSUPPORTED: ReasonSeverity.HARD_BLOCK,
    ReasonCode.RAW_RETENTION_FORBIDDEN: ReasonSeverity.HARD_BLOCK,
    ReasonCode.REVISION_HANDLING_UNKNOWN: ReasonSeverity.HARD_BLOCK,
    ReasonCode.DELISTED_COVERAGE_MISSING: ReasonSeverity.HARD_BLOCK,
    ReasonCode.PROVIDER_NOT_APPROVED: ReasonSeverity.HARD_BLOCK,
}


def eligibility(security_id: str, failures: set[ReasonCode]) -> ResearchEligibilityResult:
    ordered = tuple(AbstentionReason(code, code.value) for code in sorted(failures, key=str))
    if set(REASON_CLASSIFICATION) != set(ReasonCode):
        raise RuntimeError("every ReasonCode must have an explicit classification")
    hard = {
        code
        for code, severity in REASON_CLASSIFICATION.items()
        if severity is ReasonSeverity.HARD_BLOCK
    }
    status = (
        EligibilityStatus.DATA_BLOCKED
        if failures & hard
        else (
            EligibilityStatus.INSUFFICIENT_EVIDENCE
            if failures
            else EligibilityStatus.ELIGIBLE_FOR_RESEARCH
        )
    )
    return ResearchEligibilityResult(security_id, status, ordered)
