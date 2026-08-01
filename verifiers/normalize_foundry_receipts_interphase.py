#!/usr/bin/env python3
"""Normalize receipt ownership between mutating foundry phases.

The base normalizer intentionally refuses when an ownership record's active
output no longer matches the current corpus. Between two admitted phases that
is too early: the new phase has already written both the new bytes and a new
receipt, but ownership has not yet transferred.

This controller preserves the same fail-closed rules while allowing exactly
one lawful transition:

* the previous active receipt remains internally valid;
* a new active receipt claims the same output path;
* exactly one claimant matches the current BLAKE3 digest;
* all historical archives remain byte-identical.

Unexplained single-claim drift still refuses.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import normalize_foundry_receipts as base


def validate_existing_ownership_for_transition(root: Path, ownership: dict[str, Any]) -> None:
    """Validate history and receipt claims, deferring only current-owner drift.

    Current-output agreement is recomputed after all active claimants are
    observed. This permits a newly admitted exact claimant to supersede the
    prior owner without permitting an unclaimed mutation.
    """
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
    plan = ORIGINAL_DERIVE_PLAN(root, existing)
    _receipts, claims, current = base.analyze(root)
    for key, claimants in sorted(claims.items()):
        if len(claimants) == 1 and claimants[0]["expected_digest"] != current[key]:
            raise base.Refusal(
                "RECEIPT_ACTIVE_OUTPUT_DRIFT",
                f"{key}: expected {claimants[0]['expected_digest']}, observed {current[key]}",
            )
    return plan


ORIGINAL_DERIVE_PLAN = base.derive_plan
base.validate_existing_ownership = validate_existing_ownership_for_transition
base.derive_plan = derive_transition_plan


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
        value = base.report(root, ownership, args.command)
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
