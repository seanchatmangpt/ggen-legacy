#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


STATUS_REFUSED = 3
ALLOWED_EFFECT = "WRITE_DECLARED_PROJECTION"
REFUSAL_EFFECT = "WRITE_REFUSAL_EVIDENCE"


def canonical(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise ValueError(f"expected object: {path}")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical(value) + b"\n")


def refusal(
    out_dir: Path,
    code: str,
    detail: Any,
    authority_sha256: str,
    program_sha256: str,
) -> int:
    report = {
        "schema": "ggen.legacy.fullerian.autonomics.refusal.v1",
        "refusal": code,
        "detail": detail,
        "authority_sha256": authority_sha256,
        "program_sha256": program_sha256,
        "standing": "REFUSED",
    }
    refusal_path = out_dir / "refusal.json"
    write_json(refusal_path, report)
    refusal_sha256 = sha256_file(refusal_path)
    receipt = {
        "schema": "ggen.legacy.fullerian.autonomics.refusal-receipt.v1",
        "run_id": sha256_bytes(
            canonical(
                {
                    "authority_sha256": authority_sha256,
                    "program_sha256": program_sha256,
                    "refusal": code,
                    "output_sha256": refusal_sha256,
                }
            )
        ),
        "authority_sha256": authority_sha256,
        "program_sha256": program_sha256,
        "refusal": code,
        "effect": REFUSAL_EFFECT,
        "output_sha256": refusal_sha256,
        "broker": "BRCE",
        "exit_status": STATUS_REFUSED,
        "standing": "REFUSED",
    }
    write_json(out_dir / "refusal-receipt.json", receipt)
    print(json.dumps(report, sort_keys=True))
    return STATUS_REFUSED


def monitor(program: dict[str, Any]) -> tuple[list[dict[str, Any]], str | None]:
    boundary = program.get("system_boundary")
    observations = program.get("observations")
    if not isinstance(boundary, str) or not boundary:
        return [], "BOUNDARY_MISMATCH_REFUSED"
    if not isinstance(observations, list) or not observations:
        return [], "MISSING_PROVENANCE_REFUSED"
    monitored: list[dict[str, Any]] = []
    for observation in observations:
        if not isinstance(observation, dict):
            return [], "MISSING_PROVENANCE_REFUSED"
        if not all(key in observation for key in ("id", "provenance", "boundary", "value")):
            return [], "MISSING_PROVENANCE_REFUSED"
        if not isinstance(observation.get("provenance"), str) or not observation["provenance"]:
            return [], "MISSING_PROVENANCE_REFUSED"
        if observation.get("boundary") != boundary:
            return [], "BOUNDARY_MISMATCH_REFUSED"
        monitored.append(observation)
    return monitored, None


def analyze(
    program: dict[str, Any], authority: dict[str, Any]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], str | None]:
    monitored, error = monitor(program)
    if error:
        return [], [], error
    allowed_effects = set(authority.get("actuation", {}).get("allowed_effects", []))
    candidates = program.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        return monitored, [], "UNSUPPORTED"
    admitted: list[dict[str, Any]] = []
    refused: list[dict[str, Any]] = []
    for candidate in candidates:
        if not isinstance(candidate, dict):
            refused.append({"id": "UNKNOWN", "refusal": "UNSUPPORTED"})
            continue
        candidate_id = str(candidate.get("id", "UNKNOWN"))
        if candidate.get("effect") not in allowed_effects:
            refused.append({"id": candidate_id, "refusal": "UNSUPPORTED"})
            continue
        if candidate.get("unrepresented_stakeholders"):
            refused.append(
                {"id": candidate_id, "refusal": "STAKEHOLDER_EXTERNALITY_REFUSED"}
            )
            continue
        if candidate.get("represented_stakeholder_coverage") != 1.0:
            refused.append(
                {"id": candidate_id, "refusal": "STAKEHOLDER_EXTERNALITY_REFUSED"}
            )
            continue
        if candidate.get("ecological_externality_known") is not True:
            refused.append({"id": candidate_id, "refusal": "ECOLOGICAL_UNKNOWN_REFUSED"})
            continue
        numeric = (
            "lawful_reversible_options",
            "irreversible_commitments",
            "outcome_units",
            "resource_units",
        )
        if any(not isinstance(candidate.get(key), (int, float)) for key in numeric):
            refused.append({"id": candidate_id, "refusal": "UNSUPPORTED"})
            continue
        if candidate["resource_units"] <= 0 or candidate["outcome_units"] <= 0:
            refused.append({"id": candidate_id, "refusal": "UNSUPPORTED"})
            continue
        admitted.append(candidate)
    if not admitted:
        return monitored, refused, "UNSUPPORTED"
    return monitored, refused, None


def candidate_key(candidate: dict[str, Any]) -> tuple[Any, ...]:
    return (
        -float(candidate["represented_stakeholder_coverage"]),
        -int(bool(candidate["ecological_externality_known"])),
        -int(candidate["lawful_reversible_options"]),
        int(candidate["irreversible_commitments"]),
        -(float(candidate["outcome_units"]) / float(candidate["resource_units"])),
        str(candidate["id"]),
    )


def plan(admitted: list[dict[str, Any]]) -> dict[str, Any]:
    selected = sorted(admitted, key=candidate_key)[0]
    return {
        "selected_candidate": selected["id"],
        "effect": selected["effect"],
        "lawful_reversible_options": selected["lawful_reversible_options"],
        "irreversible_commitments": selected["irreversible_commitments"],
        "outcome_per_resource": (
            float(selected["outcome_units"]) / float(selected["resource_units"])
        ),
        "repair_mode": "INTENT_ONLY",
    }


def safe_target(out_dir: Path, raw_target: Any) -> Path | None:
    if not isinstance(raw_target, str) or not raw_target:
        return None
    relative = Path(raw_target)
    if relative.is_absolute() or ".." in relative.parts:
        return None
    resolved_root = out_dir.resolve()
    resolved_target = (out_dir / relative).resolve()
    if resolved_target != resolved_root and resolved_root not in resolved_target.parents:
        return None
    return resolved_target


def broker_execute(
    out_dir: Path,
    authority: dict[str, Any],
    program: dict[str, Any],
    monitored: list[dict[str, Any]],
    refused_candidates: list[dict[str, Any]],
    planned: dict[str, Any],
    authority_sha256: str,
    program_sha256: str,
) -> int:
    execution = program.get("execution", {})
    if execution.get("mode") != "BROKERED_WRITE":
        return refusal(
            out_dir,
            "AMBIENT_EXECUTION_REFUSED",
            execution.get("mode"),
            authority_sha256,
            program_sha256,
        )
    if execution.get("authorized") is not True:
        return refusal(
            out_dir,
            "AMBIENT_EXECUTION_REFUSED",
            "broker authorization absent",
            authority_sha256,
            program_sha256,
        )
    if program.get("requested_standing") == "REPOSITORY_ALIVE":
        return refusal(
            out_dir,
            "CROWN_ESCALATION_REFUSED",
            "reference automaton has no repository crown authority",
            authority_sha256,
            program_sha256,
        )
    target = safe_target(out_dir, execution.get("target"))
    if target is None:
        return refusal(
            out_dir,
            "PATH_ESCAPE_REFUSED",
            execution.get("target"),
            authority_sha256,
            program_sha256,
        )
    projection = {
        "schema": "ggen.legacy.fullerian.autonomics.projection.v1",
        "mape_k": ["MONITOR", "ANALYZE", "PLAN", "EXECUTE"],
        "system_boundary": program["system_boundary"],
        "admitted_observation_ids": sorted(str(item["id"]) for item in monitored),
        "refused_candidates": sorted(
            refused_candidates, key=lambda item: (item["id"], item["refusal"])
        ),
        "plan": planned,
        "standing": "PARTIAL_ALIVE",
        "nonclaims": authority["standing"]["nonclaims"],
    }
    write_json(target, projection)
    output_sha256 = sha256_file(target)
    run_id = sha256_bytes(
        canonical(
            {
                "authority_sha256": authority_sha256,
                "program_sha256": program_sha256,
                "selected_candidate": planned["selected_candidate"],
                "output_sha256": output_sha256,
            }
        )
    )
    receipt = {
        "schema": "ggen.legacy.fullerian.autonomics.receipt.v1",
        "run_id": run_id,
        "admitted_base_sha": program["admitted_base_sha"],
        "authority_sha256": authority_sha256,
        "program_sha256": program_sha256,
        "selected_candidate": planned["selected_candidate"],
        "effect": planned["effect"],
        "output_sha256": output_sha256,
        "broker": "BRCE",
        "exit_status": 0,
        "standing": "PARTIAL_ALIVE",
    }
    write_json(out_dir / "receipt.json", receipt)
    report = {
        "schema": "ggen.legacy.fullerian.autonomics.run.v1",
        "run_id": run_id,
        "selected_candidate": planned["selected_candidate"],
        "projection": str(target.relative_to(out_dir.resolve())),
        "receipt": "receipt.json",
        "standing": "PARTIAL_ALIVE",
    }
    write_json(out_dir / "run-report.json", report)
    print(json.dumps(report, sort_keys=True))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--authority", required=True)
    parser.add_argument("--program", required=True)
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()

    authority_path = Path(args.authority).resolve()
    program_path = Path(args.program).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    authority = read_json(authority_path)
    program = read_json(program_path)
    authority_sha256 = sha256_file(authority_path)
    program_sha256 = sha256_file(program_path)

    if authority.get("schema") != "ggen.legacy.fullerian.autonomics.authority.v1":
        return refusal(
            out_dir,
            "UNSUPPORTED",
            "authority schema",
            authority_sha256,
            program_sha256,
        )
    if program.get("schema") != "ggen.legacy.fullerian.autonomics.program.v1":
        return refusal(
            out_dir,
            "UNSUPPORTED",
            "program schema",
            authority_sha256,
            program_sha256,
        )
    if program.get("admitted_base_sha") != authority.get("admitted_base_sha"):
        return refusal(
            out_dir,
            "BOUNDARY_MISMATCH_REFUSED",
            "admitted base SHA",
            authority_sha256,
            program_sha256,
        )

    monitored, refused_candidates, error = analyze(program, authority)
    if error:
        return refusal(
            out_dir,
            error,
            refused_candidates,
            authority_sha256,
            program_sha256,
        )
    planned = plan(
        [
            candidate
            for candidate in program["candidates"]
            if not any(item["id"] == candidate["id"] for item in refused_candidates)
        ]
    )
    return broker_execute(
        out_dir,
        authority,
        program,
        monitored,
        refused_candidates,
        planned,
        authority_sha256,
        program_sha256,
    )


if __name__ == "__main__":
    raise SystemExit(main())
