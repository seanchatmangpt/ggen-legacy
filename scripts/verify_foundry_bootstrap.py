#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BOOTSTRAP = ROOT / "foundry" / "bootstrap.yaml"
# EXPECTED_STABLE_SOURCE: claimed to represent the ggen manufacturing
# repository's stable coordinate. Unreachable in this worktree
# (`git cat-file -t` fails); producing-repo/commit not independently
# confirmed. See tickets/GL-ERRC-011.md.
EXPECTED_STABLE = "0f39227c102e0ac7519f0f27561356227a518653"
# EXPECTED_PLAN_SOURCE: claimed to represent PR #543's plan-repo HEAD.
# Unreachable in this worktree; producing-repo/commit not independently
# confirmed. See tickets/GL-ERRC-011.md.
EXPECTED_PLAN = "999db36647feeb2dfd0bd2250d2db2ef00b887c4"
# EXPECTED_RECEIVING_RUNTIME_SOURCE: claimed to represent the receiving
# boundary workflow's observed runtime HEAD. Unreachable in this worktree;
# producing-repo/commit not independently confirmed. See
# tickets/GL-ERRC-011.md.
EXPECTED_RECEIVING_RUNTIME = "0175ead9748a7f41018ec037828865ae11cfe267"
# EXPECTED_CURRENT_RUNTIME_SOURCE: claimed to represent PR #544's runtime-
# repo HEAD candidate. Unreachable in this worktree; producing-repo/commit
# not independently confirmed. See tickets/GL-ERRC-011.md.
EXPECTED_CURRENT_RUNTIME = "f831e4d9fa80fe345349ce5d6e0fff41e6eb2a4a"
EXPECTED_DISPOSITIONS = [
    "PRESERVED",
    "SUBSUMED",
    "REPLACED",
    "ARCHIVED",
    "REFUSED",
]


def nested(data: dict, *path: str):
    current = data
    for key in path:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def stale_or(code: str) -> str:
    """Distinguish a mismatch against a known-unreachable EXPECTED_* constant
    (STALE_REFERENCE_UNVERIFIABLE) from a real bootstrap-coordinate
    discrepancy. The 4 EXPECTED_* hash constants in this file are confirmed
    unreachable git objects in this worktree (see tickets/GL-ERRC-011.md);
    resolving the canonical value is a repo-owner decision out of this
    ticket's scope.
    """
    return f"STALE_REFERENCE_UNVERIFIABLE:{code}"


def main() -> int:
    errors: list[str] = []
    bootstrap = json.loads(BOOTSTRAP.read_text())

    if bootstrap.get("schema_version") != "ggen.legacy.foundry.bootstrap/1":
        errors.append("BOOTSTRAP_SCHEMA_VERSION")
    if bootstrap.get("repository_role") != "ENTERPRISE_ARCHITECTURE_FOUNDRY_CORPUS":
        errors.append("BOOTSTRAP_REPOSITORY_ROLE")
    if bootstrap.get("authority_admitted") is not True:
        errors.append("BOOTSTRAP_AUTHORITY_NOT_ADMITTED")
    if bootstrap.get("runtime_dependency_admitted") is not False:
        errors.append("BOOTSTRAP_RUNTIME_PREMATURELY_ADMITTED")
    if bootstrap.get("standing") != "PARTIAL_ALIVE":
        errors.append("BOOTSTRAP_STANDING_OVERPROMOTION")

    coordinates = bootstrap.get("coordinates", {})
    expected_coordinates = {
        "stable_manufacturing_kernel": EXPECTED_STABLE,
        "foundry_plan": EXPECTED_PLAN,
        "receiving_runtime_observed": EXPECTED_RECEIVING_RUNTIME,
        "current_runtime_candidate": EXPECTED_CURRENT_RUNTIME,
        "corpus_base": "3c6480eb8a9d4c84474fd0f99ca21787cb424f2f",
    }
    if coordinates != expected_coordinates:
        # corpus_base is not one of the EXPECTED_* constants in scope for
        # GL-ERRC-011 (it is a distinct, separately-sourced literal); only
        # the EXPECTED_*-backed keys get the stale-reference distinction.
        stale_keys = {
            "stable_manufacturing_kernel",
            "foundry_plan",
            "receiving_runtime_observed",
            "current_runtime_candidate",
        }
        drifted_stale_keys = {
            key
            for key in stale_keys
            if coordinates.get(key) != expected_coordinates.get(key)
        }
        if drifted_stale_keys:
            errors.append(stale_or(f"BOOTSTRAP_COORDINATE_DRIFT:{','.join(sorted(drifted_stale_keys))}"))
        if coordinates.get("corpus_base") != expected_coordinates.get("corpus_base"):
            errors.append("BOOTSTRAP_COORDINATE_DRIFT:corpus_base")

    evidence = bootstrap.get("receiving_evidence", {})
    if evidence.get("real_git_tests") != 4 or evidence.get("real_git_failures") != 0:
        errors.append("BOOTSTRAP_REAL_GIT_EVIDENCE")
    if evidence.get("replay_match") is not True:
        errors.append("BOOTSTRAP_REPLAY_MISMATCH")
    if evidence.get("final_standing") != "PARTIAL_ALIVE":
        errors.append("BOOTSTRAP_RECEIVING_OVERPROMOTION")
    if evidence.get("admitted") is not False:
        errors.append("BOOTSTRAP_SELF_ADMISSION")

    workstreams = bootstrap.get("workstreams", [])
    if [item.get("id") for item in workstreams] != list("ABCDEFGHIJK"):
        errors.append("BOOTSTRAP_WORKSTREAM_IDENTITY")
    if any(item.get("status") != "NOT_STARTED" for item in workstreams):
        errors.append("BOOTSTRAP_WORKSTREAM_STATE_DRIFT")

    required_schema_paths = [ROOT / path for path in bootstrap.get("required_schemas", [])]
    if len(required_schema_paths) != 3 or any(not path.is_file() for path in required_schema_paths):
        errors.append("BOOTSTRAP_REQUIRED_SCHEMA_MISSING")

    migration = json.loads((ROOT / "schemas/migration-manifest.schema.json").read_text())
    disposition_enum = nested(migration, "$defs", "component", "properties", "disposition", "enum")
    if disposition_enum != EXPECTED_DISPOSITIONS:
        errors.append("MIGRATION_DISPOSITION_LAW")
    migration_required = set(nested(migration, "$defs", "component", "required") or [])
    for required in (
        "source_commit",
        "source_digest",
        "disposition",
        "destination_digest",
        "replacement_owner",
        "equivalence_case",
        "verifier_report",
        "receipt",
    ):
        if required not in migration_required:
            errors.append(f"MIGRATION_REQUIRED_{required.upper()}")

    workstream_schema = json.loads((ROOT / "schemas/workstream-report.schema.json").read_text())
    if nested(workstream_schema, "properties", "workstream", "enum") != list("ABCDEFGHIJK"):
        errors.append("WORKSTREAM_SCHEMA_IDENTITY")
    if "agent_status" in workstream_schema or "claimed_complete" in workstream_schema:
        errors.append("WORKSTREAM_SELF_REPORT_FIELD")

    final_schema = json.loads((ROOT / "schemas/final-evidence.schema.json").read_text())
    final_properties = nested(final_schema, "$defs", "finalPredicates", "properties") or {}
    expected_constants = {
        "ggen_kernel_admitted": True,
        "ggen_legacy_corpus_admitted": True,
        "unknown_capabilities": 0,
        "unknown_dispositions": 0,
        "unknown_standings": 0,
        "unassigned_verifiers": 0,
        "missing_equivalence_cases": 0,
        "equivalence_failures": 0,
        "replay_differences": 0,
        "cross_repository_receipts_valid": True,
        "fortune_scale_reference_manufactured": True,
        "solution_admission": True,
        "standing": "ALIVE",
    }
    observed_constants = {
        key: value.get("const") for key, value in final_properties.items()
    }
    if observed_constants != expected_constants:
        errors.append("FINAL_PREDICATE_LAW_DRIFT")

    report = {
        "schema": "ggen.legacy.foundry.bootstrap.verifier.v1",
        "bootstrap": str(BOOTSTRAP.relative_to(ROOT)),
        "coordinates": coordinates,
        "receiving_evidence": evidence,
        "workstreams": [item.get("id") for item in workstreams],
        "dispositions": disposition_enum,
        "errors": errors,
        "standing": "ALIVE" if not errors else "BUILD_BROKEN",
        "nonclaims": [
            "runtime dependency admitted",
            "complete foundry ALIVE",
            "PR #2 workflow authority",
            "real customer repository reconstituted",
        ],
    }
    output = ROOT / "evidence" / "foundry-bootstrap-verifier.json"
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
