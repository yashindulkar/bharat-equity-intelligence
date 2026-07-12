"""Narrow, provider-neutral ports."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Protocol

from bharat_equity.domain.models import ValidationStatus


@dataclass(frozen=True, slots=True)
class ProviderResult:
    provider_name: str
    source_identifier: str
    retrieval_timestamp: datetime
    publication_timestamp: datetime | None
    schema_version: str
    raw_content_hash: str
    validation_status: ValidationStatus
    records: tuple[Any, ...]


class SecurityMasterProvider(Protocol):
    def fetch_security_master(self) -> ProviderResult: ...


class PriceDataProvider(Protocol):
    def fetch_prices(self) -> ProviderResult: ...


class CorporateActionsProvider(Protocol):
    def fetch_corporate_actions(self) -> ProviderResult: ...


class FundamentalsProvider(Protocol):
    def fetch_fundamentals(self) -> ProviderResult: ...


class IndexConstituentsProvider(Protocol):
    def fetch_index_constituents(self) -> ProviderResult: ...


class MarketCalendarProvider(Protocol):
    def fetch_market_calendar(self) -> ProviderResult: ...
