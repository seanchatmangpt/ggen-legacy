#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import tempfile
from pathlib import Path

MODULE_PATH = Path(__file__).parents[1] / "verifiers" / "normalize_foundry_receipts.py"
spec = importlib.util.spec_from_file_location("receipt_ownership", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(module)


def write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def receipt(subject: str, outputs: dict[str, str]) -> dict:
    digest = module.digest_named_outputs(outputs)
    return {
        "schema_version": module.RECEIPT_SCHEMA,
        "receipt_type": "TEST",
        "subject": subject,
        "subject_digest": digest,
        "source_head": "a" * 40,
        "corpus_head": "b" * 40,
        "input_digests": {},
        "output_digests": outputs,
        "run_id": digest[:20],
    }


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="foundry-receipt-ownership-") as directory:
        root = Path(directory)
        old_bytes = b'{"version":"initial"}\n'
        current_bytes = b'{"version":"workstream-c"}\n'
        stable_bytes = b'{"stable":true}\n'
        write(root / "foundry/catalogs/capabilities.json", current_bytes)
        write(root / "foundry/catalogs/stable.json", stable_bytes)

        initialization = receipt(
            "initialization",
            {
                "corpus:foundry/catalogs/capabilities.json": module.digest_bytes(old_bytes),
                "corpus:foundry/catalogs/stable.json": module.digest_bytes(stable_bytes),
            },
        )
        workstream = receipt(
            "C",
            {"corpus:foundry/catalogs/capabilities.json": module.digest_bytes(current_bytes)},
        )
        init_path = root / "foundry/receipts/initialization.json"
        c_path = root / "foundry/receipts/workstream-C.json"
        write(init_path, module.canonical_json(initialization))
        write(c_path, module.canonical_json(workstream))
        original_init = init_path.read_bytes()

        audit = module.report(root, root / "foundry/receipt-ownership.json", "audit")
        assert audit["status"] == "NORMALIZATION_REQUIRED", audit
        assert audit["duplicate_outputs_observed"] == 1

        applied = module.report(root, root / "foundry/receipt-ownership.json", "apply")
        assert applied["status"] == "NORMALIZED", applied
        active_init = json.loads(init_path.read_text())
        assert "corpus:foundry/catalogs/capabilities.json" not in active_init["output_digests"]
        assert active_init["output_digests"]["corpus:foundry/catalogs/stable.json"] == module.digest_bytes(stable_bytes)
        assert active_init["subject_digest"] == module.digest_named_outputs(active_init["output_digests"])

        ownership = json.loads((root / "foundry/receipt-ownership.json").read_text())
        record = ownership["outputs"]["corpus:foundry/catalogs/capabilities.json"]
        assert record["active_receipt"] == "foundry/receipts/workstream-C.json"
        archive = root / record["superseded"][0]["archive"]
        assert archive.read_bytes() == original_init

        second = module.report(root, root / "foundry/receipt-ownership.json", "audit")
        assert second["status"] == "ALIVE", second
        assert second["normalization_required"] is False

        # Two active receipts claiming the same current digest are ambiguous and refuse.
        duplicate = receipt(
            "duplicate",
            {"corpus:foundry/catalogs/capabilities.json": module.digest_bytes(current_bytes)},
        )
        write(root / "foundry/receipts/duplicate.json", module.canonical_json(duplicate))
        try:
            module.derive_plan(root, ownership)
        except module.Refusal as refusal:
            assert refusal.code == "RECEIPT_OWNER_AMBIGUOUS", refusal.code
        else:
            raise AssertionError("ambiguous current owner was admitted")

        print(json.dumps({
            "schema": "ggen.enterprise-architecture-foundry.receipt-ownership-test/1",
            "standing": "ALIVE",
            "historical_receipt_preserved": True,
            "active_receipt_filtered": True,
            "idempotent_replay": True,
            "ambiguous_owner_refused": True,
        }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
