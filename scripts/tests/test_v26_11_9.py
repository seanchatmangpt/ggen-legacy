from __future__ import annotations

import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import verify_v26_11_9 as v  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]


def copy(tmp: str) -> Path:
    work = Path(tmp) / "r"
    for rel in ("authority/v26.11.9", "schemas", v.REL):
        shutil.copytree(ROOT / rel, work / rel)
    return work


class V261109Tests(unittest.TestCase):
    def test_repository_verifies_and_every_mutation_is_refused(self):
        self.assertEqual(v.verify(ROOT), [])
        self.assertEqual(v.selftest(ROOT), [])

    def test_admission_cannot_be_flipped_on(self):
        with tempfile.TemporaryDirectory() as tmp:
            work = copy(tmp)
            path = work / "authority/v26.11.9/sunset-admission.json"
            data = json.loads(path.read_text())
            data["admitted"] = True
            path.write_text(json.dumps(data))
            errors = v.verify(work)
            self.assertTrue(any("OVERCLAIM sunset-admission" in e for e in errors), errors)

    def test_unpinned_manifest_and_missing_standing_are_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            work = copy(tmp)
            man = work / v.REL / "manifests/cutover-scope.json"
            data = json.loads(man.read_text())
            data["source_shas"] = {}
            man.write_text(json.dumps(data))
            ticket = next((work / v.REL / "tickets").glob("T-002-*.md"))
            ticket.write_text("\n".join(l for l in ticket.read_text().splitlines()
                                        if not l.startswith("Standing:")))
            errors = " ".join(v.verify(work))
            self.assertIn("cutover-scope.json lacks exact source sha", errors)
            self.assertIn("Standing line missing", errors)


if __name__ == "__main__":
    unittest.main()
