#!/usr/bin/env python3
"""Independent promotion verifier for the ggen ecosystem ALIVE program."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

REQUIRED_KINDS = ("source", "validation", "falsifier", "ggen", "replay")


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def receipt_kind(value: dict[str, Any]) -> str | None:
    if value.get("schema") == "ggen-legacy.source-reconstitution.receipt/v1":
        return "source"
    return value.get("receipt_kind") or value.get("kind")


def verify_digest(value: dict[str, Any]) -> bool:
    digest = value.get("receipt_digest")
    if not isinstance(digest, str) or not digest.startswith("sha256:"):
        return True
    copy = {key: item for key, item in value.items() if not key.startswith("_")}
    copy.pop("receipt_digest", None)
    return digest == "sha256:" + sha256(copy)


def index_receipts(root: Path) -> tuple[dict[tuple[str, str], dict[str, Any]], list[str]]:
    index: dict[tuple[str, str], dict[str, Any]] = {}
    errors: list[str] = []
    for path in sorted(root.rglob("*.json")) if root.exists() else []:
        try:
            value = load(path)
        except Exception as exc:
            errors.append(f"unreadable receipt {path}: {exc}")
            continue
        if not isinstance(value, dict):
            continue
        repository = value.get("repository")
        kind = receipt_kind(value)
        if not repository or not kind:
            continue
        key = (str(repository), str(kind))
        if key in index:
            errors.append(f"duplicate receipt {repository}/{kind}: {index[key].get('_path')} and {path}")
            continue
        value["_path"] = str(path)
        index[key] = value
    return index, errors


def verify(manifest_path: Path, receipts_root: Path, foundry_state_path: Path) -> dict[str, Any]:
    manifest = load(manifest_path)
    receipts, errors = index_receipts(receipts_root)
    repositories = [item for item in manifest["repositories"] if item.get("product_reconstitution", True)]
    cells: list[dict[str, Any]] = []

    for repository in sorted(repositories, key=lambda item: item["repository"]):
        name = repository["repository"]
        source_sha = repository["canonical_reconstruction_sha"]
        cell_errors: list[str] = []
        cell_receipts: dict[str, str] = {}
        for kind in REQUIRED_KINDS:
            receipt = receipts.get((name, kind))
            if not receipt:
                cell_errors.append(f"missing {kind} receipt")
                continue
            cell_receipts[kind] = receipt["_path"]
            if receipt.get("standing") != "ALIVE":
                cell_errors.append(f"{kind} standing={receipt.get('standing')}")
            observed_sha = receipt.get("canonical_sha") or receipt.get("sha")
            if observed_sha and observed_sha != source_sha:
                cell_errors.append(f"{kind} source mismatch {observed_sha} != {source_sha}")
            if not verify_digest(receipt):
                cell_errors.append(f"{kind} SHA-256 receipt digest mismatch")
            if receipt.get("promotion_granted") is True:
                cell_errors.append(f"{kind} receipt illegally grants promotion")
        cells.append({
            "repository": name,
            "canonical_sha": source_sha,
            "standing": "ALIVE" if not cell_errors else "PARTIAL_ALIVE",
            "errors": cell_errors,
            "receipts": cell_receipts,
        })
        errors.extend(f"{name}: {message}" for message in cell_errors)

    foundry = load(foundry_state_path) if foundry_state_path.exists() else {}
    workstreams = foundry.get("workstreams", {})
    missing_workstreams = [letter for letter in "ABCDEFGHIJK" if workstreams.get(letter, {}).get("status") != "ADMITTED"]
    if missing_workstreams:
        errors.append("foundry workstreams not ADMITTED: " + ",".join(missing_workstreams))

    aggregate = {
        "schema": "ggen-legacy.ecosystem-alive.promotion/v1",
        "manifest": str(manifest_path),
        "manifest_digest": "sha256:" + sha256(manifest),
        "product_repository_count": len(repositories),
        "required_receipt_kinds": list(REQUIRED_KINDS),
        "cells": cells,
        "foundry_workstreams": {letter: workstreams.get(letter, {}).get("status", "UNKNOWN") for letter in "ABCDEFGHIJK"},
        "standing": "ALIVE" if not errors else "PARTIAL_ALIVE",
        "promotion_granted": not errors,
        "errors": errors,
        "direct_actuation": False,
    }
    aggregate["promotion_digest"] = "sha256:" + sha256(aggregate)
    return aggregate


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=Path("authority/ecosystem-reconstitution/2026-07-31.repositories.json"))
    parser.add_argument("--receipts", type=Path, default=Path("target/ecosystem-alive/receipts"))
    parser.add_argument("--foundry-state", type=Path, default=Path("foundry/workstreams/state.json"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        report = verify(args.manifest, args.receipts, args.foundry_state)
    except Exception as exc:
        print(json.dumps({"schema": "ggen-legacy.ecosystem-alive.refusal/v1", "code": "ALIVE-VERIFY-INPUT", "message": str(exc)}, indent=2), file=sys.stderr)
        return 2
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if report["promotion_granted"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
