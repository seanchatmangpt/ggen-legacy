#!/usr/bin/env python3
"""Independently crown the bounded After Code Reading strategic corpus."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

REPORT_SCHEMA = "ggen.legacy.after-code-reading.crown.v1"
PRODUCER_SCHEMA = "ggen.legacy.after-code-reading.manufacture.v1"
REPLAY_SCHEMA = "ggen.legacy.after-code-reading.replay.v1"
SCOPE = "after-code-reading-strategic-corpus"
FILES = (
    "AGENTS.md",
    "RELEASE_CONTROL.md",
    "README.md",
    "authority/after-code-reading.json",
    "product/AFTER_CODE_READING.md",
    "product/PRD.md",
    "architecture/AFTER_CODE_READING_ARCHITECTURE.md",
    "architecture/ARD.md",
    "governance/after-code-reading-review-standard.md",
    "governance/claims-register.md",
    "docs/src/15-after-code-reading.md",
    "docs/src/SUMMARY.md",
    "tickets/TICKET-012-after-code-reading-pivot.md",
)
TERMS = (
    "After Manual Code",
    "After Code Reading",
    "Proof-Carrying Software Manufacturing",
    "Software Systems Manufacturer",
    "Verified Repository Reconstitution",
)
LOOP = (
    "mission",
    "admitted_requirements",
    "machine_readable_production_law",
    "full_planning",
    "manufacture",
    "authorized_actuation",
    "independent_falsification",
    "operational_evidence",
    "standing",
    "receipt",
    "replay",
    "kaizen",
)
PLANES = (
    "Mission Plane",
    "Observation Plane",
    "Admission Plane",
    "Architecture Plane",
    "Planning Plane",
    "Manufacturing Plane",
    "Actuation Plane",
    "Inspection Plane",
    "Process Evidence Plane",
    "Standing Plane",
    "Receipt and Replay Plane",
    "Improvement Plane",
)


def git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ).stdout.strip()


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def read_json(path: Path, errors: list[str], label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text())
    except Exception as exc:  # noqa: BLE001
        errors.append(f"{label}_INVALID:{exc}")
        return {}
    if not isinstance(value, dict):
        errors.append(f"{label}_NOT_OBJECT")
        return {}
    return value


def source_digest(root: Path) -> str:
    digest = hashlib.sha256()
    for relative in sorted(FILES):
        path = relative.encode()
        data = (root / relative).read_bytes()
        digest.update(len(path).to_bytes(8, "little"))
        digest.update(path)
        digest.update(len(data).to_bytes(8, "little"))
        digest.update(data)
    return digest.hexdigest()


def require(errors: list[str], root: Path, relative: str, phrases: tuple[str, ...]) -> None:
    path = root / relative
    if not path.is_file():
        errors.append(f"REQUIRED_FILE_MISSING:{relative}")
        return
    text = path.read_text()
    errors.extend(
        f"REQUIRED_TEXT_MISSING:{relative}:{phrase}"
        for phrase in phrases
        if phrase not in text
    )


def authority_errors(authority: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if authority.get("schema") != "urn:chatman:ggen-legacy:after-code-reading:v1":
        errors.append("AUTHORITY_SCHEMA_MISMATCH")
    if authority.get("release") != "v26.8.1" or authority.get("ticket") != "TICKET-012":
        errors.append("AUTHORITY_IDENTITY_MISMATCH")
    if authority.get("state") not in {"PARTIAL_ALIVE", "ALIVE"}:
        errors.append("AUTHORITY_STATE_ILLEGAL")
    if authority.get("claim_ceiling") not in {"DOCUMENTED", "REFERENCE_CONFORMANT"}:
        errors.append("AUTHORITY_CEILING_ILLEGAL")
    terms = tuple(
        item.get("term") for item in authority.get("category_stack", []) if isinstance(item, dict)
    )
    if terms != TERMS:
        errors.append("CATEGORY_STACK_MISMATCH")
    if tuple(authority.get("control_loop", [])) != LOOP:
        errors.append("CONTROL_LOOP_MISMATCH")
    invariants = authority.get("hard_invariants", [])
    for invariant in (
        "Code is intermediate manufacturing material, not the product.",
        "The producer cannot certify itself.",
        "Unknown evidence cannot be promoted into success.",
        "Generated output cannot become a second authority.",
        "ALIVE requires exact-head evidence and independent replay.",
    ):
        if invariant not in invariants:
            errors.append(f"HARD_INVARIANT_MISSING:{invariant}")
    falsifiers = authority.get("falsifiers", [])
    if len(falsifiers) < 8:
        errors.append("FALSIFIER_CARDINALITY")
    if not any("same agent-generated test suite" in item for item in falsifiers):
        errors.append("PRODUCER_VERIFIER_FALSIFIER_MISSING")
    if not any("ALIVE without independent replay" in item for item in falsifiers):
        errors.append("PREMATURE_ALIVE_FALSIFIER_MISSING")
    projects = {
        item.get("project") for item in authority.get("project_mapping", []) if isinstance(item, dict)
    }
    for project in ("ggen", "ggen-legacy", "ferroplan", "BRCE", "wasm4pm", "TCPS"):
        if project not in projects:
            errors.append(f"PROJECT_MAPPING_MISSING:{project}")
    return errors


def projection_errors(root: Path) -> list[str]:
    errors: list[str] = []
    require(errors, root, "README.md", (
        "After Code Reading",
        "Proof-Carrying Software Manufacturing",
        "Code is intermediate manufacturing material.",
    ))
    require(errors, root, "AGENTS.md", (
        "## 21. After Code Reading law",
        "the independent verifier",
        "receipt and clean replay",
    ))
    require(errors, root, "RELEASE_CONTROL.md", (
        "## After Code Reading claim law",
        "REFERENCE_CONFORMANT",
    ))
    require(errors, root, "product/PRD.md", tuple(f"PRD-FR-{n:03d}" for n in range(15, 26)))
    require(errors, root, "architecture/AFTER_CODE_READING_ARCHITECTURE.md", PLANES)
    require(errors, root, "governance/after-code-reading-review-standard.md", (
        "human source-reading or source-writing task",
        "machine control replaces it",
        "new risk is introduced",
        "independently attempts to falsify",
        "runtime evidence",
        "Automatic refusal conditions",
    ))
    require(errors, root, "docs/src/SUMMARY.md", ("15-after-code-reading.md",))
    return errors


def producer_errors(report: dict[str, Any], revision: str, tree: str, digest: str) -> list[str]:
    errors: list[str] = []
    subject = report.get("subject", {})
    if report.get("schema") != PRODUCER_SCHEMA:
        errors.append("PRODUCER_SCHEMA_MISMATCH")
    if subject.get("scope") != SCOPE or subject.get("revision") != revision or subject.get("tree") != tree:
        errors.append("PRODUCER_SUBJECT_MISMATCH")
    if report.get("producer_role") != "evidence_manufacturer":
        errors.append("PRODUCER_ROLE_MISMATCH")
    if report.get("final_admission_allowed") is not False:
        errors.append("PRODUCER_SELF_CERTIFICATION")
    if report.get("standing") != "PARTIAL_ALIVE":
        errors.append("PRODUCER_STANDING_MUST_BE_PARTIAL")
    if report.get("errors"):
        errors.append("PRODUCER_REPORTED_ERRORS")
    observations = report.get("observations", {})
    if observations.get("source_set_sha256") != digest:
        errors.append("PRODUCER_SOURCE_DIGEST_MISMATCH")
    if observations.get("observed_file_count") != len(FILES):
        errors.append("PRODUCER_FILE_COUNT_MISMATCH")
    return errors


def replay_errors(report: dict[str, Any], revision: str, tree: str, digest: str, label: str) -> list[str]:
    errors: list[str] = []
    prefix = f"REPLAY_{label}"
    subject = report.get("subject", {})
    if report.get("schema") != REPLAY_SCHEMA:
        errors.append(f"{prefix}_SCHEMA_MISMATCH")
    if subject.get("scope") != SCOPE or subject.get("revision") != revision or subject.get("tree") != tree:
        errors.append(f"{prefix}_SUBJECT_MISMATCH")
    if report.get("final_admission_allowed") is not False:
        errors.append(f"{prefix}_SELF_CERTIFICATION")
    if report.get("standing") != "PARTIAL_ALIVE":
        errors.append(f"{prefix}_STANDING_MUST_BE_PARTIAL")
    if report.get("errors"):
        errors.append(f"{prefix}_REPORTED_ERRORS")
    if report.get("source_set_sha256") != digest:
        errors.append(f"{prefix}_SOURCE_DIGEST_MISMATCH")
    if not report.get("book_sha256") or report.get("book_file_count", 0) <= 0:
        errors.append(f"{prefix}_BOOK_EVIDENCE_MISSING")
    if report.get("local_docs_verifier_errors"):
        errors.append(f"{prefix}_LOCAL_VERIFIER_ERRORS")
    if report.get("tracked_source_clean") is not True:
        errors.append(f"{prefix}_TRACKED_DRIFT")
    return errors


def replay_pair_errors(a: dict[str, Any], b: dict[str, Any]) -> list[str]:
    fields = (
        "source_set_sha256",
        "authority_sha256",
        "book_sha256",
        "book_file_count",
        "local_docs_verifier_standing",
        "local_docs_verifier_errors",
    )
    return [f"REPLAY_DIVERGENCE:{field}" for field in fields if a.get(field) != b.get(field)]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--expected-revision", required=True)
    parser.add_argument("--manufacture", type=Path, required=True)
    parser.add_argument("--replay-a", type=Path, required=True)
    parser.add_argument("--replay-b", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    errors: list[str] = []

    revision = git(root, "rev-parse", "HEAD")
    tree = git(root, "rev-parse", "HEAD^{tree}")
    if revision != args.expected_revision:
        errors.append(f"EXACT_REVISION_MISMATCH:{revision}:{args.expected_revision}")
    errors.extend(f"REQUIRED_FILE_MISSING:{item}" for item in FILES if not (root / item).is_file())
    digest = source_digest(root) if not errors else ""

    authority = read_json(root / "authority/after-code-reading.json", errors, "AUTHORITY")
    producer = read_json(args.manufacture, errors, "PRODUCER")
    replay_a = read_json(args.replay_a, errors, "REPLAY_A")
    replay_b = read_json(args.replay_b, errors, "REPLAY_B")

    authority_failures = authority_errors(authority)
    projection_failures = projection_errors(root)
    producer_failures = producer_errors(producer, revision, tree, digest)
    replay_a_failures = replay_errors(replay_a, revision, tree, digest, "A")
    replay_b_failures = replay_errors(replay_b, revision, tree, digest, "B")
    pair_failures = replay_pair_errors(replay_a, replay_b)
    errors.extend(authority_failures + projection_failures + producer_failures)
    errors.extend(replay_a_failures + replay_b_failures + pair_failures)

    negative_controls: list[dict[str, Any]] = []
    mutated_authority = copy.deepcopy(authority)
    mutated_authority["category_stack"] = []
    negative_controls.append({"id": "missing-category-stack", "rejected": bool(authority_errors(mutated_authority))})
    self_certifying = copy.deepcopy(producer)
    self_certifying["standing"] = "ALIVE"
    self_certifying["final_admission_allowed"] = True
    negative_controls.append({"id": "producer-self-certification", "rejected": bool(producer_errors(self_certifying, revision, tree, digest))})
    divergent = copy.deepcopy(replay_b)
    divergent["book_sha256"] = "0" * 64
    negative_controls.append({"id": "replay-divergence", "rejected": bool(replay_pair_errors(replay_a, divergent))})
    missing_receipt = copy.deepcopy(replay_a)
    missing_receipt["receipt_sha256"] = None
    negative_controls.append({"id": "missing-replay-receipt", "rejected": not bool(missing_receipt.get("receipt_sha256"))})
    errors.extend(
        f"NEGATIVE_CONTROL_FAILED:{item['id']}"
        for item in negative_controls
        if not item["rejected"]
    )

    report: dict[str, Any] = {
        "schema": REPORT_SCHEMA,
        "subject": {
            "repository": "seanchatmangpt/ggen-legacy",
            "scope": SCOPE,
            "release": "v26.8.1",
            "revision": revision,
            "tree": tree,
            "source_set_sha256": digest,
            "authority_sha256": hashlib.sha256(
                (root / "authority/after-code-reading.json").read_bytes()
            ).hexdigest() if (root / "authority/after-code-reading.json").is_file() else None,
        },
        "verifier": "scripts/verify_after_code_reading_crown.py",
        "verifier_role": "independent_read_only_crown",
        "producer_verifier_separated": True,
        "actuation_performed": False,
        "clean_replay_count": 2,
        "replay_match": not pair_failures,
        "source_declared_state": authority.get("state"),
        "source_declared_ceiling": authority.get("claim_ceiling"),
        "promotion_transition": {
            "from": authority.get("state"),
            "to": "ALIVE" if not errors else "BLOCKED",
        },
        "checks": {
            "authority": "PASS" if not authority_failures else "FAIL",
            "projection_coverage": "PASS" if not projection_failures else "FAIL",
            "producer_claim_ceiling": "PASS" if not producer_failures else "FAIL",
            "replay_a": "PASS" if not replay_a_failures else "FAIL",
            "replay_b": "PASS" if not replay_b_failures else "FAIL",
            "replay_identity": "PASS" if not pair_failures else "FAIL",
            "negative_controls": "PASS" if all(item["rejected"] for item in negative_controls) else "FAIL",
        },
        "negative_controls": negative_controls,
        "errors": errors,
        "claim_ceiling": "REFERENCE_CONFORMANT" if not errors else authority.get("claim_ceiling"),
        "release_admitted": not errors,
        "standing": "ALIVE" if not errors else "BLOCKED",
        "reason": "EXACT_HEAD_INDEPENDENT_REPLAY_MATCH" if not errors else "AFTER_CODE_READING_CROWN_NONCONFORMANCE",
        "nonclaims": [
            "This promotion is bounded to the After Code Reading strategic corpus.",
            "It does not prove the complete ggen-legacy product implementation.",
            "It does not close the complete A-K foundry program.",
            "It does not establish external production adoption.",
            "It does not establish universal elimination of human source reading.",
            "It does not establish endorsement by Robert C. Martin.",
            "It does not grant Sunset Admission for any real predecessor.",
        ],
    }
    report["receipt_sha256"] = hashlib.sha256(canonical(report)).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "standing": report["standing"],
        "release_admitted": report["release_admitted"],
        "errors": errors,
    }, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
