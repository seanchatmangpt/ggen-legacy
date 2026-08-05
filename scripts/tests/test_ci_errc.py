from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[2] / "scripts" / "ci_errc.py"
SPEC = importlib.util.spec_from_file_location("ci_errc", MODULE_PATH)
assert SPEC and SPEC.loader
ci_errc = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ci_errc)


class CiErrcTests(unittest.TestCase):
    def test_lsp_source_routes_only_to_runtime(self) -> None:
        routed = ci_errc.classify_paths(["src/backend.rs"])
        self.assertEqual(routed["lsp_runtime"], ["src/backend.rs"])
        self.assertEqual(routed["assurance_deep"], [])

    def test_lsp_contract_is_excluded_from_deep_assurance(self) -> None:
        routed = ci_errc.classify_paths(["authority/lsp-contract.json"])
        self.assertEqual(routed["lsp_runtime"], ["authority/lsp-contract.json"])
        self.assertEqual(routed["assurance_deep"], [])

    def test_assurance_and_migration_have_independent_owners(self) -> None:
        routed = ci_errc.classify_paths(
            ["docs/src/SUMMARY.md", "migrations/ggen-v26.8.1/migration-manifest.json"]
        )
        self.assertEqual(routed["assurance_deep"], ["docs/src/SUMMARY.md"])
        self.assertEqual(
            routed["migration_deep"],
            ["migrations/ggen-v26.8.1/migration-manifest.json"],
        )

    def test_invalid_changed_json_is_typed_failure(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "authority" / "broken.json"
            target.parent.mkdir(parents=True)
            target.write_text("{", encoding="utf-8")
            checks = ci_errc.validate_structured_files(root, ["authority/broken.json"])
        self.assertEqual(len(checks), 1)
        self.assertFalse(checks[0]["passed"])
        self.assertEqual(checks[0]["failure"], "STRUCTURED_FILE_INVALID")

    def test_valid_toml_and_json_are_admitted(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "config.toml").write_text('name = "ggen"\n', encoding="utf-8")
            (root / "receipt.json").write_text(json.dumps({"standing": "ALIVE"}), encoding="utf-8")
            checks = ci_errc.validate_structured_files(
                root, ["config.toml", "receipt.json"]
            )
        self.assertEqual([check["passed"] for check in checks], [True, True])


if __name__ == "__main__":
    unittest.main()
