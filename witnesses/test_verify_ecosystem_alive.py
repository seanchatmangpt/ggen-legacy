#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import tempfile
from pathlib import Path

MODULE_PATH = Path(__file__).parents[1] / "verifiers" / "verify_ecosystem_alive.py"
spec = importlib.util.spec_from_file_location("alive_verifier", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(module)


def write(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def main() -> int:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        manifest = {
            "repositories": [
                {"repository": "seanchatmangpt/a", "canonical_reconstruction_sha": "a" * 40, "product_reconstitution": True},
                {"repository": "seanchatmangpt/transport", "canonical_reconstruction_sha": "b" * 40, "product_reconstitution": False},
            ]
        }
        write(root / "manifest.json", manifest)
        write(root / "state.json", {"workstreams": {letter: {"status": "ADMITTED"} for letter in "ABCDEFGHIJK"}})
        for kind in module.REQUIRED_KINDS:
            value = {
                "schema": "ggen-legacy.test-receipt/v1",
                "receipt_kind": kind,
                "repository": "seanchatmangpt/a",
                "canonical_sha": "a" * 40,
                "standing": "ALIVE",
                "promotion_granted": False,
            }
            value["receipt_digest"] = "sha256:" + module.sha256(value)
            write(root / "receipts" / f"{kind}.json", value)
        report = module.verify(root / "manifest.json", root / "receipts", root / "state.json")
        assert report["promotion_granted"] is True, report
        assert report["standing"] == "ALIVE"

        broken = json.loads((root / "receipts" / "validation.json").read_text())
        broken["standing"] = "BUILD_BROKEN"
        write(root / "receipts" / "validation.json", broken)
        report = module.verify(root / "manifest.json", root / "receipts", root / "state.json")
        assert report["promotion_granted"] is False
        assert any("validation standing=BUILD_BROKEN" in error for error in report["errors"])
        print(json.dumps({"schema": "ggen-legacy.ecosystem-alive.verifier-test/v1", "positive": "ALIVE", "negative": "REFUSED"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
