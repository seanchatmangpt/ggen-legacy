#!/usr/bin/env python3
"""Independent verifier for one five-receipt ecosystem ALIVE cell."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

KINDS = ("source", "validation", "falsifier", "ggen", "replay")


class Refusal(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message

    def payload(self) -> dict[str, str]:
        return {
            "schema": "ggen-legacy.ecosystem-alive.cell-refusal/v1",
            "code": self.code,
            "message": self.message,
        }


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise Refusal("CELL-JSON-OBJECT", f"{path} is not an object")
    return value


def kind(value: dict[str, Any]) -> str | None:
    if value.get("schema") == "ggen-legacy.source-reconstitution.receipt/v1":
        return "source"
    observed = value.get("receipt_kind") or value.get("kind")
    return str(observed) if observed else None


def verify_digest(value: dict[str, Any]) -> None:
    digest = value.get("receipt_digest")
    if not isinstance(digest, str) or not digest.startswith("sha256:"):
        raise Refusal("CELL-DIGEST-MISSING", f"{kind(value)} receipt lacks SHA-256 digest")
    unsigned = {key: item for key, item in value.items() if key != "receipt_digest" and not key.startswith("_")}
    expected = "sha256:" + sha256(unsigned)
    if digest != expected:
        raise Refusal("CELL-DIGEST-MISMATCH", f"{kind(value)} expected {expected}, observed {digest}")


def verify_source(value: dict[str, Any], repository: str, canonical_sha: str) -> None:
    if value.get("repository") != repository:
        raise Refusal("CELL-SOURCE-REPOSITORY", f"expected {repository}, observed {value.get('repository')}")
    observed = value.get("canonical_sha") or value.get("sha")
    if observed != canonical_sha or value.get("sha") != canonical_sha:
        raise Refusal("CELL-SOURCE-IDENTITY", f"expected {canonical_sha}, observed {observed}/{value.get('sha')}")
    if value.get("standing") != "ALIVE" or value.get("clean_before_execution") is not True:
        raise Refusal("CELL-SOURCE-NOT-ALIVE", str(value.get("standing")))
    if not value.get("source_tree"):
        raise Refusal("CELL-SOURCE-TREE-MISSING", repository)


def verify_cell(receipts: Path, repository: str, canonical_sha: str) -> dict[str, Any]:
    indexed: dict[str, dict[str, Any]] = {}
    paths: dict[str, str] = {}
    for path in sorted(receipts.glob("*.json")):
        value = load(path)
        observed_kind = kind(value)
        if observed_kind not in KINDS:
            continue
        if observed_kind in indexed:
            raise Refusal("CELL-DUPLICATE-RECEIPT", observed_kind)
        indexed[observed_kind] = value
        paths[observed_kind] = str(path)
    missing = [item for item in KINDS if item not in indexed]
    if missing:
        raise Refusal("CELL-RECEIPT-MISSING", ",".join(missing))

    for receipt_kind in KINDS:
        value = indexed[receipt_kind]
        if value.get("repository") != repository:
            raise Refusal("CELL-REPOSITORY-MISMATCH", f"{receipt_kind}: {value.get('repository')}")
        if value.get("standing") != "ALIVE":
            raise Refusal("CELL-STANDING-NOT-ALIVE", f"{receipt_kind}: {value.get('standing')}")
        if value.get("promotion_granted") is True:
            raise Refusal("CELL-ILLEGAL-PROMOTION", receipt_kind)
        observed_sha = value.get("canonical_sha") or value.get("sha")
        if observed_sha != canonical_sha:
            raise Refusal("CELL-SHA-MISMATCH", f"{receipt_kind}: {observed_sha}")
        verify_digest(value)

    verify_source(indexed["source"], repository, canonical_sha)
    validation = indexed["validation"]
    if not validation.get("results") or any(item.get("exit_code") != 0 for item in validation["results"]):
        raise Refusal("CELL-VALIDATION-FAILED", repository)
    falsifier = indexed["falsifier"]
    if falsifier.get("refusal_code") != "CELL-SOURCE-IDENTITY" or falsifier.get("mutation_refused") is not True:
        raise Refusal("CELL-FALSIFIER-INVALID", repository)
    ggen = indexed["ggen"]
    if ggen.get("graph_valid") is not True or ggen.get("receipt_verified") is not True or ggen.get("matrix_row_exact") is not True:
        raise Refusal("CELL-GGEN-CONTRACT-OPEN", repository)
    replay = indexed["replay"]
    if replay.get("run_count") != 2 or replay.get("outcomes_equal") is not True or replay.get("tracked_drift") != 0:
        raise Refusal("CELL-REPLAY-FAILED", repository)

    report = {
        "schema": "ggen-legacy.ecosystem-alive.cell-report/v1",
        "repository": repository,
        "canonical_sha": canonical_sha,
        "receipt_kinds": list(KINDS),
        "receipt_paths": paths,
        "standing": "ALIVE",
        "promotion_granted": False,
        "direct_actuation": False,
    }
    report["cell_digest"] = "sha256:" + sha256(report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    source = sub.add_parser("source")
    source.add_argument("--receipt", type=Path, required=True)
    source.add_argument("--repository", required=True)
    source.add_argument("--sha", required=True)
    cell = sub.add_parser("cell")
    cell.add_argument("--receipts", type=Path, required=True)
    cell.add_argument("--repository", required=True)
    cell.add_argument("--sha", required=True)
    cell.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "source":
            verify_source(load(args.receipt), args.repository, args.sha)
            print(json.dumps({"standing": "ALIVE", "repository": args.repository, "canonical_sha": args.sha}, sort_keys=True))
        else:
            report = verify_cell(args.receipts, args.repository, args.sha)
            text = json.dumps(report, indent=2, sort_keys=True) + "\n"
            if args.output:
                args.output.parent.mkdir(parents=True, exist_ok=True)
                args.output.write_text(text, encoding="utf-8")
            print(text, end="")
        return 0
    except Refusal as refusal:
        print(json.dumps(refusal.payload(), indent=2, sort_keys=True), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
