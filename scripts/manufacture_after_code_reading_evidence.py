#!/usr/bin/env python3
"""Manufacture a non-promoting evidence packet for After Code Reading.

The producer observes and binds evidence. It never grants final standing.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

SCHEMA = "ggen.legacy.after-code-reading.manufacture.v1"
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--expected-revision", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    errors: list[str] = []

    revision = git(root, "rev-parse", "HEAD")
    tree = git(root, "rev-parse", "HEAD^{tree}")
    if revision != args.expected_revision:
        errors.append(f"EXACT_REVISION_MISMATCH:{revision}:{args.expected_revision}")
    errors.extend(f"REQUIRED_FILE_MISSING:{item}" for item in FILES if not (root / item).is_file())

    try:
        authority = json.loads((root / "authority/after-code-reading.json").read_text())
    except Exception as exc:  # noqa: BLE001
        authority = {}
        errors.append(f"AUTHORITY_INVALID:{exc}")

    if authority.get("schema") != "urn:chatman:ggen-legacy:after-code-reading:v1":
        errors.append("AUTHORITY_SCHEMA_MISMATCH")
    if authority.get("release") != "v26.8.1" or authority.get("ticket") != "TICKET-012":
        errors.append("AUTHORITY_IDENTITY_MISMATCH")
    observed_terms = tuple(
        item.get("term") for item in authority.get("category_stack", []) if isinstance(item, dict)
    )
    if observed_terms != TERMS:
        errors.append("CATEGORY_STACK_MISMATCH")
    if tuple(authority.get("control_loop", [])) != LOOP:
        errors.append("CONTROL_LOOP_MISMATCH")

    invariants = authority.get("hard_invariants", [])
    for invariant in (
        "The producer cannot certify itself.",
        "Unknown evidence cannot be promoted into success.",
        "Generated output cannot become a second authority.",
        "ALIVE requires exact-head evidence and independent replay.",
    ):
        if invariant not in invariants:
            errors.append(f"HARD_INVARIANT_MISSING:{invariant}")

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
    require(errors, root, "tickets/TICKET-012-after-code-reading-pivot.md", (
        "TICKET-012",
        "Negative falsifiers",
        "Replay",
    ))

    observed = [item for item in FILES if (root / item).is_file()]
    observations = {
        "exact_revision": revision,
        "exact_tree": tree,
        "required_file_count": len(FILES),
        "observed_file_count": len(observed),
        "source_set_sha256": source_digest(root) if len(observed) == len(FILES) else None,
        "authority_sha256": hashlib.sha256(
            (root / "authority/after-code-reading.json").read_bytes()
        ).hexdigest() if (root / "authority/after-code-reading.json").is_file() else None,
        "category_count": len(observed_terms),
        "control_loop_edge_count": max(0, len(LOOP) - 1),
        "prd_requirement_count": 11,
        "architecture_plane_count": len(PLANES),
        "files": {
            item: {
                "sha256": hashlib.sha256((root / item).read_bytes()).hexdigest(),
                "bytes": (root / item).stat().st_size,
            }
            for item in observed
        },
    }
    report: dict[str, Any] = {
        "schema": SCHEMA,
        "subject": {
            "repository": "seanchatmangpt/ggen-legacy",
            "scope": "after-code-reading-strategic-corpus",
            "release": "v26.8.1",
            "revision": revision,
            "tree": tree,
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
    report["receipt_sha256"] = hashlib.sha256(canonical(report)).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"standing": report["standing"], "errors": errors}, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
