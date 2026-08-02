#!/usr/bin/env python3
"""Mutation-driven falsifiers for the Chatman ecosystem authority graph."""

from __future__ import annotations

import copy
import importlib.util
import json
import unittest
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "chatman_ecosystem_verifier",
    ROOT / "verifiers/verify_chatman_ecosystem.py",
)
assert SPEC and SPEC.loader
VERIFIER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = VERIFIER
SPEC.loader.exec_module(VERIFIER)


class ChatmanEcosystemFalsifiers(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = json.loads(
            (ROOT / "authority/chatman-ecosystem/ecosystem.json").read_text(encoding="utf-8")
        )
        cls.architecture = (
            ROOT / "authority/chatman-ecosystem/architecture.md"
        ).read_text(encoding="utf-8")

    def codes(self, value: dict) -> set[str]:
        return {
            finding.code
            for finding in VERIFIER.structural_findings(value, self.architecture)
        }

    def test_positive_authority_graph(self) -> None:
        self.assertEqual(set(), self.codes(copy.deepcopy(self.data)))

    def test_duplicate_capability_refused(self) -> None:
        value = copy.deepcopy(self.data)
        value["capabilities"].append(copy.deepcopy(value["capabilities"][0]))
        self.assertIn("DUPLICATE_CAPABILITY_ID", self.codes(value))

    def test_unknown_repository_realization_refused(self) -> None:
        value = copy.deepcopy(self.data)
        value["capabilities"][0]["repository_realizations"].append("unknown/missing")
        self.assertIn("UNKNOWN_REPOSITORY_REALIZATION", self.codes(value))

    def test_non_brce_actuation_refused(self) -> None:
        value = copy.deepcopy(self.data)
        next(item for item in value["capabilities"] if item["id"] == "ggen")[
            "can_actuate"
        ] = True
        self.assertIn("NON_BRCE_ACTUATION", self.codes(value))

    def test_direct_actuation_relationship_refused(self) -> None:
        value = copy.deepcopy(self.data)
        value["relationships"][0]["direct_actuation"] = True
        self.assertIn("DIRECT_ACTUATION_RELATIONSHIP", self.codes(value))

    def test_transport_product_authority_refused(self) -> None:
        value = copy.deepcopy(self.data)
        next(
            item
            for item in value["repositories"]
            if item["id"] == "seanchatmangpt/clnrm"
        )["product_authority"] = True
        self.assertIn("TRANSPORT_PROMOTED", self.codes(value))

    def test_alive_without_evidence_refused(self) -> None:
        value = copy.deepcopy(self.data)
        value["capabilities"][0]["standing"] = "ALIVE"
        value["capabilities"][0]["evidence_refs"] = []
        self.assertIn("ALIVE_WITHOUT_EVIDENCE", self.codes(value))

    def test_undocumented_capability_refused(self) -> None:
        value = copy.deepcopy(self.data)
        value["capabilities"][0]["id"] = "not-in-the-architecture-document"
        self.assertIn("UNDOCUMENTED_CAPABILITY", self.codes(value))

    def test_self_certification_refused(self) -> None:
        value = copy.deepcopy(self.data)
        relationship = next(
            item
            for item in value["relationships"]
            if item["relation"] == "computes-bounded-standing-for"
        )
        relationship["source"] = "ggen"
        self.assertIn("SELF_CERTIFICATION_PATH", self.codes(value))


if __name__ == "__main__":
    unittest.main(verbosity=2)
