from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("authority_vacuum.py")
spec = importlib.util.spec_from_file_location("authority_vacuum", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
assert spec.loader is not None
spec.loader.exec_module(module)

EQUIVALENCE_PATH = Path(__file__).with_name("equivalence_runner.py")
equivalence_spec = importlib.util.spec_from_file_location("equivalence_runner_ostar_test", EQUIVALENCE_PATH)
equivalence = importlib.util.module_from_spec(equivalence_spec)
sys.modules[equivalence_spec.name] = equivalence
assert equivalence_spec.loader is not None
equivalence_spec.loader.exec_module(equivalence)


def run(*argv: str, cwd: Path) -> str:
    result = subprocess.run(argv, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    return result.stdout.strip()


class AuthorityVacuumTests(unittest.TestCase):
    def repository(self, root: Path) -> tuple[Path, str, dict[str, str]]:
        repo = root / "subject"
        repo.mkdir()
        (repo / "policy.txt").write_text("todo_allowed=false\n", encoding="utf-8")
        (repo / "runtime.txt").write_text("todo_allowed=true\n", encoding="utf-8")
        run("git", "init", "-q", cwd=repo)
        run("git", "config", "user.email", "reconstitution@example.invalid", cwd=repo)
        run("git", "config", "user.name", "Reconstitution Test", cwd=repo)
        run("git", "add", ".", cwd=repo)
        run("git", "commit", "-qm", "exact subject", cwd=repo)
        sha = run("git", "rev-parse", "HEAD", cwd=repo)
        blobs = {path: run("git", "rev-parse", f"HEAD:{path}", cwd=repo) for path in ("policy.txt", "runtime.txt")}
        return repo, sha, blobs

    def study(self, sha: str, blobs: dict[str, str], capability_count: int = 1) -> dict:
        candidates = [{"id": f"cap-{index}", "disposition": "UNKNOWN"} for index in range(capability_count)]
        return {
            "schema": module.STUDY_SCHEMA,
            "study_id": "TEST-AUTHORITY-VACUUM",
            "initial_authority_state": "NO_AUTHORITY",
            "direct_actuation": False,
            "semantic_scope": {"mode": "bounded-observable-surfaces", "universal_equivalence_claimed": False},
            "controlled_predicates": [{"predicate": "source.todo_allowed", "cardinality": "one"}],
            "subjects": [
                {
                    "id": "subject-a",
                    "repo": "example/subject",
                    "exact_sha": sha,
                    "transport": "git-checkout",
                    "authority": False,
                    "artifacts": [
                        {"id": "policy", "path": "policy.txt", "git_blob_sha1": blobs["policy.txt"]},
                        {"id": "runtime", "path": "runtime.txt", "git_blob_sha1": blobs["runtime.txt"]},
                    ],
                }
            ],
            "observations": [
                {"id": "policy-law", "subject": "subject-a", "predicate": "source.todo_allowed", "value": False, "evidence": "policy", "claim_ceiling": "OBSERVED_DECLARATION"},
                {"id": "runtime-counterexample", "subject": "subject-a", "predicate": "source.todo_allowed", "value": True, "evidence": "runtime", "claim_ceiling": "OBSERVED_SOURCE"},
            ],
            "candidate_capabilities": candidates,
        }

    def test_exact_observation_preserves_conflict_and_no_authority(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo, sha, blobs = self.repository(root)
            report = module.observe(self.study(sha, blobs), {"subject-a": repo})
            self.assertEqual(report["core"]["authority_state"], "NO_AUTHORITY")
            self.assertEqual(report["core"]["standing"], "ALIVE")
            self.assertEqual(report["core"]["conflicts"][0]["resolution"], "UNRESOLVED")
            self.assertFalse(report["receipt"]["authority"])

    def test_identical_observation_replays_byte_for_byte(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo, sha, blobs = self.repository(root)
            study = self.study(sha, blobs)
            first = module.observe(study, {"subject-a": repo})
            second = module.observe(study, {"subject-a": repo})
            self.assertEqual(module.replay(first, second)["status"], "REPLAY_MATCH")
            self.assertEqual(module.canonical_bytes(first), module.canonical_bytes(second))

    def test_observer_cannot_select_a_canonical_subject(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _, sha, blobs = self.repository(root)
            study = self.study(sha, blobs)
            study["canonical_subject"] = "subject-a"
            with self.assertRaises(module.AuthorityVacuumError) as caught:
                module.observe(study)
            self.assertEqual(caught.exception.code, "CANONICAL_SUBJECT_SELECTION_REFUSED")

    def test_unbounded_semantic_equivalence_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo, sha, blobs = self.repository(root)
            report = module.observe(self.study(sha, blobs), {"subject-a": repo})
            contract = self.contract(report, ["PRESERVED"])
            contract["semantic_scope"]["universal_equivalence_claimed"] = True
            with self.assertRaises(module.AuthorityVacuumError) as caught:
                module.admit(report, contract)
            self.assertEqual(caught.exception.code, "RICE_SCOPE_UNBOUNDED")

    def test_observer_refuses_direct_actuation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _, sha, blobs = self.repository(root)
            study = self.study(sha, blobs)
            study["direct_actuation"] = True
            with self.assertRaises(module.AuthorityVacuumError) as caught:
                module.observe(study)
            self.assertEqual(caught.exception.code, "OBSERVATION_ACTUATION_REFUSED")

    def contract(self, report: dict, dispositions: list[str]) -> dict:
        capabilities = []
        for index, disposition in enumerate(dispositions):
            capabilities.append(
                {
                    "id": f"cap-{index}",
                    "disposition": disposition,
                    "evidence_ids": ["policy-law", "runtime-counterexample"],
                    "observable_surfaces": ["exit_code", "diagnostics"],
                }
            )
        return {
            "schema": module.CONTRACT_SCHEMA,
            "study_id": report["core"]["study_id"],
            "observation_receipt_digest": report["receipt"]["artifact_digest"],
            "authority": {"id": "test-o-star", "digest": "a" * 64},
            "semantic_scope": {"mode": "bounded-observable-surfaces", "universal_equivalence_claimed": False},
            "capabilities": capabilities,
            "required_dispositions": sorted(set(dispositions)),
            "require_refusal": True,
        }

    def test_complete_five_disposition_contract_is_admitted_only_as_candidate(self) -> None:
        dispositions = ["PRESERVED", "SUBSUMED", "REPLACED", "ARCHIVED", "REFUSED"]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo, sha, blobs = self.repository(root)
            report = module.observe(self.study(sha, blobs, len(dispositions)), {"subject-a": repo})
            admission = module.admit(report, self.contract(report, dispositions))
            self.assertEqual(admission["core"]["authority_state"], "ADMITTED_CANDIDATE")
            self.assertEqual(admission["core"]["claim_ceiling"], "SCHEMA_VALIDATED")
            self.assertEqual(admission["core"]["standing"], "PARTIAL_ALIVE")
            self.assertFalse(admission["core"]["actuation_authority"])

    def test_all_non_refused_scope_is_rejected_as_scoping_failure(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo, sha, blobs = self.repository(root)
            report = module.observe(self.study(sha, blobs), {"subject-a": repo})
            with self.assertRaises(module.AuthorityVacuumError) as caught:
                module.admit(report, self.contract(report, ["PRESERVED"]))
            self.assertEqual(caught.exception.code, "SCOPING_FAILURE_NO_REFUSAL")

    def test_receipt_tampering_is_detected_before_replay(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo, sha, blobs = self.repository(root)
            report = module.observe(self.study(sha, blobs), {"subject-a": repo})
            tampered = json.loads(json.dumps(report))
            tampered["core"]["blocked"].append("REFUSED:TAMPERED")
            with self.assertRaises(module.AuthorityVacuumError) as caught:
                module.replay(report, tampered)
            self.assertEqual(caught.exception.code, "OBSERVATION_RECEIPT_INVALID")

    def test_receipt_parent_tampering_is_detected_before_admission(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo, sha, blobs = self.repository(root)
            report = module.observe(self.study(sha, blobs), {"subject-a": repo})
            report["receipt"]["parent_digests"] = ["0" * 64]
            with self.assertRaises(module.AuthorityVacuumError) as caught:
                module.admit(report, self.contract(report, ["REFUSED"]))
            self.assertEqual(caught.exception.code, "OBSERVATION_RECEIPT_INVALID")

    def test_equivalence_runner_refuses_unbounded_claim_metadata(self) -> None:
        manifest = {
            "semantic_scope": {
                "mode": "arbitrary-program-semantics",
                "universal_equivalence_claimed": True,
            },
            "cases": [
                {
                    "case_id": "bounded-fixture",
                    "expected_disposition": "PRESERVED",
                    "observable_surfaces": ["exit_code"],
                }
            ],
        }
        claim = equivalence.describe_claim(manifest, require_bounded_scope=True)
        self.assertEqual(claim["standing"], "REFUSED")
        self.assertEqual(claim["claim_ceiling"], "REFUSED:RICE_SCOPE_UNBOUNDED")

    def test_refused_equivalence_scope_never_executes_adapters(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            marker = root / "must-not-exist"
            manifest = {
                "semantic_scope": {
                    "mode": "arbitrary-program-semantics",
                    "universal_equivalence_claimed": True,
                },
                "cases": [
                    {
                        "case_id": "refused-before-execution",
                        "legacy_adapter": f"touch {marker}",
                        "current_adapter": f"touch {marker}",
                        "expected_disposition": "PRESERVED",
                        "observable_surfaces": ["exit_code"],
                    }
                ],
            }
            report = equivalence.run_manifest(manifest, root, require_bounded_scope=True)
            self.assertEqual(report["claim"]["standing"], "REFUSED")
            self.assertEqual(report["results"], [])
            self.assertFalse(marker.exists())

    def test_equivalence_semantic_receipt_replays_without_timestamps_or_durations(self) -> None:
        manifest = {
            "semantic_scope": {
                "mode": "bounded-observable-surfaces",
                "universal_equivalence_claimed": False,
            },
            "cases": [
                {
                    "case_id": "real-process-boundary",
                    "legacy_adapter": "printf same",
                    "current_adapter": "printf same",
                    "success_inputs": [""],
                    "failure_inputs": [],
                    "normalization_policy": "none",
                    "expected_disposition": "PRESERVED",
                    "observable_surfaces": ["exit_code", "stdout"],
                    "timeout_seconds": 1,
                    "recovery_action": "none",
                }
            ],
        }
        with tempfile.TemporaryDirectory() as first_dir, tempfile.TemporaryDirectory() as second_dir:
            first = equivalence.run_manifest(manifest, Path(first_dir), require_bounded_scope=True)
            second = equivalence.run_manifest(manifest, Path(second_dir), require_bounded_scope=True)
        self.assertEqual(first["claim"]["claim_ceiling"], "BOUNDED_OBSERVABLE_CONTRACT")
        self.assertEqual(
            first["semantic_receipt"]["artifact_digest"],
            second["semantic_receipt"]["artifact_digest"],
        )


if __name__ == "__main__":
    unittest.main()
