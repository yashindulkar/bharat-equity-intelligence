"""Immutable content-addressed JSON evidence and deterministic manifests."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from bharat_equity.domain.models import DatasetManifest, require_utc


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def content_hash(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_json(value)).hexdigest()


class ImmutableEvidenceStore:
    def __init__(self, root: Path) -> None:
        self.root = root

    def put(self, payload: dict[str, Any]) -> str:
        digest = content_hash(payload)
        target = (
            self.root
            / digest.removeprefix("sha256:")[:2]
            / f"{digest.removeprefix('sha256:')}.json"
        )
        target.parent.mkdir(parents=True, exist_ok=True)
        encoded = canonical_json(payload)
        if target.exists() and target.read_bytes() != encoded:
            raise RuntimeError("content-address collision")
        if not target.exists():
            target.write_bytes(encoded)
        return digest


def build_manifest(
    dataset_id: str, record_hashes: list[str], cutoff: datetime, rejected_count: int = 0
) -> DatasetManifest:
    require_utc(cutoff, "cutoff")
    hashes = tuple(sorted(set(record_hashes)))
    identity = {
        "dataset_id": dataset_id,
        "cutoff": cutoff.isoformat(),
        "record_hashes": hashes,
        "rejected_count": rejected_count,
        "schema_version": "1.0.0",
    }
    return DatasetManifest(
        dataset_id, cutoff, cutoff, hashes, rejected_count, content_hash(identity)
    )
