from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("verify_v26928", ROOT / "scripts/verify_v26_9_28.py")
assert SPEC and SPEC.loader
VERIFY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFY)


class V26928CrownTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lock = json.loads((ROOT / "authority/v26.9.28/ecosystem-lock.json").read_text())
        cls.contract = json.loads((ROOT / "authority/v26.9.28/reconstitution-contract.json").read_text())

    def test_admitted_lock(self):
        self.assertEqual([], VERIFY.verify_lock(self.lock))

    def test_admitted_contract(self):
        self.assertEqual([], VERIFY.verify_contract(self.contract))

    def test_read_plane_cannot_acquire_do(self):
        lock = copy.deepcopy(self.lock)
        item = next(x for x in lock["components"] if x["repo"] == "seanchatmangpt/ash_r2rml")
        item["authority"] = "CONSEQUENTIAL_DO"
        errors = VERIFY.verify_lock(lock)
        self.assertTrue(any("LOCK_AUTHORITY_MISMATCH" in e or "LOCK_DO_OWNER_SET_INVALID" in e for e in errors))

    def test_mutable_ref_is_not_exact_subject(self):
        lock = copy.deepcopy(self.lock)
        lock["components"][0]["sha"] = "main"
        self.assertTrue(any("LOCK_MUTABLE_OR_INVALID_SUBJECT" in e for e in VERIFY.verify_lock(lock)))

    def test_candidate_cannot_widen_authority(self):
        lock = copy.deepcopy(self.lock)
        lock["candidates"][0]["authority_widening"] = True
        self.assertIn(
            "LOCK_CANDIDATE_AUTHORITY_WIDENING:seanchatmangpt/ash_a2a",
            VERIFY.verify_lock(lock),
        )

    def test_release_pipeline_order_is_authority(self):
        contract = copy.deepcopy(self.contract)
        contract["pipeline"][7], contract["pipeline"][8] = contract["pipeline"][8], contract["pipeline"][7]
        self.assertIn("CONTRACT_PIPELINE_MISMATCH", VERIFY.verify_contract(contract))


if __name__ == "__main__":
    unittest.main()
