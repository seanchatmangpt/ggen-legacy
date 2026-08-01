#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUTHORITY = ROOT / "authority" / "foundry-work-program.json"
EXPECTED_STABLE_GGEN = "0f39227c102e0ac7519f0f27561356227a518653"
EXPECTED_PLAN_HEAD = "999db36647feeb2dfd0bd2250d2db2ef00b887c4"
EXPECTED_RUNTIME_HEAD = "f831e4d9fa80fe345349ce5d6e0fff41e6eb2a4a"
EXPECTED_RECEIVING_RUNTIME = "0175ead9748a7f41018ec037828865ae11cfe267"
EXPECTED_COMMANDS = [
    "validate-program",
    "baseline",
    "initialize-corpus",
    "extract",
    "admit-workstream",
    "admit-solution",
    "verify",
    "replay",
]


def main() -> int:
    data = json.loads(AUTHORITY.read_text())
    errors: list[str] = []

    provenance = data.get("provenance", {})
    if provenance.get("pull_request") != 543:
        errors.append("PR_543_IDENTITY")
    if provenance.get("head") != EXPECTED_PLAN_HEAD:
        errors.append("PR_543_HEAD_DRIFT")
    if provenance.get("standing_transferred") is not False:
        errors.append("PR_543_STANDING_TRANSFER")

    runtime = data.get("runtime_provenance", {})
    if runtime.get("pull_request") != 544:
        errors.append("PR_544_IDENTITY")
    if runtime.get("head") != EXPECTED_RUNTIME_HEAD:
        errors.append("PR_544_HEAD_DRIFT")
    if runtime.get("standing_transferred") is not False:
        errors.append("PR_544_STANDING_TRANSFER")
    if runtime.get("runtime_dependency_admitted") is not False:
        errors.append("OPEN_RUNTIME_DEPENDENCY_ADMITTED")
    if runtime.get("commands") != EXPECTED_COMMANDS:
        errors.append("RUNTIME_COMMAND_SURFACE_DRIFT")
    if runtime.get("real_boundary_test") != "tools/architecture-foundry/tests/real_git.rs":
        errors.append("RUNTIME_REAL_BOUNDARY_IDENTITY")

    dedicated = runtime.get("dedicated_runtime_evidence", {})
    if dedicated.get("workflow_run") != 30678356171:
        errors.append("RUNTIME_DEDICATED_WORKFLOW_IDENTITY")
    if dedicated.get("conclusion") != "success":
        errors.append("RUNTIME_DEDICATED_WORKFLOW_NOT_GREEN")
    if dedicated.get("exact_head") != EXPECTED_RUNTIME_HEAD:
        errors.append("RUNTIME_DEDICATED_HEAD_MISMATCH")

    prior = runtime.get("prior_failure_evidence", {})
    if prior.get("workflow_run") != 30677969304:
        errors.append("RUNTIME_PRIOR_FAILURE_IDENTITY")
    if prior.get("conclusion") != "failure":
        errors.append("RUNTIME_PRIOR_FAILURE_NOT_PRESERVED")
    if prior.get("typed_reason") != "SOURCE_WORKTREE_DIRTY_AFTER_WORKSPACE_FMT":
        errors.append("RUNTIME_PRIOR_FAILURE_REASON_DRIFT")

    receiving = runtime.get("receiving_boundary_evidence", {})
    if receiving.get("workflow_run") != 30678135632:
        errors.append("RECEIVING_WORKFLOW_IDENTITY")
    if receiving.get("conclusion") != "success":
        errors.append("RECEIVING_WORKFLOW_NOT_GREEN")
    if receiving.get("runtime_head") != EXPECTED_RECEIVING_RUNTIME:
        errors.append("RECEIVING_RUNTIME_HEAD_DRIFT")
    if receiving.get("real_git_tests") != 4 or receiving.get("real_git_failures") != 0:
        errors.append("RECEIVING_REAL_GIT_EVIDENCE_DRIFT")
    if receiving.get("replay_match") is not True:
        errors.append("RECEIVING_REPLAY_MISMATCH")
    if receiving.get("final_standing") != "PARTIAL_ALIVE":
        errors.append("RECEIVING_STANDING_OVERPROMOTION")
    if receiving.get("admitted") is not False:
        errors.append("RECEIVING_SELF_ADMISSION")
    if set(receiving.get("workflow_fences", [])) != {
        "MUTABLE_ACTION_COORDINATE",
        "FLOATING_RUNTIME_REFERENCE",
    }:
        errors.append("RECEIVING_WORKFLOW_FENCE_DRIFT")

    stable = data.get("repositories", {}).get("ggen", {}).get("manufacturing_coordinate")
    if stable != EXPECTED_STABLE_GGEN:
        errors.append("STABLE_MANUFACTURING_COORDINATE_DRIFT")

    workstreams = [item.get("id") for item in data.get("workstreams", [])]
    if workstreams != list("ABCDEFGHIJK"):
        errors.append("WORKSTREAM_DAG_IDENTITY")

    report = {
        "schema": "ggen.legacy.foundry.provenance.verifier.v1",
        "plan_head": provenance.get("head"),
        "runtime_head": runtime.get("head"),
        "stable_manufacturing_coordinate": stable,
        "runtime_dependency_admitted": runtime.get("runtime_dependency_admitted"),
        "dedicated_runtime_evidence": dedicated,
        "prior_failure_evidence": prior,
        "receiving_boundary_evidence": receiving,
        "commands": runtime.get("commands"),
        "errors": errors,
        "standing": "ALIVE" if not errors else "BUILD_BROKEN",
        "nonclaims": [
            "PR #543 product standing ALIVE",
            "PR #544 production dependency admitted",
            "PR #2 mutable workflow admissible",
            "complete A-K foundry closure",
        ],
    }
    output = ROOT / "evidence" / "foundry-provenance-verifier.json"
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
