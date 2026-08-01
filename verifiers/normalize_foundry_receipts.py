#!/usr/bin/env python3
"""Normalize mutable foundry receipt ownership without weakening replay.

Historical receipts are archived byte-for-byte. Active receipts retain only the
output keys they still own. Duplicate claims are resolved only when exactly one
claimant's expected BLAKE3 digest equals the observed current consequence.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

RECEIPT_SCHEMA = "ggen.enterprise-architecture-foundry.receipt/1"
OWNERSHIP_SCHEMA = "ggen.enterprise-architecture-foundry.receipt-ownership/1"


class Refusal(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message

    def payload(self) -> dict[str, str]:
        return {"schema": "ggen.enterprise-architecture-foundry.refusal/1", "code": self.code, "message": self.message}


def blake3_module():
    try:
        import blake3  # type: ignore[import-not-found]
    except ModuleNotFoundError as exc:
        raise Refusal("RECEIPT_BLAKE3_UNAVAILABLE", "install blake3==1.0.9") from exc
    return blake3


def digest_bytes(data: bytes) -> str:
    return blake3_module().blake3(data).hexdigest()


def digest_file(path: Path) -> str:
    try:
        return digest_bytes(path.read_bytes())
    except FileNotFoundError as exc:
        raise Refusal("RECEIPT_OUTPUT_MISSING", str(path)) from exc


def hash_named_bytes(hasher: Any, name: str, value: bytes) -> None:
    encoded = name.encode("utf-8")
    hasher.update(len(encoded).to_bytes(8, "little"))
    hasher.update(encoded)
    hasher.update(len(value).to_bytes(8, "little"))
    hasher.update(value)


def digest_named_outputs(outputs: dict[str, str]) -> str:
    hasher = blake3_module().blake3()
    for name, digest in sorted(outputs.items()):
        hash_named_bytes(hasher, name, digest.encode("utf-8"))
    return hasher.hexdigest()


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise Refusal("RECEIPT_FILE_MISSING", str(path)) from exc
    except json.JSONDecodeError as exc:
        raise Refusal("RECEIPT_JSON_INVALID", f"{path}: {exc}") from exc
    if not isinstance(value, dict):
        raise Refusal("RECEIPT_JSON_NOT_OBJECT", str(path))
    return value


def active_receipts(root: Path) -> list[Path]:
    receipts = root / "foundry" / "receipts"
    if not receipts.is_dir():
        raise Refusal("RECEIPT_DIRECTORY_MISSING", str(receipts))
    return sorted(path for path in receipts.rglob("*.json") if path.is_file())


def validate_receipt(path: Path, receipt: dict[str, Any]) -> None:
    if receipt.get("schema_version") != RECEIPT_SCHEMA:
        raise Refusal("RECEIPT_SCHEMA_INVALID", f"{path}: {receipt.get('schema_version')}")
    outputs = receipt.get("output_digests")
    if not isinstance(outputs, dict):
        raise Refusal("RECEIPT_OUTPUTS_INVALID", str(path))
    observed = digest_named_outputs({str(key): str(value) for key, value in outputs.items()})
    if observed != receipt.get("subject_digest"):
        raise Refusal(
            "RECEIPT_SUBJECT_DIGEST_INVALID",
            f"{path}: expected {receipt.get('subject_digest')}, recomputed {observed}",
        )
    if receipt.get("run_id") != observed[:20]:
        raise Refusal("RECEIPT_RUN_ID_INVALID", f"{path}: expected {observed[:20]}")


def local_output_path(root: Path, key: str) -> Path | None:
    selector, separator, relative = key.partition(":")
    if not separator:
        raise Refusal("RECEIPT_OUTPUT_KEY_INVALID", key)
    if selector in {"projection", "external", "source"}:
        return None
    if selector != "corpus":
        raise Refusal("RECEIPT_REPOSITORY_INVALID", selector)
    path = Path(relative)
    if not relative or path.is_absolute() or ".." in path.parts:
        raise Refusal("RECEIPT_OUTPUT_PATH_INVALID", key)
    return root / path


def load_existing_ownership(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"schema_version": OWNERSHIP_SCHEMA, "outputs": {}, "archives": {}}
    value = load_json(path)
    if value.get("schema_version") != OWNERSHIP_SCHEMA:
        raise Refusal("RECEIPT_OWNERSHIP_SCHEMA_INVALID", str(path))
    if not isinstance(value.get("outputs"), dict) or not isinstance(value.get("archives"), dict):
        raise Refusal("RECEIPT_OWNERSHIP_SHAPE_INVALID", str(path))
    return value


def validate_existing_ownership(root: Path, ownership: dict[str, Any]) -> None:
    for key, record in sorted(ownership.get("outputs", {}).items()):
        if not isinstance(record, dict):
            raise Refusal("RECEIPT_OWNERSHIP_RECORD_INVALID", key)
        active = root / str(record.get("active_receipt", ""))
        active_value = load_json(active)
        outputs = active_value.get("output_digests", {})
        if outputs.get(key) != record.get("active_digest"):
            raise Refusal("RECEIPT_ACTIVE_OWNER_STALE", f"{key}: {active}")
        observed_path = local_output_path(root, key)
        if observed_path is not None and digest_file(observed_path) != record.get("active_digest"):
            raise Refusal("RECEIPT_ACTIVE_OUTPUT_DRIFT", key)
        for superseded in record.get("superseded", []):
            archive = root / str(superseded.get("archive", ""))
            expected_archive_digest = superseded.get("archive_blake3")
            if not archive.is_file() or digest_file(archive) != expected_archive_digest:
                raise Refusal("RECEIPT_HISTORY_DRIFT", str(archive))
            archived_value = load_json(archive)
            if archived_value.get("output_digests", {}).get(key) != superseded.get("expected_digest"):
                raise Refusal("RECEIPT_HISTORY_CLAIM_DRIFT", f"{archive}: {key}")


def analyze(root: Path) -> tuple[dict[str, dict[str, Any]], dict[str, list[dict[str, Any]]], dict[str, str]]:
    receipts: dict[str, dict[str, Any]] = {}
    claims: dict[str, list[dict[str, Any]]] = defaultdict(list)
    current: dict[str, str] = {}
    for path in active_receipts(root):
        relative = path.relative_to(root).as_posix()
        receipt = load_json(path)
        validate_receipt(path, receipt)
        receipts[relative] = receipt
        for key, expected in sorted(receipt["output_digests"].items()):
            output = local_output_path(root, key)
            if output is None:
                continue
            if key not in current:
                current[key] = digest_file(output)
            claims[key].append({"receipt": relative, "expected_digest": str(expected)})
    return receipts, claims, current


def derive_plan(root: Path, existing: dict[str, Any]) -> dict[str, Any]:
    receipts, claims, current = analyze(root)
    ownership_outputs = copy.deepcopy(existing.get("outputs", {}))
    archives = copy.deepcopy(existing.get("archives", {}))
    filters: dict[str, set[str]] = defaultdict(set)
    duplicate_count = 0

    for key, claimants in sorted(claims.items()):
        if len(claimants) == 1:
            continue
        duplicate_count += 1
        matching = [claim for claim in claimants if claim["expected_digest"] == current[key]]
        if not matching:
            raise Refusal(
                "RECEIPT_OUTPUT_UNOWNED",
                f"{key}: current {current[key]} matches none of {[c['expected_digest'] for c in claimants]}",
            )
        if len(matching) != 1:
            raise Refusal("RECEIPT_OWNER_AMBIGUOUS", f"{key}: matching claimants={matching}")
        owner = matching[0]
        superseded: list[dict[str, Any]] = []
        for claimant in claimants:
            if claimant is owner:
                continue
            filters[claimant["receipt"]].add(key)
            receipt = receipts[claimant["receipt"]]
            archive_relative = (
                Path("foundry/receipt-history")
                / Path(claimant["receipt"]).relative_to("foundry/receipts")
            )
            archive_relative = archive_relative.with_name(
                f"{archive_relative.stem}.{receipt['subject_digest'][:16]}{archive_relative.suffix}"
            )
            superseded.append(
                {
                    "receipt": claimant["receipt"],
                    "archive": archive_relative.as_posix(),
                    "expected_digest": claimant["expected_digest"],
                }
            )
        ownership_outputs[key] = {
            "active_receipt": owner["receipt"],
            "active_digest": owner["expected_digest"],
            "observed_digest": current[key],
            "superseded": superseded,
        }

    return {
        "schema_version": OWNERSHIP_SCHEMA,
        "duplicate_output_count": duplicate_count,
        "filters": {receipt: sorted(keys) for receipt, keys in sorted(filters.items())},
        "outputs": ownership_outputs,
        "archives": archives,
    }


def apply_plan(root: Path, ownership_path: Path, plan: dict[str, Any]) -> dict[str, Any]:
    changes: list[dict[str, Any]] = []
    for receipt_relative, keys in sorted(plan["filters"].items()):
        receipt_path = root / receipt_relative
        original_bytes = receipt_path.read_bytes()
        original = json.loads(original_bytes)
        validate_receipt(receipt_path, original)
        archive_relative = (
            Path("foundry/receipt-history") / Path(receipt_relative).relative_to("foundry/receipts")
        ).with_name(
            f"{Path(receipt_relative).stem}.{original['subject_digest'][:16]}.json"
        )
        archive_path = root / archive_relative
        archive_path.parent.mkdir(parents=True, exist_ok=True)
        if archive_path.exists():
            if archive_path.read_bytes() != original_bytes:
                raise Refusal("RECEIPT_HISTORY_COLLISION", str(archive_path))
        else:
            archive_path.write_bytes(original_bytes)

        filtered = copy.deepcopy(original)
        for key in keys:
            filtered["output_digests"].pop(key, None)
        filtered["subject_digest"] = digest_named_outputs(filtered["output_digests"])
        filtered["run_id"] = filtered["subject_digest"][:20]
        receipt_path.write_bytes(canonical_json(filtered))
        changes.append(
            {
                "receipt": receipt_relative,
                "archive": archive_relative.as_posix(),
                "archive_blake3": digest_file(archive_path),
                "removed_outputs": keys,
                "active_subject_digest": filtered["subject_digest"],
            }
        )
        for key in keys:
            record = plan["outputs"][key]
            for superseded in record["superseded"]:
                if superseded["receipt"] == receipt_relative:
                    superseded["archive"] = archive_relative.as_posix()
                    superseded["archive_blake3"] = digest_file(archive_path)

    ownership = {
        "schema_version": OWNERSHIP_SCHEMA,
        "policy": "exact-current-digest-single-owner",
        "historical_receipts_immutable": True,
        "active_receipts_replay_current_outputs_only": True,
        "outputs": plan["outputs"],
        "archives": {change["archive"]: change["archive_blake3"] for change in changes},
        "changes": changes,
    }
    ownership["ownership_digest"] = "sha256:" + hashlib.sha256(canonical_json(ownership)).hexdigest()
    ownership_path.parent.mkdir(parents=True, exist_ok=True)
    ownership_path.write_bytes(canonical_json(ownership))
    validate_existing_ownership(root, ownership)
    # Re-run active receipt validation and present-output replay after mutation.
    receipts, claims, current = analyze(root)
    for key, claimants in claims.items():
        if len(claimants) > 1:
            raise Refusal("RECEIPT_DUPLICATE_REMAINS_ACTIVE", f"{key}: {claimants}")
        if claimants[0]["expected_digest"] != current[key]:
            raise Refusal("RECEIPT_ACTIVE_OUTPUT_DRIFT", key)
    return ownership


def report(root: Path, ownership_path: Path, mode: str) -> dict[str, Any]:
    existing = load_existing_ownership(ownership_path)
    if ownership_path.exists():
        validate_existing_ownership(root, existing)
    plan = derive_plan(root, existing)
    if mode == "apply" and plan["filters"]:
        ownership = apply_plan(root, ownership_path, plan)
        status = "NORMALIZED"
    else:
        ownership = existing
        status = "NORMALIZATION_REQUIRED" if plan["filters"] else "ALIVE"
    return {
        "schema": "ggen.enterprise-architecture-foundry.receipt-ownership-report/1",
        "status": status,
        "normalization_required": bool(plan["filters"]),
        "duplicate_outputs_observed": plan["duplicate_output_count"],
        "receipt_filters": plan["filters"],
        "ownership_manifest": str(ownership_path),
        "ownership_records": len(ownership.get("outputs", {})),
        "direct_actuation": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("audit", "apply"))
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--ownership", type=Path, default=Path("foundry/receipt-ownership.json"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    ownership = args.ownership if args.ownership.is_absolute() else root / args.ownership
    try:
        value = report(root, ownership, args.command)
    except Refusal as refusal:
        print(json.dumps(refusal.payload(), indent=2, sort_keys=True), file=sys.stderr)
        return 2
    text = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    if args.command == "audit" and value["normalization_required"]:
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
