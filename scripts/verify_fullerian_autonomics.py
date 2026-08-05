#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
AUTHORITY = ROOT / "authority" / "fullerian-autonomics.json"
SCHEMA = ROOT / "schemas" / "fullerian-autonomics.schema.json"
RUNTIME = ROOT / "scripts" / "run_fullerian_autonomics.py"
REFERENCE = ROOT / "tests" / "fixtures" / "autonomics" / "reference-program.json"
NEGATIVE = ROOT / "tests" / "fixtures" / "autonomics" / "negative-programs.json"
TICKET = ROOT / "projects" / "001" / "TICKET-012-fullerian-autonomics.md"
WORKFLOW = ROOT / ".github" / "workflows" / "verify-fullerian-autonomics.yml"
VERIFIER = Path(__file__).resolve()
SUBJECT_FILES = [
    AUTHORITY,
    SCHEMA,
    RUNTIME,
    VERIFIER,
    REFERENCE,
    NEGATIVE,
    TICKET,
    WORKFLOW,
]


def canonical(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise ValueError(f"expected object: {path}")
    return value


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tree_digest(paths: list[Path]) -> str:
    digest = hashlib.sha256()
    for path in sorted(paths, key=lambda item: str(item.relative_to(ROOT))):
        relative = str(path.relative_to(ROOT))
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def run_runtime(program: Path, out_dir: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(RUNTIME),
            "--authority",
            str(AUTHORITY),
            "--program",
            str(program),
            "--out-dir",
            str(out_dir),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def apply_patch(document: dict[str, Any], patch: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(document)
    for dotted_path, value in patch.items():
        parts = dotted_path.split(".")
        current: Any = result
        for part in parts[:-1]:
            current = current[int(part)] if isinstance(current, list) else current[part]
        last = parts[-1]
        if isinstance(current, list):
            current[int(last)] = value
        else:
            current[last] = value
    return result


def check(checks: list[dict[str, Any]], check_id: str, passed: bool, detail: Any) -> None:
    checks.append({"id": check_id, "passed": bool(passed), "detail": detail})


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output", default="evidence/fullerian-autonomics-verifier.json"
    )
    args = parser.parse_args()

    checks: list[dict[str, Any]] = []
    missing = [str(path.relative_to(ROOT)) for path in SUBJECT_FILES if not path.is_file()]
    check(checks, "subject-files-present", not missing, missing)
    if missing:
        report = {
            "schema": "ggen.legacy.fullerian.autonomics.verifier.v1",
            "checks": checks,
            "standing": "BUILD_BROKEN",
        }
        print(json.dumps(report, indent=2, sort_keys=True))
        return 2

    authority = read_json(AUTHORITY)
    schema = read_json(SCHEMA)
    reference = read_json(REFERENCE)
    negative = read_json(NEGATIVE)

    expected_canon = {
        "comprehensive-anticipatory-design-science",
        "synergy",
        "ephemeralization",
        "trimtab-leverage",
        "world-game-100-percent",
    }
    expected_extensions = {
        "observation-admission",
        "combinatorial-maximalism",
        "brce",
        "typed-non-success",
        "scoped-standing",
    }
    canon_ids = {item.get("id") for item in authority.get("canon", [])}
    extension_ids = {item.get("id") for item in authority.get("extensions", [])}
    check(checks, "fuller-canon-preserved", canon_ids == expected_canon, sorted(canon_ids))
    check(
        checks,
        "post-fuller-extensions-distinguished",
        extension_ids == expected_extensions,
        sorted(extension_ids),
    )

    phases = [item.get("id") for item in authority.get("autonomic_model", {}).get("phases", [])]
    check(checks, "mape-k-order", phases == ["MONITOR", "ANALYZE", "PLAN", "EXECUTE"], phases)
    check(
        checks,
        "brce-exclusive-path",
        authority.get("actuation", {}).get("exclusive_path") == "BRCE"
        and authority.get("actuation", {}).get("ambient_execution") is False
        and authority.get("actuation", {}).get("receipt_required") is True,
        authority.get("actuation"),
    )
    check(
        checks,
        "crown-authority-refused",
        authority.get("repository_crown_authority") is False,
        authority.get("repository_crown_authority"),
    )
    check(
        checks,
        "exact-base-bound",
        authority.get("admitted_base_sha") == reference.get("admitted_base_sha")
        == "8d6428f40c0d30d5983fb0ecdd16cab1c1328a23",
        {
            "authority": authority.get("admitted_base_sha"),
            "reference": reference.get("admitted_base_sha"),
        },
    )
    check(
        checks,
        "schema-boundaries-present",
        "$defs" in schema
        and all(name in schema["$defs"] for name in ("program", "candidate", "receipt", "refusalReceipt")),
        sorted(schema.get("$defs", {}).keys()),
    )

    with tempfile.TemporaryDirectory(prefix="ggen-fuller-a-") as a_raw, tempfile.TemporaryDirectory(
        prefix="ggen-fuller-b-"
    ) as b_raw, tempfile.TemporaryDirectory(prefix="ggen-fuller-neg-") as neg_raw:
        out_a = Path(a_raw)
        out_b = Path(b_raw)
        neg_root = Path(neg_raw)
        first = run_runtime(REFERENCE, out_a)
        second = run_runtime(REFERENCE, out_b)
        check(
            checks,
            "positive-execution",
            first.returncode == 0 and second.returncode == 0,
            {
                "first": first.returncode,
                "second": second.returncode,
                "first_stderr": first.stderr,
                "second_stderr": second.stderr,
            },
        )

        expected_paths = [
            "projection/selected-design.json",
            "receipt.json",
            "run-report.json",
        ]
        present = all((out_a / path).is_file() and (out_b / path).is_file() for path in expected_paths)
        check(checks, "brokered-artifacts-present", present, expected_paths)

        replay_match = present and all(
            (out_a / path).read_bytes() == (out_b / path).read_bytes()
            for path in expected_paths
        )
        check(checks, "byte-identical-replay", replay_match, expected_paths)

        receipt = read_json(out_a / "receipt.json") if present else {}
        projection = read_json(out_a / expected_paths[0]) if present else {}
        check(
            checks,
            "identity-bound-receipt",
            receipt.get("broker") == "BRCE"
            and receipt.get("exit_status") == 0
            and receipt.get("output_sha256") == sha256_file(out_a / expected_paths[0])
            and receipt.get("authority_sha256") == sha256_file(AUTHORITY)
            and receipt.get("program_sha256") == sha256_file(REFERENCE),
            receipt,
        )
        check(
            checks,
            "combinatorial-selection",
            receipt.get("selected_candidate") == "preserve-fence-brce-intent"
            and projection.get("plan", {}).get("lawful_reversible_options") == 12
            and projection.get("plan", {}).get("irreversible_commitments") == 1,
            projection.get("plan"),
        )
        refused_map = {
            item.get("id"): item.get("refusal")
            for item in projection.get("refused_candidates", [])
        }
        check(
            checks,
            "world-game-externality-refusal",
            refused_map.get("fast-unbounded-replacement")
            == "STAKEHOLDER_EXTERNALITY_REFUSED",
            refused_map,
        )

        reference_document = read_json(REFERENCE)
        negative_results: list[dict[str, Any]] = []
        no_unreceipted_effects = True
        for case in negative.get("cases", []):
            case_id = case["id"]
            case_dir = neg_root / case_id
            case_dir.mkdir(parents=True, exist_ok=True)
            case_program = apply_patch(reference_document, case["patch"])
            case_path = case_dir / "program.json"
            case_path.write_bytes(canonical(case_program) + b"\n")
            completed = run_runtime(case_path, case_dir / "out")
            refusal_path = case_dir / "out" / "refusal.json"
            refusal_receipt_path = case_dir / "out" / "refusal-receipt.json"
            refusal_doc = read_json(refusal_path) if refusal_path.is_file() else {}
            refusal_receipt = (
                read_json(refusal_receipt_path) if refusal_receipt_path.is_file() else {}
            )
            projection_path = case_dir / "out" / "projection" / "selected-design.json"
            receipt_path = case_dir / "out" / "receipt.json"
            refusal_receipted = (
                refusal_receipt.get("broker") == "BRCE"
                and refusal_receipt.get("effect") == "WRITE_REFUSAL_EVIDENCE"
                and refusal_receipt.get("exit_status") == 3
                and refusal_receipt.get("refusal") == case["expected_refusal"]
                and refusal_receipt.get("output_sha256") == sha256_file(refusal_path)
            )
            passed = (
                completed.returncode == 3
                and refusal_doc.get("refusal") == case["expected_refusal"]
                and refusal_receipted
                and not projection_path.exists()
                and not receipt_path.exists()
            )
            emitted_files = sorted(
                str(path.relative_to(case_dir / "out"))
                for path in (case_dir / "out").rglob("*")
                if path.is_file()
            )
            no_unreceipted_effects = no_unreceipted_effects and (
                emitted_files == ["refusal-receipt.json", "refusal.json"]
                and refusal_receipted
            )
            negative_results.append(
                {
                    "id": case_id,
                    "passed": passed,
                    "returncode": completed.returncode,
                    "expected": case["expected_refusal"],
                    "observed": refusal_doc.get("refusal"),
                    "refusal_receipted": refusal_receipted,
                    "emitted_files": emitted_files,
                }
            )
        check(
            checks,
            "typed-negative-controls",
            bool(negative_results) and all(item["passed"] for item in negative_results),
            negative_results,
        )
        check(
            checks,
            "zero-unreceipted-actuation",
            no_unreceipted_effects,
            negative_results,
        )

    passed = all(item["passed"] for item in checks)
    report = {
        "schema": "ggen.legacy.fullerian.autonomics.verifier.v1",
        "subject": {
            "repository": "seanchatmangpt/ggen-legacy",
            "admitted_base_sha": authority.get("admitted_base_sha"),
            "dependency_closed_sparse_tree_sha256": tree_digest(SUBJECT_FILES),
            "files": {
                str(path.relative_to(ROOT)): sha256_file(path) for path in SUBJECT_FILES
            },
        },
        "execution": {
            "runtime": str(RUNTIME.relative_to(ROOT)),
            "positive_fixture": str(REFERENCE.relative_to(ROOT)),
            "negative_fixture": str(NEGATIVE.relative_to(ROOT)),
            "crossed_boundaries": [
                "process",
                "filesystem",
                "serialization",
                "broker",
                "receipt",
                "replay",
            ],
        },
        "checks": checks,
        "standing": "ALIVE" if passed else "BUILD_BROKEN",
        "claim_ceiling": "REFERENCE_CONFORMANT" if passed else "TESTED",
        "nonclaims": authority.get("standing", {}).get("nonclaims", []),
        "replay": "REPLAY_MATCH" if passed else "REPLAY_UNVERIFIED",
    }
    output = ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
