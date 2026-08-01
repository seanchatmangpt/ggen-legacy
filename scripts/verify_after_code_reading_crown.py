#!/usr/bin/env python3
"""Independently crown the bounded After Code Reading strategic corpus.

The verifier does not import the producer implementation. It re-derives source
identity, authority semantics, projection coverage, replay identity, and the
producer's claim ceiling. It can promote only the declared strategic corpus;
it cannot promote the complete ggen-legacy product or external production use.
"""

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
REQUIRED_FILES = (
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
CATEGORY_TERMS = (
    "After Manual Code",
    "After Code Reading",
    "Proof-Carrying Software Manufacturing",
    "Software Systems Manufacturer",
    "Verified Repository Reconstitution",
)
CONTROL_LOOP = (
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
REQUIRED_PRD_IDS = tuple(f"PRD-FR-{number:03d}" for number in range(15, 26))
REQUIRED_PLANES = (
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


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def source_digest(root: Path) -> str:
    hasher = hashlib.sha256()
    for relative in sorted(REQUIRED_FILES):
        data = (root / relative).read_bytes()
        encoded = relative.encode("utf-8")
        hasher.update(len(encoded).to_bytes(8, "little"))
        hasher.update(encoded)
        hasher.update(len(data).to_bytes(8, "little"))
        hasher.update(data)
    return hasher.hexdigest()


def read_json(path: Path, errors: list[str], code: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 - verifier reports typed failure
        errors.append(f"{code}_INVALID:{exc}")
        return {}
    if not isinstance(value, dict):
        errors.append(f"{code}_NOT_OBJECT")
        return {}
    return value


def require_text(errors: list[str], root: Path, relative: str, needles: tuple[str, ...]) -> None:
    path = root / relative
    if not path.is_file():
        errors.append(f"REQUIRED_FILE_MISSING:{relative}")
        return
    text = path.read_text(encoding="utf-8")
    for needle in needles:
        if needle not in text:
            errors.append(f"REQUIRED_TEXT_MISSING:{relative}:{needle}")


def validate_authority(authority: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if authority.get("schema") != "urn:chatman:ggen-legacy:after-code-reading:v1":
        errors.append("AUTHORITY_SCHEMA_MISMATCH")
    if authority.get("release") != "v26.8.1":
        errors.append("AUTHORITY_RELEASE_MISMATCH")
    if authority.get("ticket") != "TICKET-012":
        errors.append("AUTHORITY_TICKET_MISMATCH")
    if authority.get("state") not in {"PARTIAL_ALIVE", "ALIVE"}:
        errors.append("AUTHORITY_STATE_ILLEGAL")
    if authority.get("claim_ceiling") not in {"DOCUMENTED", "REFERENCE_CONFORMANT"}:
        errors.append("AUTHORITY_CEILING_ILLEGAL")

    terms = tuple(
        item.get("term")
        for item in authority.get("category_stack", [])
        if isinstance(item, dict)
    )
    if terms != CATEGORY_TERMS:
        errors.append("CATEGORY_STACK_MISMATCH")
    if tuple(authority.get("control_loop", [])) != CONTROL_LOOP:
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
        item.get("project")
        for item in authority.get("project_mapping", [])
        if isinstance(item, dict)
    }
    for project in ("ggen", "ggen-legacy", "ferroplan", "BRCE", "wasm4pm", "TCPS"):
        if project not in projects:
            errors.append(f"PROJECT_MAPPING_MISSING:{project}")
    return errors


def validate_producer(
    producer: dict[str, Any],
    revision: str,
    tree: str,
    expected_source_digest: str,
) -> list[str]:
    errors: list[str] = []
    if producer.get("schema") != PRODUCER_SCHEMA:
        errors.append("PRODUCER_SCHEMA_MISMATCH")
    subject = producer.get("subject", {})
    if subject.get("scope") != SCOPE:
        errors.append("PRODUCER_SCOPE_MISMATCH")
    if subject.get("revision") != revision:
        errors.append("PRODUCER_REVISION_MISMATCH")
    if subject.get("tree") != tree:
        errors.append("PRODUCER_TREE_MISMATCH")
    if producer.get("producer_role") != "evidence_manufacturer":
        errors.append("PRODUCER_ROLE_MISMATCH")
    if producer.get("final_admission_allowed") is not False:
        errors.append("PRODUCER_SELF_CERTIFICATION")
    if producer.get("standing") != "PARTIAL_ALIVE":
        errors.append("PRODUCER_STANDING_MUST_BE_PARTIAL")
    if producer.get("errors"):
        errors.append("PRODUCER_REPORTED_ERRORS")
    observations = producer.get("observations", {})
    if observations.get("source_set_sha256") != expected_source_digest:
        errors.append("PRODUCER_SOURCE_DIGEST_MISMATCH")
    if observations.get("observed_file_count") != len(REQUIRED_FILES):
        errors.append("PRODUCER_FILE_COUNT_MISMATCH")
    return errors


def validate_replay(
    replay: dict[str, Any],
    revision: str,
    tree: str,
    expected_source_digest: str,
    label: str,
) -> list[str]:
    errors: list[str] = []
    prefix = f"REPLAY_{label}"
    if replay.get("schema") != REPLAY_SCHEMA:
        errors.append(f"{prefix}_SCHEMA_MISMATCH")
    subject = replay.get("subject", {})
    if subject.get("scope") != SCOPE:
        errors.append(f"{prefix}_SCOPE_MISMATCH")
    if subject.get("revision") != revision:
        errors.append(f"{prefix}_REVISION_MISMATCH")
    if subject.get("tree") != tree:
        errors.append(f"{prefix}_TREE_MISMATCH")
    if replay.get("final_admission_allowed") is not False:
        errors.append(f"{prefix}_SELF_CERTIFICATION")
    if replay.get("standing") != "PARTIAL_ALIVE":
        errors.append(f"{prefix}_STANDING_MUST_BE_PARTIAL")
    if replay.get("errors"):
        errors.append(f"{prefix}_REPORTED_ERRORS")
    if replay.get("source_set_sha256") != expected_source_digest:
        errors.append(f"{prefix}_SOURCE_DIGEST_MISMATCH")
    if not replay.get("book_sha256"):
        errors.append(f"{prefix}_BOOK_DIGEST_MISSING")
    if replay.get("book_file_count", 0) <= 0:
        errors.append(f"{prefix}_BOOK_EMPTY")
    if replay.get("local_docs_verifier_errors"):
        errors.append(f"{prefix}_LOCAL_VERIFIER_ERRORS")
    if replay.get("tracked_source_clean") is not True:
        errors.append(f"{prefix}_TRACKED_DRIFT")
    return errors


def validate_replay_pair(a: dict[str, Any], b: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for field in (
        "source_set_sha256",
        "authority_sha256",
        "book_sha256",
        "book_file_count",
        "local_docs_verifier_standing",
        "local_docs_verifier_errors",
    ):
        if a.get(field) != b.get(field):
            errors.append(f"REPLAY_DIVERGENCE:{field}")
    return errors


def validate_projection_text(root: Path) -> list[str]:
    errors: list[str] = []
    require_text(
        errors,
        root,
        "README.md",
        (
            "After Code Reading",
            "Proof-Carrying Software Manufacturing",
            "Code is intermediate manufacturing material.",
        ),
    )
    require_text(
        errors,
        root,
        "AGENTS.md",
        ("## 21. After Code Reading law", "The producer cannot certify itself"),
    )
    require_text(
        errors,
        root,
        "RELEASE_CONTROL.md",
        ("## After Code Reading claim law", "REFERENCE_CONFORMANT"),
    )
    require_text(errors, root, "product/PRD.md", REQUIRED_PRD_IDS)
    require_text(
        errors,
        root,
        "architecture/AFTER_CODE_READING_ARCHITECTURE.md",
        REQUIRED_PLANES,
    )
    require_text(
        errors,
        root,
        "governance/after-code-reading-review-standard.md",
        (
            "human-reading task",
            "replacement control",
            "new risk",
            "independent verifier",
            "evidence",
            "automatic stop",
        ),
    )
    require_text(
        errors,
        root,
        "docs/src/SUMMARY.md",
        ("15-after-code-reading.md",),
    )
    return errors


def run_negative_controls(
    authority: dict[str, Any],
    producer: dict[str, Any],
    replay_a: dict[str, Any],
    replay_b: dict[str, Any],
    revision: str,
    tree: str,
    expected_source_digest: str,
) -> tuple[list[dict[str, Any]], list[str]]:
    checks: list[dict[str, Any]] = []
    failures: list[str] = []

    mutated_authority = copy.deepcopy(authority)
    mutated_authority["category_stack"] = []
    rejected = bool(validate_authority(mutated_authority))
    checks.append({"id": "missing-category-stack", "rejected": rejected})
    if not rejected:
        failures.append("NEGATIVE_CONTROL_FAILED:missing-category-stack")

    self_certifying = copy.deepcopy(producer)
    self_certifying["standing"] = "ALIVE"
    self_certifying["final_admission_allowed"] = True
    rejected = bool(
        validate_producer(self_certifying, revision, tree, expected_source_digest)
    )
    checks.append({"id": "producer-self-certification", "rejected": rejected})
    if not rejected:
        failures.append("NEGATIVE_CONTROL_FAILED:producer-self-certification")

    divergent = copy.deepcopy(replay_b)
    divergent["book_sha256"] = "0" * 64
    rejected = bool(validate_replay_pair(replay_a, divergent))
    checks.append({"id": "replay-divergence", "rejected": rejected})
    if not rejected:
        failures.append("NEGATIVE_CONTROL_FAILED:replay-divergence")

    missing_receipt = copy.deepcopy(replay_a)
    missing_receipt["receipt_sha256"] = None
    rejected = not bool(missing_receipt.get("receipt_sha256"))
    checks.append({"id": "missing-replay-receipt", "rejected": rejected})
    if not rejected:
        failures.append("NEGATIVE_CONTROL_FAILED:missing-replay-receipt")

    return checks, failures


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

    for relative in REQUIRED_FILES:
        if not (root / relative).is_file():
            errors.append(f"REQUIRED_FILE_MISSING:{relative}")

    expected_source_digest = source_digest(root) if not errors else ""
    authority = read_json(root / "authority/after-code-reading.json", errors, "AUTHORITY")
    producer = read_json(args.manufacture, errors, "PRODUCER")
    replay_a = read_json(args.replay_a, errors, "REPLAY_A")
    replay_b = read_json(args.replay_b, errors, "REPLAY_B")

    errors.extend(validate_authority(authority))
    errors.extend(validate_projection_text(root))
    errors.extend(validate_producer(producer, revision, tree, expected_source_digest))
    errors.extend(validate_replay(replay_a, revision, tree, expected_source_digest, "A"))
    errors.extend(validate_replay(replay_b, revision, tree, expected_source_digest, "B"))
    errors.extend(validate_replay_pair(replay_a, replay_b))

    negative_controls, negative_failures = run_negative_controls(
        authority,
        producer,
        replay_a,
        replay_b,
        revision,
        tree,
        expected_source_digest,
    )
    errors.extend(negative_failures)

    source_state = authority.get("state")
    source_ceiling = authority.get("claim_ceiling")
    report: dict[str, Any] = {
        "schema": REPORT_SCHEMA,
        "subject": {
            "repository": "seanchatmangpt/ggen-legacy",
            "scope": SCOPE,
            "release": "v26.8.1",
            "revision": revision,
            "tree": tree,
            "source_set_sha256": expected_source_digest,
            "authority_sha256": sha256_file(root / "authority/after-code-reading.json")
            if (root / "authority/after-code-reading.json").is_file()
            else None,
        },
        "verifier": "scripts/verify_after_code_reading_crown.py",
        "verifier_role": "independent_read_only_crown",
        "producer_verifier_separated": True,
        "actuation_performed": False,
        "clean_replay_count": 2,
        "replay_match": not bool(validate_replay_pair(replay_a, replay_b)),
        "source_declared_state": source_state,
        "source_declared_ceiling": source_ceiling,
        "promotion_transition": {
            "from": source_state,
            "to": "ALIVE" if not errors else "BLOCKED",
        },
        "checks": {
            "authority": "PASS" if not validate_authority(authority) else "FAIL",
            "projection_coverage": "PASS" if not validate_projection_text(root) else "FAIL",
            "producer_claim_ceiling": "PASS"
            if not validate_producer(producer, revision, tree, expected_source_digest)
            else "FAIL",
            "replay_a": "PASS"
            if not validate_replay(replay_a, revision, tree, expected_source_digest, "A")
            else "FAIL",
            "replay_b": "PASS"
            if not validate_replay(replay_b, revision, tree, expected_source_digest, "B")
            else "FAIL",
            "replay_identity": "PASS" if not validate_replay_pair(replay_a, replay_b) else "FAIL",
            "negative_controls": "PASS" if not negative_failures else "FAIL",
        },
        "negative_controls": negative_controls,
        "errors": errors,
        "claim_ceiling": "REFERENCE_CONFORMANT" if not errors else source_ceiling,
        "release_admitted": not errors,
        "standing": "ALIVE" if not errors else "BLOCKED",
        "reason": "EXACT_HEAD_INDEPENDENT_REPLAY_MATCH"
        if not errors
        else "AFTER_CODE_READING_CROWN_NONCONFORMANCE",
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
    report["receipt_sha256"] = sha256_bytes(canonical_bytes(report))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "standing": report["standing"],
                "release_admitted": report["release_admitted"],
                "errors": errors,
            },
            sort_keys=True,
        )
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
