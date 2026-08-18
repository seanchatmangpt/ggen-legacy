from __future__ import annotations
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("external_reconstitution.py")
spec = importlib.util.spec_from_file_location("external_reconstitution", MODULE_PATH)
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
assert spec.loader is not None
spec.loader.exec_module(mod)

def sh(*argv: str, cwd: Path) -> str:
    p = subprocess.run(argv, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    return p.stdout.strip()

class ExternalReconstitutionTests(unittest.TestCase):
    def fixture(self, root: Path) -> tuple[Path, Path, str]:
        repo = root / "legacy"; repo.mkdir(); (repo / "src").mkdir()
        (repo / "Cargo.toml").write_text('[package]\nname="sample"\nversion="0.1.0"\nedition="2024"\nlicense="MIT OR Apache-2.0"\n\n[features]\ndefault=[]\n', encoding="utf-8")
        (repo / "LICENSE-MIT").write_text("MIT\n", encoding="utf-8")
        (repo / "src" / "lib.rs").write_text("pub struct Prediction;\npub trait Module { fn run(&self); }\npub fn predict() {}\nimpl Module for Prediction {\n    fn run(&self) {}\n}\n", encoding="utf-8")
        sh("git", "init", "-q", cwd=repo); sh("git", "config", "user.email", "fde@example.invalid", cwd=repo); sh("git", "config", "user.name", "FDE Test", cwd=repo); sh("git", "add", ".", cwd=repo); sh("git", "commit", "-qm", "fixture", cwd=repo)
        sha = sh("git", "rev-parse", "HEAD", cwd=repo)
        contract = root / "contract.json"
        contract.write_text(json.dumps({"case_id":"TEST-001","source":{"repo":"example/sample","ref":sha,"sha":sha,"license_expression":"MIT OR Apache-2.0","expected_files":["Cargo.toml","LICENSE-MIT","src/lib.rs"]},"observation":{"include_prefixes":["src"],"exclude_prefixes":[]}}), encoding="utf-8")
        return repo, contract, sha

    def test_replay_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); repo,contract,_=self.fixture(root); out1,out2=root/"out1",root/"out2"
            r1=mod.manufacture(repo,contract,out1,cargo_bin="cargo",skip_cargo_metadata=True); r2=mod.manufacture(repo,contract,out2,cargo_bin="cargo",skip_cargo_metadata=True)
            self.assertEqual(r1["receipt_sha256"],r2["receipt_sha256"]); self.assertEqual(r1["artifacts_sha256"],r2["artifacts_sha256"])
            surface=json.loads((out1/"rust-surface-observations.json").read_text()); names={item.get("name") for item in surface["items"]}
            self.assertTrue({"Prediction","Module","predict"}.issubset(names)); self.assertTrue(any(item["evidence_kind"]=="lexical-trait-impl" for item in surface["items"])); self.assertEqual(r1["standing"],"PARTIAL_ALIVE")

    def test_wrong_exact_sha_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); repo,contract,_=self.fixture(root); data=json.loads(contract.read_text()); data["source"]["sha"]="0"*40; contract.write_text(json.dumps(data),encoding="utf-8")
            with self.assertRaises(mod.ReconstitutionError) as cm: mod.manufacture(repo,contract,root/"out",cargo_bin="cargo",skip_cargo_metadata=True)
            self.assertEqual(cm.exception.code,"SOURCE_IDENTITY_MISMATCH")

    def test_dirty_tracked_source_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); repo,contract,_=self.fixture(root); (repo/"src"/"lib.rs").write_text("pub struct Changed;\n",encoding="utf-8")
            with self.assertRaises(mod.ReconstitutionError) as cm: mod.manufacture(repo,contract,root/"out",cargo_bin="cargo",skip_cargo_metadata=True)
            self.assertEqual(cm.exception.code,"SOURCE_TREE_DIRTY")

if __name__ == "__main__": unittest.main()
