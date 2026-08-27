#!/usr/bin/env python3
"""Independent receiver for the ggen dashboard language-neutral contract."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

SCHEMA = "https://ggen.io/schema/dashboard-contract/v1"
RECEIPT_SCHEMA = "https://ggen.io/schema/legacy-dashboard-reconstitution-receipt/v1"
VERIFIER_VERSION = "26.8.27"
REQUIRED_STANDING = {
    "UNKNOWN", "UNSUPPORTED", "BLOCKED", "BUILD_BROKEN", "PARTIAL_ALIVE", "ALIVE", "REFUSED"
}
REQUIRED_STAGES = {"OBSERVE", "SELECT", "CONSTRUCT", "PREFLIGHT", "BRCE", "RECEIPT", "REPLAY"}
REQUIRED_PROJECTIONS = {"overview", "resources", "evidence", "authority", "receipts", "replay", "topology"}


class Refusal(RuntimeError):
    pass


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def unique(records: list[dict[str, Any]], field: str, refusal: str) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for record in records:
        value = record.get(field)
        if not isinstance(value, str) or not value:
            raise Refusal(f"REFUSED:{refusal}:MISSING_{field.upper()}")
        if value in index:
            raise Refusal(f"REFUSED:{refusal}:DUPLICATE:{value}")
        index[value] = record
    return index


def validate_contract(payload: dict[str, Any]) -> dict[str, Any]:
    if payload.get("schema") != SCHEMA:
        raise Refusal("REFUSED:CONTRACT_SCHEMA")
    if payload.get("brceRequired") is not True:
        raise Refusal("REFUSED:BRCE_NOT_REQUIRED")
    version = payload.get("contractVersion")
    if not isinstance(version, str) or not version:
        raise Refusal("REFUSED:CONTRACT_VERSION")

    standing = payload.get("standing")
    stages = payload.get("authorityStages")
    intents = payload.get("intentKinds")
    projections = payload.get("projections")
    if not all(isinstance(value, list) for value in (standing, stages, intents, projections)):
        raise Refusal("REFUSED:CONTRACT_COLLECTIONS")

    standing_by_code = unique(standing, "code", "STANDING_IDENTITY")
    missing_standing = sorted(REQUIRED_STANDING - standing_by_code.keys())
    if missing_standing:
        raise Refusal("REFUSED:STANDING_COVERAGE:" + ",".join(missing_standing))
    if any(record.get("allowsDo") is not False for record in standing):
        raise Refusal("REFUSED:STANDING_DO_AUTHORITY")

    stage_by_code = unique(stages, "code", "STAGE_IDENTITY")
    missing_stages = sorted(REQUIRED_STAGES - stage_by_code.keys())
    if missing_stages:
        raise Refusal("REFUSED:STAGE_COVERAGE:" + ",".join(missing_stages))
    do_stages = sorted(code for code, record in stage_by_code.items() if record.get("allowsDo") is True)
    if do_stages != ["BRCE"]:
        raise Refusal("REFUSED:DO_AUTHORITY_TOPOLOGY:" + ",".join(do_stages))
    orders = [record.get("order") for record in stages]
    if any(not isinstance(value, int) for value in orders) or len(set(orders)) != len(orders):
        raise Refusal("REFUSED:STAGE_ORDER_IDENTITY")

    intent_by_code = unique(intents, "code", "INTENT_IDENTITY")
    do_intents = sorted(code for code, record in intent_by_code.items() if record.get("allowsDo") is True)
    if do_intents != ["ACTUATE_VIA_BRCE"]:
        raise Refusal("REFUSED:INTENT_AUTHORITY_TOPOLOGY:" + ",".join(do_intents))

    projection_by_id = unique(projections, "id", "PROJECTION_IDENTITY")
    missing_projections = sorted(REQUIRED_PROJECTIONS - projection_by_id.keys())
    if missing_projections:
        raise Refusal("REFUSED:PROJECTION_COVERAGE:" + ",".join(missing_projections))
    route_index = unique(projections, "route", "PROJECTION_ROUTE")

    return {
        "contract_version": version,
        "standing_codes": sorted(standing_by_code),
        "authority_stages": [code for code, _ in sorted(stage_by_code.items(), key=lambda item: item[1]["order"])],
        "do_stage": "BRCE",
        "do_intent": "ACTUATE_VIA_BRCE",
        "projection_ids": sorted(projection_by_id),
        "projection_routes": sorted(route_index),
    }


def manufacture_receipt(raw: bytes, payload: dict[str, Any], source_repo: str, source_sha: str) -> dict[str, Any]:
    if not source_repo or not source_sha:
        raise Refusal("REFUSED:SOURCE_IDENTITY")
    witness = validate_contract(payload)
    body: dict[str, Any] = {
        "schema": RECEIPT_SCHEMA,
        "verifier_version": VERIFIER_VERSION,
        "source": {
            "repository": source_repo,
            "sha": source_sha,
            "contract_sha256": hashlib.sha256(raw).hexdigest(),
        },
        "reconstruction": witness,
        "standing": "PARTIAL_ALIVE",
        "scope": "received-dashboard-contract-only",
        "authority_ceiling": "RECONSTRUCT_ONLY",
        "do_authority": False,
        "self_certifying": False,
        "ggen_certified": False,
    }
    body["receipt"] = {"algorithm": "sha256", "digest": hashlib.sha256(canonical(body)).hexdigest()}
    return body


def verify_receipt_integrity(receipt: dict[str, Any]) -> None:
    identity = receipt.get("receipt")
    if not isinstance(identity, dict) or identity.get("algorithm") != "sha256":
        raise Refusal("REFUSED:RECEIPT_IDENTITY")
    expected = identity.get("digest")
    if not isinstance(expected, str) or len(expected) != 64:
        raise Refusal("REFUSED:RECEIPT_DIGEST")
    unsigned = dict(receipt)
    unsigned.pop("receipt", None)
    actual = hashlib.sha256(canonical(unsigned)).hexdigest()
    if actual != expected:
        raise Refusal("REFUSED:RECEIPT_TAMPER")
    if receipt.get("self_certifying") is not False or receipt.get("ggen_certified") is not False:
        raise Refusal("REFUSED:SELF_CERTIFICATION")
    if receipt.get("do_authority") is not False or receipt.get("authority_ceiling") != "RECONSTRUCT_ONLY":
        raise Refusal("REFUSED:RECEIVER_AUTHORITY")


def verify_command(args: argparse.Namespace) -> int:
    raw = Path(args.contract).read_bytes()
    payload = json.loads(raw)
    receipt = manufacture_receipt(raw, payload, args.source_repo, args.source_sha)
    verify_receipt_integrity(receipt)
    Path(args.out).write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"PARTIAL_ALIVE:contract={receipt['source']['contract_sha256']} receipt={receipt['receipt']['digest']}")
    return 0


def replay_command(args: argparse.Namespace) -> int:
    left = json.loads(Path(args.left).read_text(encoding="utf-8"))
    right = json.loads(Path(args.right).read_text(encoding="utf-8"))
    verify_receipt_integrity(left)
    verify_receipt_integrity(right)
    if canonical(left) != canonical(right):
        raise Refusal("REFUSED:REPLAY_DIVERGENCE")
    print(f"ALIVE:REPLAY_EQUIVALENT:{left['receipt']['digest']}")
    return 0


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest="command", required=True)
    verify = commands.add_parser("verify")
    verify.add_argument("--contract", required=True)
    verify.add_argument("--source-repo", required=True)
    verify.add_argument("--source-sha", required=True)
    verify.add_argument("--out", required=True)
    verify.set_defaults(run=verify_command)
    replay = commands.add_parser("replay")
    replay.add_argument("--left", required=True)
    replay.add_argument("--right", required=True)
    replay.set_defaults(run=replay_command)
    return root


def main() -> int:
    args = parser().parse_args()
    try:
        return args.run(args)
    except (OSError, json.JSONDecodeError, Refusal) as error:
        print(str(error))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
