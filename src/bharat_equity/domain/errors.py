"""Typed errors and stable machine-readable failure reasons."""

from __future__ import annotations

from enum import StrEnum


class ReasonCode(StrEnum):
    DATA_STALE = "DATA_STALE"
    CRITICAL_FIELD_MISSING = "CRITICAL_FIELD_MISSING"
    PROVIDER_CONFLICT = "PROVIDER_CONFLICT"
    FUTURE_INFORMATION_REJECTED = "FUTURE_INFORMATION_REJECTED"
    UNSUPPORTED_CORPORATE_ACTION = "UNSUPPORTED_CORPORATE_ACTION"
    DUPLICATE_CORPORATE_ACTION = "DUPLICATE_CORPORATE_ACTION"
    INVALID_PRICE_BAR = "INVALID_PRICE_BAR"
    INVALID_TIMESTAMP = "INVALID_TIMESTAMP"
    IDENTITY_CONFLICT = "IDENTITY_CONFLICT"
    INSUFFICIENT_HISTORY = "INSUFFICIENT_HISTORY"
    DATA_BLOCKED = "DATA_BLOCKED"
    NO_SUITABLE_CANDIDATE = "NO_SUITABLE_CANDIDATE"
    DUPLICATE_SOURCE_RECORD = "DUPLICATE_SOURCE_RECORD"


class DomainError(ValueError):
    """A domain failure with a stable reason code."""

    def __init__(self, code: ReasonCode, message: str) -> None:
        self.code = code
        super().__init__(message)
