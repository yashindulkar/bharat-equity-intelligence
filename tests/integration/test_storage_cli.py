from datetime import UTC, datetime

from bharat_equity.cli import run
from bharat_equity.infrastructure.storage import ImmutableEvidenceStore, build_manifest


def test_manifest_and_writes_are_deterministic(tmp_path) -> None:
    store = ImmutableEvidenceStore(tmp_path)
    payload = {"scope": "SYNTHETIC", "value": "IMPOSSIBLE"}
    assert store.put(payload) == store.put(payload)
    cutoff = datetime(2025, 6, 15, tzinfo=UTC)
    assert build_manifest("SYNTHETIC", [store.put(payload)], cutoff) == build_manifest(
        "SYNTHETIC", [store.put(payload)], cutoff
    )


def test_cli_rejects_future_record_with_reason_code() -> None:
    result = run(datetime(2025, 6, 15, tzinfo=UTC))
    assert result["reason_codes"] == ["FUTURE_INFORMATION_REJECTED"]
    assert result["scope"] == "SYNTHETIC_ONLY_NOT_INVESTMENT_ADVICE"
