#!/usr/bin/env python3
"""Prove lawful inter-phase supersession and unexplained-drift refusal."""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "verifiers"))

import normalize_foundry_receipts as base  # noqa: E402
import normalize_foundry_receipts_interphase as interphase  # noqa: E402,F401


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(base.canonical_json(value))


def receipt(subject: str, key: str, digest: str) -> dict:
    outputs = {key: digest}
    subject_digest = base.digest_named_outputs(outputs)
    return {
        "schema_version": base.RECEIPT_SCHEMA,
        "receipt_type": "WORKSTREAM_ADMISSION",
        "subject": subject,
        "subject_digest": subject_digest,
        "source_head": "1" * 40,
        "corpus_head": "2" * 40,
        "input_digests": {},
        "output_digests": outputs,
        "run_id": subject_digest[:20],
    }


def setup_root(root: Path, include_new_claim: bool) -> tuple[Path, str, str]:
    output = root / "foundry/catalogs/mutable.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(b"old\n")
    key = "corpus:foundry/catalogs/mutable.json"
    old_digest = base.digest_file(output)
    old_receipt = root / "foundry/receipts/workstream-A.json"
    write_json(old_receipt, receipt("A", key, old_digest))
    ownership = {
        "schema_version": base.OWNERSHIP_SCHEMA,
        "policy": "exact-current-digest-single-owner",
        "historical_receipts_immutable": True,
        "active_receipts_replay_current_outputs_only": True,
        "outputs": {
            key: {
                "active_receipt": "foundry/receipts/workstream-A.json",
                "active_digest": old_digest,
                "observed_digest": old_digest,
                "superseded": [],
            }
        },
        "archives": {},
        "changes": [],
    }
    ownership_path = root / "foundry/receipt-ownership.json"
    write_json(ownership_path, ownership)

    output.write_bytes(b"new\n")
    new_digest = base.digest_file(output)
    if include_new_claim:
        write_json(
            root / "foundry/receipts/workstream-B.json",
            receipt("B", key, new_digest),
        )
    return ownership_path, old_digest, new_digest


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="receipt-supersession-positive-") as directory:
        root = Path(directory)
        ownership_path, old_digest, new_digest = setup_root(root, include_new_claim=True)
        report = base.report(root, ownership_path, "apply")
        assert report["status"] == "NORMALIZED", report
        ownership = json.loads(ownership_path.read_text())
        key = "corpus:foundry/catalogs/mutable.json"
        record = ownership["outputs"][key]
        assert record["active_receipt"] == "foundry/receipts/workstream-B.json"
        assert record["active_digest"] == new_digest
        assert record["superseded"][0]["expected_digest"] == old_digest
        archive = root / record["superseded"][0]["archive"]
        assert archive.is_file()
        archived = json.loads(archive.read_text())
        assert archived["output_digests"][key] == old_digest
        active_a = json.loads((root / "foundry/receipts/workstream-A.json").read_text())
        assert key not in active_a["output_digests"]

    with tempfile.TemporaryDirectory(prefix="receipt-supersession-negative-") as directory:
        root = Path(directory)
        ownership_path, _old_digest, _new_digest = setup_root(root, include_new_claim=False)
        try:
            base.report(root, ownership_path, "audit")
        except base.Refusal as refusal:
            assert refusal.code == "RECEIPT_ACTIVE_OUTPUT_DRIFT", refusal.payload()
        else:
            raise AssertionError("unexplained single-claim drift was not refused")

    print(
        json.dumps(
            {
                "schema": "ggen.enterprise-architecture-foundry.interphase-supersession-test/1",
                "standing": "ALIVE",
                "lawful_exact_claimant_transfer": True,
                "historical_receipt_preserved": True,
                "unexplained_drift_refused": True,
                "direct_actuation": False,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
