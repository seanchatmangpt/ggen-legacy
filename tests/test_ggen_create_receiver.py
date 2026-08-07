from __future__ import annotations

import base64
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import stat
import tarfile
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
        self.assertEqual(fixture["schema"], "ggen-legacy-ggen-create-fixture/2")
        archive = base64.b64decode(fixture["archive_base64"], validate=True)
        self.assertEqual(
            "sha256:" + hashlib.sha256(archive).hexdigest(),
            fixture["archive_sha256"],
        )
        with tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz") as source:
            for member in source.getmembers():
                path = Path(member.name)
                if path.is_absolute() or ".." in path.parts:
                    self.fail(f"unsafe fixture path: {member.name}")
                if member.isdir():
                    (root / path).mkdir(parents=True, exist_ok=True)
                    continue
                if not member.isfile():
                    self.fail(f"non-regular fixture member: {member.name}")
                extracted = source.extractfile(member)
                self.assertIsNotNone(extracted)
                target = root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(extracted.read())
                target.chmod(member.mode)
        self.assertEqual(
            fixture["producer"],
            {
                "commit": "a0a9133095e5114b693d62a85fc287fe76425c2e",
                "repository": "seanchatmangpt/ggen-create",
                "version": "0.4.0",
            },
        )
        subject = root / "subject"
        bundle = subject / "foundry/generated/ggen-create"
        return subject, bundle

    def verify(self, subject: Path, bundle: Path) -> dict[str, object]:
        return MODULE.verify(
            bundle,
            authority_path=ROOT / "authority/ggen-create-receiving-contract.json",
            subject_root=subject,
        )

    def reseal(self, bundle: Path) -> None:
        receipt_path = bundle / "receipt.json"
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        outputs, modes, problems = MODULE.bundle_outputs(bundle)
        self.assertEqual(problems, [])
        receipt["outputs"] = outputs
        receipt["output_modes"] = modes
        receipt["bundle_digest"] = MODULE.digest_json({
            "outputs": outputs,
            "output_modes": modes,
        })
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

    def test_fixture_is_alive(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            subject, bundle = self.materialize(Path(raw))
            report = self.verify(subject, bundle)
            self.assertTrue(report["valid"])
            self.assertEqual(report["state"], "ALIVE")
            self.assertTrue(all(report["checks"].values()))
            self.assertEqual(
                report["producer"]["commit"],
                "a0a9133095e5114b693d62a85fc287fe76425c2e",
            )

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

    @unittest.skipIf(os.name == "nt", "POSIX mode semantics")
    def test_subject_mode_drift_is_build_broken(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            subject, bundle = self.materialize(Path(raw))
            source = subject / "src/order_router.py"
            source.chmod(0o755)
            report = self.verify(subject, bundle)
            self.assertFalse(report["valid"])
            self.assertIn(
                {"path": "src/order_router.py", "reason": "mode"},
                report["drift"],
            )

    def test_output_tamper_is_build_broken(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            subject, bundle = self.materialize(Path(raw))
            (bundle / "ontology.ttl").write_text("tampered\n", encoding="utf-8")
            report = self.verify(subject, bundle)
            self.assertFalse(report["valid"])
            self.assertFalse(report["checks"]["output_digests"])
            self.assertFalse(report["checks"]["bundle_digest"])

    @unittest.skipIf(os.name == "nt", "POSIX mode semantics")
    def test_output_mode_tamper_is_build_broken(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            subject, bundle = self.materialize(Path(raw))
            (bundle / "verify_bundle.py").chmod(0o644)
            report = self.verify(subject, bundle)
            self.assertFalse(report["valid"])
            self.assertFalse(report["checks"]["output_modes"])
            self.assertFalse(report["checks"]["bundle_digest"])

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

    def test_forged_producer_identity_is_refused_after_complete_reseal(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            subject, bundle = self.materialize(Path(raw))
            forged = {
                "name": "ggen-create",
                "version": "0.4.0",
                "repository": "seanchatmangpt/ggen-create",
                "commit": "0" * 40,
            }
            for name in ("manifest.json", "receiving-contract.json"):
                path = bundle / name
                value = json.loads(path.read_text(encoding="utf-8"))
                value["producer_identity"] = forged
                path.write_text(
                    json.dumps(value, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8",
                )
            receipt_path = bundle / "receipt.json"
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            receipt["producer_identity"] = forged
            receipt_path.write_text(
                json.dumps(receipt, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            self.reseal(bundle)
            report = self.verify(subject, bundle)
            self.assertFalse(report["valid"])
            self.assertTrue(report["checks"]["receipt_digest"])
            self.assertTrue(report["checks"]["bundle_digest"])
            self.assertFalse(report["checks"]["producer_identity"])


if __name__ == "__main__":
    unittest.main()
