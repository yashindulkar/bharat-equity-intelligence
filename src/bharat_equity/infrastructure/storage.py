"""Atomic content-addressed synthetic evidence, ledgers, and deterministic manifests."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

from bharat_equity.domain.errors import DomainError, ReasonCode
from bharat_equity.domain.models import DatasetManifest, require_text, require_utc

MAX_EVIDENCE_BYTES = 4 * 1024 * 1024


def canonical_json(value: Any) -> bytes:
    try:
        return json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        ).encode()
    except (TypeError, ValueError) as error:
        raise DomainError(
            ReasonCode.EVIDENCE_INTEGRITY_FAILURE,
            "payload is not canonical finite JSON",
        ) from error


def content_hash(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_json(value)).hexdigest()


def _validate_digest(digest: str) -> str:
    require_text(digest, "digest")
    raw = digest.removeprefix("sha256:")
    if not digest.startswith("sha256:") or len(raw) != 64:
        raise DomainError(ReasonCode.EVIDENCE_INTEGRITY_FAILURE, "invalid SHA-256 digest")
    try:
        int(raw, 16)
    except ValueError as error:
        raise DomainError(
            ReasonCode.EVIDENCE_INTEGRITY_FAILURE, "invalid SHA-256 digest"
        ) from error
    return raw


def _atomic_create(target: Path, encoded: bytes) -> bool:
    """Publish with an exclusive hard link; an existing object is never overwritten."""
    target.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=".pending-", dir=target.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
        try:
            os.link(temporary, target)
            published = True
        except FileExistsError:
            published = False
        directory = os.open(target.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
        return published
    finally:
        temporary.unlink(missing_ok=True)


def _read_limited(path: Path) -> bytes:
    try:
        with path.open("rb") as stream:
            encoded = stream.read(MAX_EVIDENCE_BYTES + 1)
    except OSError as error:
        raise DomainError(
            ReasonCode.EVIDENCE_INTEGRITY_FAILURE, "stored object unavailable"
        ) from error
    if len(encoded) > MAX_EVIDENCE_BYTES:
        raise DomainError(ReasonCode.EVIDENCE_INTEGRITY_FAILURE, "stored object exceeds size limit")
    return encoded


class ImmutableEvidenceStore:
    def __init__(self, root: Path) -> None:
        self.root = root

    def _path(self, digest: str) -> Path:
        raw = _validate_digest(digest)
        return self.root / raw[:2] / f"{raw}.json"

    def put(self, payload: dict[str, Any]) -> str:
        encoded = canonical_json(payload)
        if len(encoded) > MAX_EVIDENCE_BYTES:
            raise DomainError(ReasonCode.EVIDENCE_INTEGRITY_FAILURE, "evidence exceeds size limit")
        digest = "sha256:" + hashlib.sha256(encoded).hexdigest()
        target = self._path(digest)
        try:
            published = _atomic_create(target, encoded)
        except OSError as error:
            raise DomainError(
                ReasonCode.EVIDENCE_INTEGRITY_FAILURE, "atomic evidence publish failed"
            ) from error
        if not published and _read_limited(target) != encoded:
            raise DomainError(ReasonCode.EVIDENCE_INTEGRITY_FAILURE, "content-address collision")
        return digest

    def get(self, digest: str) -> dict[str, Any]:
        target = self._path(digest)
        encoded = _read_limited(target)
        actual = "sha256:" + hashlib.sha256(encoded).hexdigest()
        if actual != digest:
            raise DomainError(ReasonCode.EVIDENCE_INTEGRITY_FAILURE, "evidence digest mismatch")
        try:
            payload = json.loads(encoded)
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise DomainError(
                ReasonCode.EVIDENCE_INTEGRITY_FAILURE, "evidence is invalid JSON"
            ) from error
        if not isinstance(payload, dict) or canonical_json(payload) != encoded:
            raise DomainError(
                ReasonCode.EVIDENCE_INTEGRITY_FAILURE, "evidence is not canonical JSON"
            )
        return payload


class AppliedActionLedger:
    """Durable create-only action application records."""

    def __init__(self, root: Path) -> None:
        self.root = root

    @staticmethod
    def identity(action_identity: str, target_series_id: str, method_version: str) -> str:
        for name, value in (
            ("action_identity", action_identity),
            ("target_series_id", target_series_id),
            ("method_version", method_version),
        ):
            require_text(value, name)
        return content_hash(
            {
                "action_identity": action_identity,
                "target_series_id": target_series_id,
                "method_version": method_version,
            }
        )

    def record(
        self,
        action_identity: str,
        target_series_id: str,
        method_version: str,
        result_evidence_hash: str,
    ) -> str:
        _validate_digest(result_evidence_hash)
        identity = self.identity(action_identity, target_series_id, method_version)
        raw = _validate_digest(identity)
        target = self.root / raw[:2] / f"{raw}.ledger.json"
        payload = canonical_json(
            {
                "action_identity": action_identity,
                "target_series_id": target_series_id,
                "method_version": method_version,
                "ledger_identity": identity,
                "result_evidence_hash": result_evidence_hash,
            }
        )
        try:
            published = _atomic_create(target, payload)
        except OSError as error:
            raise DomainError(
                ReasonCode.EVIDENCE_INTEGRITY_FAILURE, "atomic ledger publish failed"
            ) from error
        if not published:
            self.get(identity)
            raise DomainError(ReasonCode.DUPLICATE_CORPORATE_ACTION, "application already recorded")
        return identity

    def get(self, identity: str) -> dict[str, Any]:
        raw = _validate_digest(identity)
        target = self.root / raw[:2] / f"{raw}.ledger.json"
        encoded = _read_limited(target)
        try:
            payload = json.loads(encoded)
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise DomainError(
                ReasonCode.EVIDENCE_INTEGRITY_FAILURE, "ledger is invalid JSON"
            ) from error
        if (
            not isinstance(payload, dict)
            or canonical_json(payload) != encoded
            or payload.get("ledger_identity") != identity
        ):
            raise DomainError(ReasonCode.EVIDENCE_INTEGRITY_FAILURE, "ledger verification failed")
        expected = self.identity(
            str(payload.get("action_identity", "")),
            str(payload.get("target_series_id", "")),
            str(payload.get("method_version", "")),
        )
        if expected != identity:
            raise DomainError(ReasonCode.EVIDENCE_INTEGRITY_FAILURE, "ledger digest mismatch")
        _validate_digest(str(payload.get("result_evidence_hash", "")))
        return payload


def build_manifest(
    dataset_id: str, record_hashes: list[str], cutoff: datetime, rejected_count: int = 0
) -> DatasetManifest:
    require_text(dataset_id, "dataset_id")
    require_utc(cutoff, "cutoff")
    if rejected_count < 0:
        raise DomainError(ReasonCode.CRITICAL_FIELD_MISSING, "rejected_count must be non-negative")
    hashes = tuple(sorted(set(record_hashes)))
    total = len(record_hashes) + rejected_count
    unique = len(hashes)
    duplicates = len(record_hashes) - unique
    identity = {
        "dataset_id": dataset_id,
        "cutoff": cutoff.isoformat(),
        "record_hashes": hashes,
        "total_input_count": total,
        "unique_record_count": unique,
        "duplicate_count": duplicates,
        "rejected_count": rejected_count,
        "reason_codes": ([ReasonCode.DUPLICATE_SOURCE_RECORD.value] if duplicates else []),
        "schema_version": "1.0.0",
    }
    return DatasetManifest(
        dataset_id,
        cutoff,
        cutoff,
        hashes,
        total,
        unique,
        duplicates,
        rejected_count,
        (ReasonCode.DUPLICATE_SOURCE_RECORD,) if duplicates else (),
        content_hash(identity),
    )
