#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "ci_step_receipt.py"


class ReceiptTest(unittest.TestCase):
    def command(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_successful_execution_reaches_alive(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            report = Path(directory) / "receipt.json"
            self.assertEqual(
                self.command(
                    "init", "--report", str(report), "--schema", "test/v1",
                    "--head", "abc", "--claim-ceiling", "TEST_ONLY",
                ).returncode,
                0,
            )
            self.assertEqual(
                self.command(
                    "run", "--report", str(report), "--id", "pass", "--",
                    sys.executable, "-c", "print('alive')",
                ).returncode,
                0,
            )
            self.assertEqual(
                self.command("finalize", "--report", str(report)).returncode,
                0,
            )
            payload = json.loads(report.read_text(encoding="utf-8"))
            self.assertEqual(payload["standing"], "ALIVE")
            self.assertEqual(payload["checks"][0]["exit_code"], 0)
            self.assertIn("alive", payload["checks"][0]["stdout_tail"])

    def test_failure_is_preserved_and_refuses_alive(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            report = Path(directory) / "receipt.json"
            self.command(
                "init", "--report", str(report), "--schema", "test/v1",
                "--head", "abc", "--claim-ceiling", "TEST_ONLY",
            )
            failed = self.command(
                "run", "--report", str(report), "--id", "fail", "--",
                sys.executable, "-c", "import sys; print('broken'); sys.exit(7)",
            )
            self.assertEqual(failed.returncode, 7)
            self.assertEqual(
                self.command("finalize", "--report", str(report)).returncode,
                1,
            )
            payload = json.loads(report.read_text(encoding="utf-8"))
            self.assertEqual(payload["standing"], "BUILD_BROKEN")
            self.assertEqual(payload["failures"][0]["exit_code"], 7)
            self.assertEqual(payload["checks"][0]["failure"], "CHECK_FAILED")

    def test_uninitialized_receipt_is_typed_refusal(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            report = Path(directory) / "missing.json"
            result = self.command(
                "run", "--report", str(report), "--id", "missing", "--", "true"
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("REFUSED:RECEIPT_NOT_INITIALIZED", result.stderr)


if __name__ == "__main__":
    unittest.main()
