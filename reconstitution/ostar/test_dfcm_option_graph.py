from __future__ import annotations

import copy
import importlib.util
import sys
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("dfcm_option_graph.py")
spec = importlib.util.spec_from_file_location("dfcm_option_graph", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
assert spec.loader is not None
spec.loader.exec_module(module)


def study() -> dict:
    return {
        "schema": "ggen.legacy.authority-vacuum.study.v1",
        "study_id": "OSTAR-EMPIRE-001",
        "initial_authority_state": "NO_AUTHORITY",
        "direct_actuation": False,
        "candidate_capabilities": [
            {"id": "ostar-cli-load", "disposition": "UNKNOWN"},
            {"id": "ostar-codemanufactory-manufacture", "disposition": "UNKNOWN"},
            {"id": "ostar-governance-pipeline", "disposition": "UNKNOWN"},
            {"id": "ostar-dteam-process-intelligence", "disposition": "UNKNOWN"},
            {"id": "ostar-ggen-projection-contract", "disposition": "UNKNOWN"},
            {"id": "ontostar-admission-manufacture", "disposition": "UNKNOWN"},
        ],
    }


class DfcmOptionGraphTests(unittest.TestCase):
    def test_six_capabilities_preserve_all_1800_syntactic_closures(self) -> None:
        graph = module.construct(study())
        self.assertEqual(graph["core"]["dfcm_phase"], "PRESERVE")
        self.assertEqual(graph["core"]["option_count"], 1800)
        self.assertEqual(graph["core"]["selection_state"], "UNSELECTED")
        self.assertFalse(graph["core"]["actuation_authority"])
        module.verify(graph)

    def test_every_option_exercises_all_five_dispositions(self) -> None:
        graph = module.construct(study())
        required = set(module.DISPOSITIONS)
        for option in graph["core"]["options"]:
            self.assertEqual({item["disposition"] for item in option["assignments"]}, required)
            self.assertFalse(option["selection_authority"])
            self.assertFalse(option["actuation_authority"])

    def test_construct_is_deterministic(self) -> None:
        left = module.construct(study())
        right = module.construct(study())
        self.assertEqual(module.canonical_bytes(left), module.canonical_bytes(right))
        self.assertEqual(module.replay(left, right)["status"], "REPLAY_MATCH")

    def test_reversible_constraint_prunes_without_selecting(self) -> None:
        graph = module.construct(study())
        constraints = {
            "schema": module.CONSTRAINT_SCHEMA,
            "selection_authority": False,
            "actuation_authority": False,
            "rules": [
                {"capability": "ostar-cli-load", "allowed_dispositions": ["REFUSED"]},
            ],
        }
        pruned = module.prune(graph, constraints)
        self.assertGreater(pruned["core"]["option_count"], 0)
        self.assertLess(pruned["core"]["option_count"], 1800)
        self.assertEqual(pruned["core"]["selection_state"], "UNSELECTED")
        for option in pruned["core"]["options"]:
            assignments = {item["capability"]: item["disposition"] for item in option["assignments"]}
            self.assertEqual(assignments["ostar-cli-load"], "REFUSED")
        module.verify(pruned)

    def test_direct_selection_is_refused(self) -> None:
        graph = module.construct(study())
        with self.assertRaises(module.DfcmError) as caught:
            module.select(graph, graph["core"]["options"][0]["option_id"])
        self.assertEqual(caught.exception.code, "DFCM_SELECTION_REQUIRES_ADMISSION")

    def test_premature_disposition_is_refused(self) -> None:
        value = study()
        value["candidate_capabilities"][0]["disposition"] = "PRESERVED"
        with self.assertRaises(module.DfcmError) as caught:
            module.construct(value)
        self.assertEqual(caught.exception.code, "DFCM_PREMATURE_DISPOSITION_REFUSED")

    def test_receipt_tampering_is_detected(self) -> None:
        graph = module.construct(study())
        tampered = copy.deepcopy(graph)
        tampered["core"]["options"].pop()
        with self.assertRaises(module.DfcmError) as caught:
            module.verify(tampered)
        self.assertEqual(caught.exception.code, "DFCM_RECEIPT_INVALID")

    def test_constraints_cannot_grant_selection_authority(self) -> None:
        graph = module.construct(study())
        constraints = {
            "schema": module.CONSTRAINT_SCHEMA,
            "selection_authority": True,
            "actuation_authority": False,
            "rules": [],
        }
        with self.assertRaises(module.DfcmError) as caught:
            module.prune(graph, constraints)
        self.assertEqual(caught.exception.code, "DFCM_SELECTION_AUTHORITY_REFUSED")


if __name__ == "__main__":
    unittest.main()
