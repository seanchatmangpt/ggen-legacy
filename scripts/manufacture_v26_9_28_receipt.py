#!/usr/bin/env python3
"""Manufacture a deterministic, non-promoting v26.9.28 composition receipt."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

SOURCE_FILES = (
    "authority/v26.9.28/ecosystem-lock.json",
    "authority/v26.9.28/reconstitution-contract.json",
    "schemas/v26.9.28/ecosystem-lock.schema.json",
    "schemas/v26.9.28/reconstitution-contract.schema.json",
    "ontology/v26.9.28/reconstitution.ttl",
    "queries/v26.9.28/required-owners.rq",
    "queries/v26.9.28/no-authority-widening.rq",
    "planning/v26.9.28/domain.hddl",
    "planning/v26.9.28/fond-domain.pddl",
    "planning/v26.9.28/release.tla",
)


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    ).stdout.strip()


def source_set_digest(root: Path) -> str:
    digest = hashlib.sha256()
    for relative in SOURCE_FILES:
        path = relative.encode()
        data = (root / relative).read_bytes()
        digest.update(len(path).to_bytes(8, "big"))
        digest.update(path)
        digest.update(len(data).to_bytes(8, "big"))
        digest.update(data)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--expected-revision", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    revision = git(root, "rev-parse", "HEAD")
    tree = git(root, "rev-parse", "HEAD^{tree}")
    if revision != args.expected_revision:
        raise SystemExit(f"EXACT_REVISION_MISMATCH:{revision}:{args.expected_revision}")
    missing = [p for p in SOURCE_FILES if not (root / p).is_file()]
    if missing:
        raise SystemExit("REQUIRED_SOURCE_MISSING:" + ",".join(missing))

    lock_path = root / "authority/v26.9.28/ecosystem-lock.json"
    contract_path = root / "authority/v26.9.28/reconstitution-contract.json"
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    receipt = {
        "schema": "ggen.legacy.v26.9.28.manufacture-receipt.v1",
        "subject": {
            "repository": "seanchatmangpt/ggen-legacy",
            "release": "v26.9.28",
            "revision": revision,
            "tree": tree,
        },
        "producer_role": "composition_evidence_manufacturer",
        "standing": "PARTIAL_ALIVE",
        "final_admission_allowed": False,
        "actuation_performed": False,
        "source_set_sha256": source_set_digest(root),
        "lock_sha256": sha256(lock_path.read_bytes()),
        "contract_sha256": sha256(contract_path.read_bytes()),
        "component_subjects": [
            {"repo": item["repo"], "sha": item["sha"], "authority": item["authority"]}
            for item in lock["components"]
        ],
        "candidate_subjects": [
            {"repo": item["repo"], "sha": item["sha"], "state": item["state"]}
            for item in lock.get("candidates", [])
        ],
        "release_admitted": False,
        "sunset_admitted": False,
    }
    receipt["receipt_sha256"] = sha256(canonical(receipt))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"standing": receipt["standing"], "receipt_sha256": receipt["receipt_sha256"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
