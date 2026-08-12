#!/usr/bin/env python3
"""Independent GL-ERRC-003 replay and negative-control verifier."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_SELF_EXCLUSIONS = {
    "scripts/reconstitute_fortune5.py",
    "scripts/verify_fortune5_reconstitution.py",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tree(root: Path) -> dict[str, str]:
    return {p.relative_to(root).as_posix(): sha(p) for p in sorted(root.rglob("*")) if p.is_file()}


def run_engine(root: Path, out: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(root / "scripts/reconstitute_fortune5.py"),
            "--root", str(root),
            "--contract", str(root / "authority/fortune5-reconstitution.json"),
            "--output", str(out),
            "--strict",
        ],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
        timeout=30,
    )


def verify_receipt(out: Path) -> dict:
    receipt = json.loads((out / "receipt.json").read_text())
    for rel, expected in receipt["output_manifest"].items():
        actual = sha(out / rel)
        if actual != expected:
            raise RuntimeError(f"OUTPUT_DIGEST_MISMATCH:{rel}")
    if receipt["claim_ceiling"] != "FORTUNE5_SELF_RECONSTITUTION_ANALYSIS_ONLY":
        raise RuntimeError("CLAIM_CEILING_WIDENED")
    if receipt["standing"] != "PARTIAL_ALIVE" or receipt["external_production_standing"] != "UNKNOWN":
        raise RuntimeError("SELF_CERTIFICATION_DETECTED")
    required_sources = {
        "authority/fortune5-reconstitution.json",
        "scripts/reconstitute_fortune5.py",
        "scripts/verify_fortune5_reconstitution.py",
        "tickets/GL-ERRC-003.md",
        ".github/workflows/ci.yml",
    }
    if not required_sources.issubset(receipt["source_manifest"]):
        missing = sorted(required_sources - set(receipt["source_manifest"]))
        raise RuntimeError("RECEIPT_SOURCE_BINDING_MISSING:" + ",".join(missing))
    return receipt


def verify_self_evidence(contract: dict, matrix: dict) -> None:
    exclusions = set(contract.get("evidence_exclusions", []))
    if exclusions != REQUIRED_SELF_EXCLUSIONS:
        raise RuntimeError("SELF_EVIDENCE_EXCLUSION_DRIFT")
    invariant_exclusions = set(matrix.get("invariants", {}).get("evidence_exclusions", []))
    if invariant_exclusions != exclusions or not matrix.get("invariants", {}).get("reconstitution_source_excluded_from_evidence"):
        raise RuntimeError("SELF_EVIDENCE_INVARIANT_MISSING")
    for row in matrix["matrix"]:
        for paths in row["evidence"].values():
            leaked = exclusions.intersection(paths)
            if leaked:
                raise RuntimeError(f"SELF_EVIDENCE_LEAK:{row['id']}:{','.join(sorted(leaked))}")


def mutate_cardinality(src: Path, dst: Path) -> None:
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns(".git", "target", "__pycache__"))
    p = dst / "product/PRD.md"
    text = p.read_text()
    target_id = "PRD-FR-" + "014"
    start = text.index("### " + target_id)
    end = text.find("\n### PRD-FR-", start + 1)
    p.write_text(text[:start] + (text[end + 1:] if end >= 0 else ""))


def mutate_workflow(src: Path, dst: Path) -> None:
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns(".git", "target", "__pycache__"))
    (dst / ".github/workflows/rogue.yml").write_text("name: rogue\n")


def mutate_self_exclusion(src: Path, dst: Path) -> None:
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns(".git", "target", "__pycache__"))
    p = dst / "authority/fortune5-reconstitution.json"
    contract = json.loads(p.read_text())
    contract["evidence_exclusions"] = ["scripts/reconstitute_fortune5.py"]
    p.write_text(json.dumps(contract, sort_keys=True, indent=2) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    root = args.root.resolve()
    with tempfile.TemporaryDirectory(prefix="gl-errc-003-") as td_raw:
        td = Path(td_raw)
        first, second = td / "first", td / "second"
        run_first, run_second = run_engine(root, first), run_engine(root, second)
        if run_first.returncode or run_second.returncode:
            print(json.dumps({
                "standing": "BUILD_BROKEN",
                "first": {"exit": run_first.returncode, "stderr": run_first.stderr},
                "second": {"exit": run_second.returncode, "stderr": run_second.stderr},
            }, sort_keys=True))
            return 1
        if tree(first) != tree(second):
            print("REPLAY_DIVERGENCE", file=sys.stderr)
            return 1

        receipt = verify_receipt(first)
        matrix = json.loads((first / "matrix.json").read_text())
        queue = json.loads((first / "work-queue.json").read_text())
        contract = json.loads((root / "authority/fortune5-reconstitution.json").read_text())
        expected = contract["expected_cardinality"]
        observed = matrix["counts"]
        for key in ("product_requirements", "claims", "maturity_obligations", "workstreams"):
            if observed[key] != expected[key]:
                raise RuntimeError(f"CARDINALITY_MISMATCH:{key}")

        verify_self_evidence(contract, matrix)

        external = set(contract["external_claims"])
        rows = {row["id"]: row for row in matrix["matrix"]}
        for claim_id in external:
            row = rows[claim_id]
            if not row["external_gate"]:
                raise RuntimeError(f"EXTERNAL_GATE_LOST:{claim_id}")
            if row["computed_standing_ceiling"] != "UNKNOWN" or row["errc_operator"] != "RAISE":
                raise RuntimeError(f"EXTERNAL_GATE_WIDENED:{claim_id}")

        allowed = {"ELIMINATE", "REDUCE", "RAISE", "CREATE"}
        if any(item["operator"] not in allowed for item in queue["items"]):
            raise RuntimeError("INVALID_ERRC_OPERATOR")
        if any(item["auto_executable"] or item["actuation"] != "REFUSED:AMBIENT_ACTUATION" for item in queue["items"]):
            raise RuntimeError("AMBIENT_ACTUATION_ESCALATION")

        bad_cardinality = td / "bad-cardinality"
        mutate_cardinality(root, bad_cardinality)
        killed_cardinality = run_engine(bad_cardinality, td / "bad-cardinality-output")
        if killed_cardinality.returncode != 2 or "REFUSED:CARDINALITY_DRIFT:product_requirements" not in killed_cardinality.stderr:
            raise RuntimeError("CARDINALITY_MUTANT_SURVIVED")

        bad_workflow = td / "bad-workflow"
        mutate_workflow(root, bad_workflow)
        killed_workflow = run_engine(bad_workflow, td / "bad-workflow-output")
        if killed_workflow.returncode != 2 or "REFUSED:WORKFLOW_TOPOLOGY_DRIFT" not in killed_workflow.stderr:
            raise RuntimeError("WORKFLOW_MUTANT_SURVIVED")

        bad_self_evidence = td / "bad-self-evidence"
        mutate_self_exclusion(root, bad_self_evidence)
        leaked_output = td / "bad-self-evidence-output"
        leaked_run = run_engine(bad_self_evidence, leaked_output)
        if leaked_run.returncode != 0:
            raise RuntimeError("SELF_EVIDENCE_MUTANT_DID_NOT_REACH_VERIFIER")
        leaked_contract = json.loads((bad_self_evidence / "authority/fortune5-reconstitution.json").read_text())
        leaked_matrix = json.loads((leaked_output / "matrix.json").read_text())
        try:
            verify_self_evidence(leaked_contract, leaked_matrix)
        except RuntimeError:
            self_evidence_killed = True
        else:
            self_evidence_killed = False
        if not self_evidence_killed:
            raise RuntimeError("SELF_EVIDENCE_MUTANT_SURVIVED")

        report = {
            "schema": "ggen.legacy.errc.reconstitution.verifier/1",
            "ticket": "GL-ERRC-003",
            "subject_head": receipt["subject_head"],
            "objects": observed["objects"],
            "work_orders": observed["work_orders"],
            "replay": "REPLAY_MATCH",
            "negative_controls": {
                "cardinality_drift": "KILLED",
                "workflow_topology_drift": "KILLED",
                "self_evidence_exclusion_drift": "KILLED",
            },
            "claim_ceiling": "FORTUNE5_SELF_RECONSTITUTION_ANALYSIS_ONLY",
            "standing": "PARTIAL_ALIVE",
        }
        print(json.dumps(report, sort_keys=True))
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
