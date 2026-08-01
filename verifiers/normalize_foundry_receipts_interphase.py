#!/usr/bin/env python3
"""Normalize receipt ownership between mutating foundry phases.

A completed phase may lawfully replace a mutable projection and issue a new
receipt before ownership has transferred. This verifier admits that transition
only when exactly one active claimant matches the current BLAKE3 digest. It
preserves the base normalizer's immutable history and fail-closed replay law.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import normalize_foundry_receipts as base


def validate_existing_history(root: Path, ownership: dict[str, Any]) -> None:
    """Validate receipt claims and archives while deferring owner transfer."""
    for key, record in sorted(ownership.get("outputs", {}).items()):
        if not isinstance(record, dict):
            raise base.Refusal("RECEIPT_OWNERSHIP_RECORD_INVALID", key)
        active = root / str(record.get("active_receipt", ""))
        active_value = base.load_json(active)
        outputs = active_value.get("output_digests", {})
        if outputs.get(key) != record.get("active_digest"):
            raise base.Refusal("RECEIPT_ACTIVE_OWNER_STALE", f"{key}: {active}")
        for superseded in record.get("superseded", []):
            archive = root / str(superseded.get("archive", ""))
            expected_archive_digest = superseded.get("archive_blake3")
            if not archive.is_file() or base.digest_file(archive) != expected_archive_digest:
                raise base.Refusal("RECEIPT_HISTORY_DRIFT", str(archive))
            archived_value = base.load_json(archive)
            if archived_value.get("output_digests", {}).get(key) != superseded.get("expected_digest"):
                raise base.Refusal("RECEIPT_HISTORY_CLAIM_DRIFT", f"{archive}: {key}")


def derive_transition_plan(root: Path, existing: dict[str, Any]) -> dict[str, Any]:
    plan = base.derive_plan(root, existing)
    _receipts, claims, current = base.analyze(root)
    for key, claimants in sorted(claims.items()):
        if len(claimants) == 1 and claimants[0]["expected_digest"] != current[key]:
            raise base.Refusal(
                "RECEIPT_ACTIVE_OUTPUT_DRIFT",
                f"{key}: expected {claimants[0]['expected_digest']}, observed {current[key]}",
            )
    return plan


def report(root: Path, ownership_path: Path, mode: str) -> dict[str, Any]:
    existing = base.load_existing_ownership(ownership_path)
    if ownership_path.exists():
        validate_existing_history(root, existing)
    plan = derive_transition_plan(root, existing)
    if mode == "apply" and plan["filters"]:
        ownership = base.apply_plan(root, ownership_path, plan)
        status = "NORMALIZED"
    else:
        ownership = existing
        status = "NORMALIZATION_REQUIRED" if plan["filters"] else "ALIVE"
    return {
        "schema": "ggen.enterprise-architecture-foundry.interphase-ownership-report/1",
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
    except base.Refusal as refusal:
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
