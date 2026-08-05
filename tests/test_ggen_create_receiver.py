from __future__ import annotations

import base64
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).parents[1]
SPEC = importlib.util.spec_from_file_location(
    "verify_ggen_create_bundle",
    ROOT / "scripts" / "verify_ggen_create_bundle.py",
)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class GgenCreateReceiverTests(unittest.TestCase):
    def materialize(self, root: Path) -> tuple[Path, Path]:
        fixture = json.loads(
            (ROOT / "tests/fixtures/ggen_create_fortune5.json").read_text(
                encoding="utf-8"
            )
        )
        subject = root / "subject"
        bundle = subject / "foundry/generated/ggen-create"
        for relative, encoded in fixture["subject"].items():
            path = subject / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(base64.b64decode(encoded))
        for relative, encoded in fixture["bundle"].items():
            path = bundle / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(base64.b64decode(encoded))
        return subject, bundle

    def verify(self, subject: Path, bundle: Path) -> dict[str, object]:
        return MODULE.verify(
            bundle,
            authority_path=ROOT / "authority/ggen-create-receiving-contract.json",
            subject_root=subject,
        )

    def test_fixture_is_alive(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            subject, bundle = self.materialize(Path(raw))
            report = self.verify(subject, bundle)
            self.assertTrue(report["valid"])
            self.assertEqual(report["state"], "ALIVE")
            self.assertTrue(all(report["checks"].values()))

    def test_subject_drift_is_build_broken(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            subject, bundle = self.materialize(Path(raw))
            (subject / "src/order_router.py").write_text(
                "raise RuntimeError('drift')\n",
                encoding="utf-8",
            )
            report = self.verify(subject, bundle)
            self.assertFalse(report["valid"])
            self.assertEqual(report["state"], "BUILD_BROKEN")
            self.assertIn(
                {"path": "src/order_router.py", "reason": "digest"},
                report["drift"],
            )

    def test_unadmitted_subject_file_is_build_broken(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            subject, bundle = self.materialize(Path(raw))
            (subject / "src/ambient.py").write_text("pass\n", encoding="utf-8")
            report = self.verify(subject, bundle)
            self.assertFalse(report["valid"])
            self.assertIn(
                {"path": "src/ambient.py", "reason": "unadmitted"},
                report["drift"],
            )

    def test_output_tamper_is_build_broken(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            subject, bundle = self.materialize(Path(raw))
            (bundle / "ontology.ttl").write_text("tampered\n", encoding="utf-8")
            report = self.verify(subject, bundle)
            self.assertFalse(report["valid"])
            self.assertFalse(report["checks"]["output_digests"])

    def test_self_certification_is_refused_even_with_valid_receipt_digest(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            subject, bundle = self.materialize(Path(raw))
            receipt_path = bundle / "receipt.json"
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            receipt["claims"]["behavioral_equivalence"] = "ALIVE"
            payload = {
                key: value
                for key, value in receipt.items()
                if key != "receipt_digest"
            }
            receipt["receipt_digest"] = MODULE.digest_json(payload)
            receipt_path.write_text(
                json.dumps(receipt, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            report = self.verify(subject, bundle)
            self.assertFalse(report["valid"])
            self.assertTrue(report["checks"]["receipt_digest"])
            self.assertFalse(report["checks"]["self_certification_refused"])


if __name__ == "__main__":
    unittest.main()
