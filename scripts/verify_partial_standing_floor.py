#!/usr/bin/env python3
"""Verify that every declared program rail is at least PARTIAL_ALIVE.

This verifier promotes no terminal product, customer, production, security,
performance, certification, or retirement claim. It verifies only that each
program rail has a bounded observed subset, evidence paths, explicit blockers,
and fail-closed claim boundaries.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

SCHEMA = "ggen.legacy.partial-standing-floor.report.v1"
AUTHORITY_SCHEMA = "ggen.legacy.partial-standing-floor.v1"
ALLOWED = {"PARTIAL_ALIVE", "ALIVE"}
REQUIRED_RAILS = {
    "documentation_and_authority",
    "after_code_reading_strategic_corpus",
    "verifier_appliance_reference",
    "offline_application_transport",
    "foundry_runtime_candidate",
    "complete_A_K_foundry_program",
    "complete_product_implementation_program",
    "external_no_read_case_program",
    "external_production_program",
    "production_security_program",
    "performance_and_availability_program",
    "compliance_evidence_and_certification_program",
    "real_predecessor_sunset_program",
}
CLAIM_GATES = {
    "complete_product_implementation_program": "completion_claim_allowed",
    "external_no_read_case_program": "external_success_claim_allowed",
    "external_production_program": "production_success_claim_allowed",
    "production_security_program": "secure_product_guarantee_allowed",
    "performance_and_availability_program": "production_targets_met_claim_allowed",
    "compliance_evidence_and_certification_program": "certification_claim_allowed",
    "real_predecessor_sunset_program": "real_sunset_success_claim_allowed",
}


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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--authority",
        type=Path,
        default=Path("authority/partial-standing-floor.json"),
    )
    parser.add_argument("--expected-revision", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    root = args.root.resolve()
    authority_path = args.authority
    if not authority_path.is_absolute():
        authority_path = root / authority_path

    errors: list[str] = []
    revision = git(root, "rev-parse", "HEAD")
    tree = git(root, "rev-parse", "HEAD^{tree}")
    if revision != args.expected_revision:
        errors.append(f"EXACT_REVISION_MISMATCH:{revision}:{args.expected_revision}")

    try:
        authority = json.loads(authority_path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        authority = {}
        errors.append(f"AUTHORITY_INVALID:{exc}")

    if authority.get("schema") != AUTHORITY_SCHEMA:
        errors.append("AUTHORITY_SCHEMA_MISMATCH")
    if authority.get("minimum_program_standing") != "PARTIAL_ALIVE":
        errors.append("MINIMUM_STANDING_MISMATCH")
    if set(authority.get("allowed_program_standings", [])) != ALLOWED:
        errors.append("ALLOWED_STANDING_SET_MISMATCH")

    policy = authority.get("policy", {})
    for field, expected in (
        ("unknown_program_rail_allowed", False),
        ("refused_program_rail_allowed", False),
        ("terminal_overclaim_allowed", False),
        ("missing_evidence_promoted_to_success", False),
        ("invalid_propositions_remain_refusable", True),
    ):
        if policy.get(field) is not expected:
            errors.append(f"POLICY_MISMATCH:{field}")

    rails = authority.get("rails", {})
    if not isinstance(rails, dict):
        rails = {}
        errors.append("RAILS_NOT_OBJECT")

    missing_rails = sorted(REQUIRED_RAILS - set(rails))
    extra_rails = sorted(set(rails) - REQUIRED_RAILS)
    errors.extend(f"REQUIRED_RAIL_MISSING:{rail}" for rail in missing_rails)
    errors.extend(f"UNDECLARED_RAIL:{rail}" for rail in extra_rails)

    checks: list[dict[str, Any]] = []
    for name in sorted(REQUIRED_RAILS):
        rail = rails.get(name, {})
        standing = rail.get("standing")
        rail_errors: list[str] = []
        if standing not in ALLOWED:
            rail_errors.append(f"ILLEGAL_STANDING:{standing}")
        if not isinstance(rail.get("observed_subset"), str) or not rail.get("observed_subset"):
            rail_errors.append("OBSERVED_SUBSET_MISSING")

        evidence = rail.get("evidence", [])
        if not isinstance(evidence, list) or not evidence:
            rail_errors.append("EVIDENCE_LIST_EMPTY")
        else:
            for relative in evidence:
                if not isinstance(relative, str) or not relative:
                    rail_errors.append("EVIDENCE_PATH_INVALID")
                    continue
                path = root / relative
                # Workflow-generated evidence is allowed to be absent before its
                # producer step, but every source authority path must exist.
                if not relative.startswith("evidence/") and not path.exists():
                    rail_errors.append(f"SOURCE_EVIDENCE_MISSING:{relative}")

        blockers = rail.get("blockers")
        if standing == "PARTIAL_ALIVE":
            if not isinstance(blockers, list) or not blockers:
                rail_errors.append("PARTIAL_BLOCKERS_MISSING")
        elif blockers not in ([], None):
            rail_errors.append("ALIVE_RAIL_HAS_BLOCKERS")

        claim_gate = CLAIM_GATES.get(name)
        if claim_gate and rail.get(claim_gate) is not False:
            rail_errors.append(f"TERMINAL_CLAIM_GATE_OPEN:{claim_gate}")

        if name == "compliance_evidence_and_certification_program":
            if rail.get("certification_observed") is not False:
                rail_errors.append("CERTIFICATION_OBSERVATION_MUST_BE_FALSE")
            if rail.get("terminal_claim_refusal") != "INDEPENDENT_ASSESSMENT_REQUIRED":
                rail_errors.append("CERTIFICATION_REFUSAL_MISSING")
        if name == "real_predecessor_sunset_program":
            if rail.get("real_predecessor_observed") is not False:
                rail_errors.append("REAL_PREDECESSOR_OBSERVATION_MUST_BE_FALSE")
            if rail.get("sunset_admitted") is not False:
                rail_errors.append("REAL_SUNSET_MUST_BE_FALSE")
        if name == "external_production_program" and rail.get("external_deployment_observed") is not False:
            rail_errors.append("EXTERNAL_DEPLOYMENT_OBSERVATION_MUST_BE_FALSE")
        if name == "external_no_read_case_program" and rail.get("external_case_observed") is not False:
            rail_errors.append("EXTERNAL_CASE_OBSERVATION_MUST_BE_FALSE")

        errors.extend(f"{name}:{item}" for item in rail_errors)
        checks.append(
            {
                "rail": name,
                "standing": standing,
                "passed": not rail_errors,
                "errors": rail_errors,
                "evidence_count": len(evidence) if isinstance(evidence, list) else 0,
                "blocker_count": len(blockers) if isinstance(blockers, list) else 0,
            }
        )

    report: dict[str, Any] = {
        "schema": SCHEMA,
        "subject": {
            "repository": "seanchatmangpt/ggen-legacy",
            "release": "v26.8.1",
            "revision": revision,
            "tree": tree,
            "authority_sha256": hashlib.sha256(authority_path.read_bytes()).hexdigest()
            if authority_path.is_file()
            else None,
        },
        "minimum_program_standing": "PARTIAL_ALIVE",
        "required_rail_count": len(REQUIRED_RAILS),
        "observed_rail_count": len(rails),
        "all_program_rails_at_least_partial_alive": not errors,
        "terminal_success_claims_promoted": False,
        "checks": checks,
        "errors": errors,
        "standing": "ALIVE" if not errors else "BLOCKED",
        "reason": "ALL_PROGRAM_RAILS_MEET_PARTIAL_ALIVE_FLOOR"
        if not errors
        else "PARTIAL_STANDING_FLOOR_NONCONFORMANCE",
        "nonclaims": [
            "Complete product implementation is not claimed complete.",
            "External production deployment is not claimed observed.",
            "Production security or availability is not guaranteed.",
            "Compliance or certification is not claimed.",
            "A real predecessor Sunset Admission is not claimed.",
            "An external no-read customer case is not claimed complete.",
        ],
    }
    report["receipt_sha256"] = hashlib.sha256(canonical(report)).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "standing": report["standing"],
        "all_program_rails_at_least_partial_alive": report[
            "all_program_rails_at_least_partial_alive"
        ],
        "errors": errors,
    }, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
