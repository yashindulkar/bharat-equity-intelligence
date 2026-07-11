"""Fail-closed Phase 1 research eligibility gates."""

from __future__ import annotations

from bharat_equity.domain.errors import ReasonCode
from bharat_equity.domain.models import (
    AbstentionReason,
    EligibilityStatus,
    ResearchEligibilityResult,
)


def eligibility(security_id: str, failures: set[ReasonCode]) -> ResearchEligibilityResult:
    ordered = tuple(AbstentionReason(code, code.value) for code in sorted(failures, key=str))
    hard = {
        ReasonCode.DATA_STALE,
        ReasonCode.CRITICAL_FIELD_MISSING,
        ReasonCode.PROVIDER_CONFLICT,
        ReasonCode.UNSUPPORTED_CORPORATE_ACTION,
        ReasonCode.IDENTITY_CONFLICT,
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
