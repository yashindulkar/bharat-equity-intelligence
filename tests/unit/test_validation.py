from bharat_equity.application.validation import REASON_CLASSIFICATION, ReasonSeverity, eligibility
from bharat_equity.domain.errors import ReasonCode
from bharat_equity.domain.models import EligibilityStatus


def test_every_reason_code_has_explicit_classification() -> None:
    assert set(REASON_CLASSIFICATION) == set(ReasonCode)


def test_every_hard_reason_blocks() -> None:
    for code, severity in REASON_CLASSIFICATION.items():
        result = eligibility("SYNTHETIC-SECURITY", {code})
        if severity is ReasonSeverity.HARD_BLOCK:
            assert result.status is EligibilityStatus.DATA_BLOCKED
        elif severity is ReasonSeverity.INSUFFICIENT_EVIDENCE:
            assert result.status is EligibilityStatus.INSUFFICIENT_EVIDENCE
