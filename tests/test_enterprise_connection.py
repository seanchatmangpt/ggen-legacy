from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "export_enterprise_connection.py"
SPEC = importlib.util.spec_from_file_location("export_enterprise_connection", SCRIPT)
assert SPEC and SPEC.loader
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


class EnterpriseConnectionTest(unittest.TestCase):
    def test_real_foundry_state_exports_deterministically_without_do_authority(self) -> None:
        state = json.loads((ROOT / "foundry/workstreams/state.json").read_text(encoding="utf-8"))
        expected_admitted = sorted(
            name
            for name, item in state["workstreams"].items()
            if item.get("status") == "ADMITTED"
        )
        with tempfile.TemporaryDirectory() as tmp:
            a = Path(tmp) / "a.json"
            b = Path(tmp) / "b.json"
            revision = "a" * 40
            first = module.export_connection(ROOT, revision, a)
            second = module.export_connection(ROOT, revision, b)
            self.assertEqual(a.read_bytes(), b.read_bytes())
            self.assertEqual(first, second)
            self.assertEqual(first["stage"], "RECONSTITUTE")
            self.assertFalse(first["authority"]["do_authority"])
            self.assertEqual(first["standing"]["state"], "PARTIAL_ALIVE")
            self.assertEqual(
                first["labels"]["admitted_workstreams"],
                ",".join(expected_admitted),
            )
            self.assertEqual(
                first["labels"]["committed_admission_reports_verified"],
                ",".join(expected_admitted),
            )
            report_evidence = [
                e for e in first["evidence"]
                if e["kind"] == "foundry-workstream-admission-report"
            ]
            self.assertEqual(
                sorted(e["identity"].split(":", 1)[0] for e in report_evidence),
                expected_admitted,
            )
            self.assertEqual(first["labels"]["local_receipts_present"], "")
            self.assertTrue(first["architecture"]["capabilities"])
            self.assertIn(
                "ZERO_UNRECEIPTED_ACTUATION",
                first["architecture"]["constraints"],
            )
            self.assertIsNone(first["parent"])

    def test_invalid_revision_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(module.Refusal):
                module.export_connection(ROOT, "main", Path(tmp) / "out.json")


if __name__ == "__main__":
    unittest.main()
