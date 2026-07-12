import json
from datetime import UTC, datetime

import pytest

from bharat_equity.cli import run
from bharat_equity.domain.errors import DomainError, ReasonCode
from bharat_equity.infrastructure.storage import (
    AppliedActionLedger,
    ImmutableEvidenceStore,
    build_manifest,
)


def test_manifest_and_writes_are_deterministic(tmp_path) -> None:
    store = ImmutableEvidenceStore(tmp_path)
    payload = {"scope": "SYNTHETIC", "value": "IMPOSSIBLE"}
    assert store.put(payload) == store.put(payload)
    cutoff = datetime(2025, 6, 15, tzinfo=UTC)
    assert build_manifest("SYNTHETIC", [store.put(payload)], cutoff) == build_manifest(
        "SYNTHETIC", [store.put(payload)], cutoff
    )


def test_verified_read_detects_corruption(tmp_path) -> None:
    store = ImmutableEvidenceStore(tmp_path)
    digest = store.put({"scope": "SYNTHETIC", "value": "ORIGINAL"})
    raw = digest.removeprefix("sha256:")
    target = tmp_path / raw[:2] / f"{raw}.json"
    target.write_text(json.dumps({"scope": "SYNTHETIC", "value": "CORRUPTED"}))
    with pytest.raises(DomainError) as error:
        store.get(digest)
    assert error.value.code is ReasonCode.EVIDENCE_INTEGRITY_FAILURE


def test_existing_object_is_not_overwritten(tmp_path) -> None:
    store = ImmutableEvidenceStore(tmp_path)
    payload = {"scope": "SYNTHETIC", "value": "IMMUTABLE"}
    digest = store.put(payload)
    assert store.put(payload) == digest
    assert store.get(digest) == payload


def test_manifest_accounts_for_duplicates() -> None:
    cutoff = datetime(2025, 6, 15, tzinfo=UTC)
    digest = "sha256:" + "a" * 64
    manifest = build_manifest("SYNTHETIC", [digest, digest], cutoff, rejected_count=1)
    assert manifest.total_input_count == 3
    assert manifest.unique_record_count == 1
    assert manifest.duplicate_count == 1
    assert manifest.rejected_count == 1
    assert manifest.reason_codes == (ReasonCode.DUPLICATE_SOURCE_RECORD,)


def test_atomic_publish_failure_leaves_no_object(tmp_path, monkeypatch) -> None:
    store = ImmutableEvidenceStore(tmp_path)

    def fail_link(source, target) -> None:
        raise OSError("SYNTHETIC injected publish failure")

    monkeypatch.setattr("bharat_equity.infrastructure.storage.os.link", fail_link)
    with pytest.raises(DomainError) as error:
        store.put({"scope": "SYNTHETIC", "value": "PARTIAL"})
    assert error.value.code is ReasonCode.EVIDENCE_INTEGRITY_FAILURE
    assert not list(tmp_path.rglob("*.json"))


def test_ledger_verified_read_detects_corruption(tmp_path) -> None:
    ledger = AppliedActionLedger(tmp_path)
    result_hash = "sha256:" + "b" * 64
    identity = ledger.record("SYNTHETIC-ACTION", "SYNTHETIC-SERIES", "1", result_hash)
    raw = identity.removeprefix("sha256:")
    target = tmp_path / raw[:2] / f"{raw}.ledger.json"
    target.write_text('{"corrupted":true}')
    with pytest.raises(DomainError) as error:
        ledger.get(identity)
    assert error.value.code is ReasonCode.EVIDENCE_INTEGRITY_FAILURE


def test_cli_rejects_future_record_with_reason_code() -> None:
    result = run(datetime(2025, 6, 15, tzinfo=UTC))
    assert result["reason_codes"] == ["FUTURE_INFORMATION_REJECTED"]
    assert result["scope"] == "SYNTHETIC_ONLY_NOT_INVESTMENT_ADVICE"
