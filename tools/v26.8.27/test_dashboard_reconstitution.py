#!/usr/bin/env python3
from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("dashboard_reconstitution.py")
spec = importlib.util.spec_from_file_location("dashboard_reconstitution", MODULE_PATH)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def contract() -> dict:
    standing = [
        {"code": code, "rank": rank, "label": code, "cssToken": f"standing-{code.lower().replace('_', '-')}", "allowsDo": False}
        for rank, code in enumerate(["UNKNOWN", "UNSUPPORTED", "BLOCKED", "BUILD_BROKEN", "PARTIAL_ALIVE", "ALIVE", "REFUSED"])
    ]
    stages = [
        {"code": code, "order": order, "label": code, "allowsDo": code == "BRCE"}
        for order, code in enumerate(["OBSERVE", "SELECT", "CONSTRUCT", "PREFLIGHT", "BRCE", "RECEIPT", "REPLAY"])
    ]
    intents = [
        {"code": "INSPECT", "label": "Inspect", "allowsDo": False},
        {"code": "QUERY", "label": "Query", "allowsDo": False},
        {"code": "CONSTRUCT_INTENT", "label": "Construct", "allowsDo": False},
        {"code": "ACTUATE_VIA_BRCE", "label": "BRCE", "allowsDo": True},
        {"code": "REPLAY_RECEIPT", "label": "Replay", "allowsDo": False},
    ]
    ids = ["overview", "resources", "evidence", "authority", "receipts", "replay", "topology"]
    projections = [{"id": value, "label": value, "description": value, "route": "/" if value == "overview" else f"/{value}", "plane": value.upper(), "icon": value} for value in ids]
    return {"schema": module.SCHEMA, "contractVersion": "26.8.27", "brceRequired": True, "standing": standing, "authorityStages": stages, "intentKinds": intents, "projections": projections}


class DashboardReconstitutionTest(unittest.TestCase):
    def test_deterministic_receipt(self):
        payload = contract()
        raw = json.dumps(payload, sort_keys=True).encode()
        left = module.manufacture_receipt(raw, payload, "seanchatmangpt/ggen-ui", "abc123")
        right = module.manufacture_receipt(raw, payload, "seanchatmangpt/ggen-ui", "abc123")
        self.assertEqual(left, right)
        module.verify_receipt_integrity(left)
        self.assertFalse(left["self_certifying"])
        self.assertFalse(left["ggen_certified"])
        self.assertFalse(left["do_authority"])

    def test_refuses_non_brce_do_stage(self):
        payload = contract()
        payload["authorityStages"].append({"code": "MODEL", "order": 99, "label": "Model", "allowsDo": True})
        with self.assertRaisesRegex(module.Refusal, "DO_AUTHORITY_TOPOLOGY"):
            module.validate_contract(payload)

    def test_refuses_duplicate_projection_route(self):
        payload = contract()
        payload["projections"][1]["route"] = "/"
        with self.assertRaisesRegex(module.Refusal, "PROJECTION_ROUTE:DUPLICATE"):
            module.validate_contract(payload)

    def test_refuses_tampered_receipt(self):
        payload = contract()
        raw = json.dumps(payload, sort_keys=True).encode()
        receipt = module.manufacture_receipt(raw, payload, "seanchatmangpt/ggen-ui", "abc123")
        tampered = copy.deepcopy(receipt)
        tampered["standing"] = "ALIVE"
        with self.assertRaisesRegex(module.Refusal, "RECEIPT_TAMPER"):
            module.verify_receipt_integrity(tampered)


if __name__ == "__main__":
    unittest.main()
