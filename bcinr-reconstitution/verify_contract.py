#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

EXPECTED_SCHEMA = "bcinr.evidence.contract/1"
EXPECTED_PRODUCER = "seanchatmangpt/ggen"
EXPECTED_RECEIVER = "seanchatmangpt/ggen-legacy"
EXPECTED_CONSUMER = "seanchatmangpt/bcinr"

REQUIRED_CLAIMS = {
    "BOUNDED_WORK",
    "TARGET_BRANCHLESS",
    "SEMANTIC_EQUIVALENCE",
    "PROOF",
    "RUNTIME_RECEIPT",
    "AUTHORITY_FENCE",
    "SCOPED_STANDING",
}

REQUIRED_RULES = {
    "INSPECTION_NOT_EXECUTION",
    "CITATION_NOT_PROOF_RECEIPT",
    "BRANCHLESS_IS_TARGET_INDEXED",
    "BOUNDED_NOT_BIG_O",
    "DOC_HIDDEN_NOT_AUTHORITY_FENCE",
    "NO_AMBIENT_DO",
    "EXACT_SUBJECT_STANDING",
}

REQUIRED_PROOF_FIELDS = {
    "repository",
    "commit",
    "module",
    "declaration",
    "source_digest",
    "proof_artifact_digest",
    "toolchain",
    "dependency_lock_digest",
    "verification_command",
    "exit_code",
}

REQUIRED_EXECUTION_FIELDS = {
    "subject",
    "observation",
    "manufacture",
    "authority",
    "consequence",
    "execution",
    "verifier",
    "replay",
    "standing",
    "binding_digest",
}


def refuse(code: str, detail: str) -> None:
    raise SystemExit(f"REFUSED:{code}: {detail}")


def codes(rows: object, field: str) -> set[str]:
    if not isinstance(rows, list):
        refuse("SCHEMA", f"expected list for {field}")
    result: set[str] = set()
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("code"), str):
            refuse("SCHEMA", f"malformed {field} row")
        result.add(row["code"])
    return result


def receipt_fields(rows: object, shape: str) -> set[str]:
    if not isinstance(rows, list):
        refuse("SCHEMA", "receipt_fields must be a list")
    result: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            refuse("SCHEMA", "malformed receipt_fields row")
        if row.get("shape") == shape:
            field = row.get("field")
            if not isinstance(field, str):
                refuse("SCHEMA", f"malformed field for {shape}")
            result.add(field)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", required=True, type=Path)
    args = parser.parse_args()

    raw = args.contract.read_bytes()
    try:
        contract = json.loads(raw)
    except json.JSONDecodeError as exc:
        refuse("JSON", str(exc))

    if contract.get("schema") != EXPECTED_SCHEMA:
        refuse("SCHEMA_ID", repr(contract.get("schema")))
    if contract.get("producer_repository") != EXPECTED_PRODUCER:
        refuse("PRODUCER_IDENTITY", repr(contract.get("producer_repository")))
    if contract.get("receiver_repository") != EXPECTED_RECEIVER:
        refuse("RECEIVER_IDENTITY", repr(contract.get("receiver_repository")))
    if contract.get("consumer_repository") != EXPECTED_CONSUMER:
        refuse("CONSUMER_IDENTITY", repr(contract.get("consumer_repository")))

    missing_claims = REQUIRED_CLAIMS - codes(contract.get("claims"), "claims")
    if missing_claims:
        refuse("CLAIM_CLOSURE", ",".join(sorted(missing_claims)))

    missing_rules = REQUIRED_RULES - codes(contract.get("rules"), "rules")
    if missing_rules:
        refuse("RULE_CLOSURE", ",".join(sorted(missing_rules)))

    evidence = contract.get("evidence")
    if not isinstance(evidence, list):
        refuse("SCHEMA", "evidence must be a list")
    ceilings = {
        row.get("code"): row.get("max_standing")
        for row in evidence
        if isinstance(row, dict)
    }
    if ceilings.get("INSPECTION") == "ALIVE":
        refuse("OVERCLAIM_INSPECTION", "inspection may not crown execution")
    if ceilings.get("FORMAL_CITATION") == "ALIVE":
        refuse("OVERCLAIM_CITATION", "citation is not proof receipt")
    if ceilings.get("PROOF_RECEIPT") != "ALIVE":
        refuse("PROOF_RECEIPT_CEILING", repr(ceilings.get("PROOF_RECEIPT")))
    if ceilings.get("EXECUTION_RECEIPT") != "ALIVE":
        refuse("EXECUTION_RECEIPT_CEILING", repr(ceilings.get("EXECUTION_RECEIPT")))

    proof_fields = receipt_fields(contract.get("receipt_fields"), "PROOF_RECEIPT_V1")
    missing_proof = REQUIRED_PROOF_FIELDS - proof_fields
    if missing_proof:
        refuse("PROOF_RECEIPT_SHAPE", ",".join(sorted(missing_proof)))

    execution_fields = receipt_fields(contract.get("receipt_fields"), "EXECUTION_RECEIPT_V1")
    missing_execution = REQUIRED_EXECUTION_FIELDS - execution_fields
    if missing_execution:
        refuse("EXECUTION_RECEIPT_SHAPE", ",".join(sorted(missing_execution)))

    rule_rows = contract.get("rules")
    descriptions = "\n".join(
        str(row.get("description", ""))
        for row in rule_rows
        if isinstance(row, dict)
    ).lower()
    if "no ambient" not in descriptions and "ambient consequential" not in descriptions:
        refuse("AUTHORITY_CEILING", "missing explicit no-ambient-actuation rule")

    digest = hashlib.sha256(raw).hexdigest()
    print(json.dumps({
        "schema": EXPECTED_SCHEMA,
        "contract_sha256": digest,
        "standing": "PARTIAL_ALIVE",
        "verified": "contract shape and anti-overclaiming laws only",
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
