"""Offline synthetic PIT demonstration; it emits research eligibility, never advice."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from datetime import UTC, datetime
from typing import cast

from bharat_equity.application.temporal import VintageView, select_vintage
from bharat_equity.domain.errors import ReasonCode
from bharat_equity.infrastructure.storage import build_manifest
from bharat_equity.providers.synthetic import SyntheticProvider


def run(cutoff: datetime) -> dict[str, object]:
    provider = SyntheticProvider()
    filings = list(provider.fetch_fundamentals().records)
    selected = select_vintage(
        filings,
        business_at=cutoff,
        cutoff=cutoff,
        view=VintageView.AS_KNOWN_THEN,
    )
    rejected = [item.filing_id for item in filings if item.usable_from > cutoff]
    results = [
        provider.fetch_security_master(),
        provider.fetch_prices(),
        provider.fetch_corporate_actions(),
        provider.fetch_fundamentals(),
    ]
    manifest = build_manifest(
        "SYNTHETIC-PHASE1", [item.raw_content_hash for item in results], cutoff, len(rejected)
    )
    reasons = [ReasonCode.FUTURE_INFORMATION_REJECTED.value] if rejected else []
    return {
        "scope": "SYNTHETIC_ONLY_NOT_INVESTMENT_ADVICE",
        "cutoff": cutoff.isoformat(),
        "view": VintageView.AS_KNOWN_THEN.value,
        "available_filing": None if selected is None else selected.filing_id,
        "rejected_future_records": rejected,
        "status": "ELIGIBLE_FOR_RESEARCH" if selected else "INSUFFICIENT_EVIDENCE",
        "reason_codes": reasons,
        "manifest": manifest.to_dict(),
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cutoff", default="2025-06-15T00:00:00+00:00")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    cutoff = datetime.fromisoformat(args.cutoff).astimezone(UTC)
    result = run(cutoff)
    if args.json:
        print(json.dumps(result, sort_keys=True, indent=2))
    else:
        print("SYNTHETIC OFFLINE RESEARCH-ELIGIBILITY DEMO — NOT A RECOMMENDATION")
        print(f"Status: {result['status']}; available filing: {result['available_filing']}")
        rejected_records = cast(list[str], result["rejected_future_records"])
        reason_codes = cast(list[str], result["reason_codes"])
        print(f"Rejected future records: {', '.join(rejected_records) or 'none'}")
        print(f"Reason codes: {', '.join(reason_codes) or 'none'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
