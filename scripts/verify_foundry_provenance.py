#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUTHORITY = ROOT / "authority" / "foundry-work-program.json"
EXPECTED_STABLE_GGEN = "0f39227c102e0ac7519f0f27561356227a518653"
EXPECTED_PLAN_HEAD = "999db36647feeb2dfd0bd2250d2db2ef00b887c4"
EXPECTED_RUNTIME_HEAD = "7313d60266111bca7ff21257b71f68a6535e7294"
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
        "commands": runtime.get("commands"),
        "errors": errors,
        "standing": "ALIVE" if not errors else "BUILD_BROKEN",
        "nonclaims": [
            "PR #543 ALIVE",
            "PR #544 ALIVE",
            "PR #544 executed by Project 001",
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
