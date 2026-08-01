#!/usr/bin/env python3
"""Manufacture a non-promoting evidence packet for the After Code Reading corpus.

This producer may observe and bind evidence. It may not grant final standing.
The independent crown verifier re-derives every material field.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

SCHEMA = "ggen.legacy.after-code-reading.manufacture.v1"
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
REQUIRED_ARCHITECTURE_PLANES = (
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


def run_git(root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(root), *args],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return completed.stdout.strip()


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def digest_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def digest_file(path: Path) -> str:
    return digest_bytes(path.read_bytes())


def digest_source_set(root: Path) -> str:
    hasher = hashlib.sha256()
    for relative in sorted(REQUIRED_FILES):
        data = (root / relative).read_bytes()
        encoded = relative.encode("utf-8")
        hasher.update(len(encoded).to_bytes(8, "little"))
        hasher.update(encoded)
        hasher.update(len(data).to_bytes(8, "little"))
        hasher.update(data)
    return hasher.hexdigest()


def require_text(errors: list[str], root: Path, relative: str, needles: tuple[str, ...]) -> None:
    path = root / relative
    if not path.is_file():
        errors.append(f"REQUIRED_FILE_MISSING:{relative}")
        return
    text = path.read_text(encoding="utf-8")
    for needle in needles:
        if needle not in text:
            errors.append(f"REQUIRED_TEXT_MISSING:{relative}:{needle}")


def validate(root: Path, expected_revision: str) -> tuple[list[str], dict[str, Any]]:
    errors: list[str] = []
    revision = run_git(root, "rev-parse", "HEAD")
    tree = run_git(root, "rev-parse", "HEAD^{tree}")
    if revision != expected_revision:
        errors.append(f"EXACT_REVISION_MISMATCH:{revision}:{expected_revision}")

    for relative in REQUIRED_FILES:
        if not (root / relative).is_file():
            errors.append(f"REQUIRED_FILE_MISSING:{relative}")

    authority_path = root / "authority/after-code-reading.json"
    try:
        authority = json.loads(authority_path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 - report typed verifier failure
        authority = {}
        errors.append(f"AUTHORITY_INVALID:{exc}")

    if authority.get("schema") != "urn:chatman:ggen-legacy:after-code-reading:v1":
        errors.append("AUTHORITY_SCHEMA_MISMATCH")
    if authority.get("release") != "v26.8.1":
        errors.append("AUTHORITY_RELEASE_MISMATCH")
    if authority.get("ticket") != "TICKET-012":
        errors.append("AUTHORITY_TICKET_MISMATCH")

    observed_terms = tuple(
        item.get("term")
        for item in authority.get("category_stack", [])
        if isinstance(item, dict)
    )
    if observed_terms != CATEGORY_TERMS:
        errors.append(f"CATEGORY_STACK_MISMATCH:{observed_terms!r}")
    if tuple(authority.get("control_loop", [])) != CONTROL_LOOP:
        errors.append("CONTROL_LOOP_MISMATCH")

    invariants = authority.get("hard_invariants", [])
    for required in (
        "The producer cannot certify itself.",
        "Unknown evidence cannot be promoted into success.",
        "Generated output cannot become a second authority.",
        "ALIVE requires exact-head evidence and independent replay.",
    ):
        if required not in invariants:
            errors.append(f"HARD_INVARIANT_MISSING:{required}")

    project_names = {
        item.get("project")
        for item in authority.get("project_mapping", [])
        if isinstance(item, dict)
    }
    for project in ("ggen", "ggen-legacy", "ferroplan", "BRCE", "wasm4pm", "TCPS"):
        if project not in project_names:
            errors.append(f"PROJECT_MAPPING_MISSING:{project}")

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
        REQUIRED_ARCHITECTURE_PLANES,
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
        "tickets/TICKET-012-after-code-reading-pivot.md",
        ("TICKET-012", "Falsifier", "Replay"),
    )

    files = {
        relative: {
            "sha256": digest_file(root / relative),
            "bytes": (root / relative).stat().st_size,
        }
        for relative in REQUIRED_FILES
        if (root / relative).is_file()
    }
    observations = {
        "exact_revision": revision,
        "exact_tree": tree,
        "required_file_count": len(REQUIRED_FILES),
        "observed_file_count": len(files),
        "source_set_sha256": digest_source_set(root) if len(files) == len(REQUIRED_FILES) else None,
        "authority_sha256": digest_file(authority_path) if authority_path.is_file() else None,
        "category_count": len(observed_terms),
        "control_loop_edge_count": max(0, len(CONTROL_LOOP) - 1),
        "prd_requirement_count": len(REQUIRED_PRD_IDS),
        "architecture_plane_count": len(REQUIRED_ARCHITECTURE_PLANES),
        "files": files,
    }
    return errors, observations


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--expected-revision", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    root = args.root.resolve()
    errors, observations = validate(root, args.expected_revision)
    report: dict[str, Any] = {
        "schema": SCHEMA,
        "subject": {
            "repository": "seanchatmangpt/ggen-legacy",
            "scope": "after-code-reading-strategic-corpus",
            "release": "v26.8.1",
            "revision": observations["exact_revision"],
            "tree": observations["exact_tree"],
        },
        "producer": "scripts/manufacture_after_code_reading_evidence.py",
        "producer_role": "evidence_manufacturer",
        "final_admission_allowed": False,
        "observations": observations,
        "errors": errors,
        "standing": "PARTIAL_ALIVE" if not errors else "BLOCKED",
        "reason": "INDEPENDENT_CROWN_REQUIRED" if not errors else "MANUFACTURE_NONCONFORMANCE",
        "nonclaims": [
            "This producer does not grant ALIVE.",
            "This report does not prove the complete ggen-legacy product.",
            "This report does not establish external production adoption.",
        ],
    }
    report["receipt_sha256"] = digest_bytes(canonical_bytes(report))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"standing": report["standing"], "errors": errors}, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
