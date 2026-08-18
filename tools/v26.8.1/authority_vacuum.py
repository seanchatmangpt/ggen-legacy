#!/usr/bin/env python3
"""Observe authority-free legacy corpora and admit only explicit bounded O* contracts.

The observer deliberately cannot decide what an arbitrary program "really is". It verifies
exact coordinates where bytes are available, records controlled contradictions, and emits a
deterministic `NO_AUTHORITY` report. Admission is a separate operation over an explicit,
digest-bound contract. Neither operation actuates anything.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

STUDY_SCHEMA = "ggen.legacy.authority-vacuum.study.v1"
OBSERVATION_SCHEMA = "ggen.legacy.authority-vacuum.observation.v1"
ADMISSION_SCHEMA = "ggen.legacy.authority-vacuum.admission.v1"
CONTRACT_SCHEMA = "ggen.legacy.authority-vacuum.contract.v1"
RECEIPT_SCHEMA = "ggen.legacy.authority-vacuum.receipt.v1"
DISPOSITIONS = {"PRESERVED", "SUBSUMED", "REPLACED", "ARCHIVED", "REFUSED"}
SURFACES = {
    "exit_code",
    "stdout",
    "stderr",
    "filesystem_delta",
    "generated_bytes",
    "diagnostics",
    "receipt_fields",
    "event_order",
    "side_effects",
    "recovery_result",
}
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")


class AuthorityVacuumError(RuntimeError):
    def __init__(self, code: str, message: str, detail: dict[str, Any] | None = None):
        super().__init__(message)
        self.code = code
        self.detail = detail or {}

    def as_json(self) -> dict[str, Any]:
        return {"status": "REFUSED", "code": self.code, "message": str(self), "detail": self.detail}


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def load_json(path: Path, code: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise AuthorityVacuumError(code, f"cannot read {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise AuthorityVacuumError(code, f"{path} must contain a JSON object")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_bytes(value))


def command(argv: list[str], cwd: Path) -> str:
    result = subprocess.run(argv, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if result.returncode != 0:
        raise AuthorityVacuumError(
            "SUBJECT_COMMAND_FAILED",
            f"command failed ({result.returncode}): {' '.join(argv)}",
            {"stderr": result.stderr[-4000:]},
        )
    return result.stdout.strip()


def _require(condition: bool, code: str, message: str, detail: dict[str, Any] | None = None) -> None:
    if not condition:
        raise AuthorityVacuumError(code, message, detail)


def validate_study(study: dict[str, Any]) -> None:
    _require(study.get("schema") == STUDY_SCHEMA, "STUDY_SCHEMA_INVALID", "study schema is not admitted")
    _require(isinstance(study.get("study_id"), str) and study["study_id"].strip(), "STUDY_ID_INVALID", "study_id must be a non-empty string")
    _require(study.get("initial_authority_state") == "NO_AUTHORITY", "OBSERVATION_SELF_ADMISSION_REFUSED", "observation must begin in NO_AUTHORITY")
    _require(study.get("direct_actuation") is False, "OBSERVATION_ACTUATION_REFUSED", "observation studies must explicitly disable direct actuation")
    _require("canonical_subject" not in study, "CANONICAL_SUBJECT_SELECTION_REFUSED", "an observation study may not select a canonical subject")
    scope = study.get("semantic_scope", {})
    _require(scope.get("mode") == "bounded-observable-surfaces", "RICE_SCOPE_UNBOUNDED", "semantic scope must be bounded-observable-surfaces")
    _require(scope.get("universal_equivalence_claimed") is False, "RICE_SCOPE_UNBOUNDED", "universal semantic equivalence cannot be claimed")

    controlled = study.get("controlled_predicates")
    _require(isinstance(controlled, list) and controlled, "STUDY_PREDICATES_MISSING", "study requires controlled predicates")
    controlled_names: set[str] = set()
    for item in controlled:
        _require(isinstance(item, dict), "STUDY_PREDICATE_INVALID", "controlled predicates must be objects")
        predicate = item.get("predicate")
        _require(isinstance(predicate, str) and predicate and predicate not in controlled_names, "STUDY_PREDICATE_INVALID", "controlled predicate names must be unique non-empty strings")
        _require(item.get("cardinality") == "one", "STUDY_PREDICATE_INVALID", f"controlled predicate {predicate} must declare cardinality one")
        controlled_names.add(predicate)

    subjects = study.get("subjects")
    _require(isinstance(subjects, list) and subjects, "STUDY_SUBJECTS_MISSING", "study requires at least one subject")
    subject_ids: set[str] = set()
    evidence_ids: set[str] = set()
    evidence_subjects: dict[str, str] = {}
    for subject in subjects:
        _require(isinstance(subject, dict), "STUDY_SUBJECT_INVALID", "subjects must be objects")
        sid = subject.get("id")
        _require(isinstance(sid, str) and sid and sid not in subject_ids, "STUDY_SUBJECT_INVALID", "subject ids must be unique non-empty strings")
        subject_ids.add(sid)
        _require(isinstance(subject.get("repo"), str) and subject["repo"].strip(), "STUDY_SUBJECT_INVALID", f"subject {sid} requires a repository identity")
        _require(isinstance(subject.get("transport"), str) and subject["transport"].strip(), "STUDY_SUBJECT_INVALID", f"subject {sid} requires a transport")
        _require(subject.get("authority") is not True, "OBSERVATION_SELF_ADMISSION_REFUSED", f"subject {sid} cannot carry authority")
        exact_sha = subject.get("exact_sha")
        _require(exact_sha is None or bool(HEX40.fullmatch(str(exact_sha))), "STUDY_SUBJECT_INVALID", f"subject {sid} exact_sha must be null or 40 lowercase hex")
        artifacts = subject.get("artifacts")
        _require(isinstance(artifacts, list), "STUDY_EVIDENCE_INVALID", f"subject {sid} artifacts must be a list")
        for artifact in artifacts:
            _require(isinstance(artifact, dict), "STUDY_EVIDENCE_INVALID", "artifacts must be objects")
            eid = artifact.get("id")
            _require(isinstance(eid, str) and eid and eid not in evidence_ids, "STUDY_EVIDENCE_INVALID", "artifact ids must be unique non-empty strings")
            evidence_ids.add(eid)
            evidence_subjects[eid] = sid
            path = artifact.get("path")
            _require(isinstance(path, str) and path and not Path(path).is_absolute() and ".." not in Path(path).parts, "STUDY_EVIDENCE_INVALID", f"artifact {eid} path is unsafe")
            _require(bool(HEX40.fullmatch(str(artifact.get("git_blob_sha1", "")))), "STUDY_EVIDENCE_INVALID", f"artifact {eid} requires a Git blob SHA-1")

    observations = study.get("observations")
    _require(isinstance(observations, list) and observations, "STUDY_OBSERVATIONS_MISSING", "study requires observations")
    observation_ids: set[str] = set()
    for observation in observations:
        _require(isinstance(observation, dict), "STUDY_OBSERVATION_INVALID", "observations must be objects")
        oid = observation.get("id")
        _require(isinstance(oid, str) and oid and oid not in observation_ids, "STUDY_OBSERVATION_INVALID", "observation ids must be unique non-empty strings")
        observation_ids.add(oid)
        _require(observation.get("subject") in subject_ids, "STUDY_OBSERVATION_INVALID", f"observation {oid} references an unknown subject")
        _require(observation.get("evidence") in evidence_ids, "STUDY_OBSERVATION_INVALID", f"observation {oid} references unknown evidence")
        _require(evidence_subjects[observation["evidence"]] == observation["subject"], "STUDY_OBSERVATION_INVALID", f"observation {oid} evidence belongs to another subject")
        _require(isinstance(observation.get("predicate"), str) and observation["predicate"], "STUDY_OBSERVATION_INVALID", f"observation {oid} requires a predicate")
        _require(isinstance(observation.get("claim_ceiling"), str) and observation["claim_ceiling"].startswith("OBSERVED_"), "STUDY_OBSERVATION_INVALID", f"observation {oid} requires an observed claim ceiling")

    capabilities = study.get("candidate_capabilities")
    _require(isinstance(capabilities, list) and capabilities, "STUDY_CAPABILITIES_MISSING", "study requires candidate capabilities")
    capability_ids: set[str] = set()
    for capability in capabilities:
        _require(isinstance(capability, dict), "STUDY_CAPABILITY_INVALID", "candidate capabilities must be objects")
        capability_id = capability.get("id")
        _require(isinstance(capability_id, str) and capability_id and capability_id not in capability_ids, "STUDY_CAPABILITY_INVALID", "candidate capability ids must be unique non-empty strings")
        capability_ids.add(capability_id)
        _require(capability.get("disposition") == "UNKNOWN", "OBSERVATION_SELF_ADMISSION_REFUSED", "observation-stage capability dispositions must remain UNKNOWN")


def _verify_subject(subject: dict[str, Any], root: Path | None) -> dict[str, Any]:
    sid = subject["id"]
    if root is None:
        if subject.get("exact_sha") and subject.get("artifacts"):
            return {
                "id": sid,
                "state": "PARTIAL_ALIVE",
                "reason": "BLOCKED:SUBJECT_TREE_NOT_MATERIALIZED",
                "exact_sha": subject.get("exact_sha"),
                "verified_artifacts": 0,
                "declared_artifacts": len(subject.get("artifacts", [])),
            }
        return {
            "id": sid,
            "state": "UNKNOWN",
            "reason": "BLOCKED:SUBJECT_IDENTITY_UNKNOWN",
            "exact_sha": subject.get("exact_sha"),
            "verified_artifacts": 0,
            "declared_artifacts": len(subject.get("artifacts", [])),
        }

    _require(root.is_dir(), "SUBJECT_ROOT_MISSING", f"subject root does not exist: {root}", {"subject": sid})
    expected_sha = subject.get("exact_sha")
    _require(expected_sha is not None, "SUBJECT_IDENTITY_UNKNOWN", f"materialized subject {sid} has no exact SHA")
    actual_sha = command(["git", "rev-parse", "HEAD"], root)
    _require(actual_sha == expected_sha, "SOURCE_IDENTITY_MISMATCH", f"subject {sid} is checked out at the wrong commit", {"expected": expected_sha, "actual": actual_sha})
    dirty = command(["git", "status", "--porcelain=v1", "--untracked-files=no"], root)
    _require(not dirty, "SOURCE_TREE_DIRTY", f"subject {sid} has tracked modifications", {"status": dirty.splitlines()})

    verified = 0
    for artifact in subject.get("artifacts", []):
        path = artifact.get("path")
        _require(isinstance(path, str) and path and not Path(path).is_absolute() and ".." not in Path(path).parts, "STUDY_EVIDENCE_INVALID", f"artifact path is unsafe: {path!r}")
        _require((root / path).is_file(), "SUBJECT_ARTIFACT_MISSING", f"subject {sid} is missing {path}")
        actual_blob = command(["git", "rev-parse", f"HEAD:{path}"], root)
        _require(actual_blob == artifact["git_blob_sha1"], "SUBJECT_ARTIFACT_MISMATCH", f"subject {sid} artifact differs: {path}", {"expected": artifact["git_blob_sha1"], "actual": actual_blob})
        verified += 1
    return {
        "id": sid,
        "state": "ALIVE",
        "reason": "ALIVE:EXACT_SUBJECT_ARTIFACTS_VERIFIED",
        "exact_sha": actual_sha,
        "verified_artifacts": verified,
        "declared_artifacts": verified,
    }


def _conflicts(study: dict[str, Any]) -> list[dict[str, Any]]:
    one = {item["predicate"] for item in study.get("controlled_predicates", []) if item.get("cardinality") == "one"}
    groups: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for observation in study.get("observations", []):
        key = (observation["subject"], observation["predicate"])
        groups.setdefault(key, []).append(observation)

    conflicts: list[dict[str, Any]] = []
    for (subject, predicate), observations in sorted(groups.items()):
        values = {json.dumps(item.get("value"), sort_keys=True, separators=(",", ":")) for item in observations}
        if predicate in one and len(values) > 1:
            conflicts.append(
                {
                    "subject": subject,
                    "predicate": predicate,
                    "cardinality": "one",
                    "observation_ids": sorted(item["id"] for item in observations),
                    "values": sorted(
                        (json.loads(value) for value in values),
                        key=lambda value: json.dumps(value, sort_keys=True),
                    ),
                    "resolution": "UNRESOLVED",
                }
            )
    return conflicts


def observe(study: dict[str, Any], roots: dict[str, Path] | None = None) -> dict[str, Any]:
    validate_study(study)
    roots = roots or {}
    subject_ids = {subject["id"] for subject in study["subjects"]}
    _require(set(roots) <= subject_ids, "SUBJECT_ROOT_INVALID", "subject-root mapping references an undeclared subject", {"unknown": sorted(set(roots) - subject_ids)})
    subject_reports = [_verify_subject(subject, roots.get(subject["id"])) for subject in study["subjects"]]
    blocked = sorted(report["reason"] for report in subject_reports if report["state"] != "ALIVE")
    states = {report["state"] for report in subject_reports}
    standing = "ALIVE" if states == {"ALIVE"} else "PARTIAL_ALIVE" if states & {"ALIVE", "PARTIAL_ALIVE"} else "UNKNOWN"
    study_digest = digest(study)
    core = {
        "schema": OBSERVATION_SCHEMA,
        "study_id": study["study_id"],
        "authority_state": "NO_AUTHORITY",
        "claim_ceiling": "OBSERVED",
        "standing": standing,
        "semantic_scope": study["semantic_scope"],
        "study_sha256": study_digest,
        "subjects": sorted(subject_reports, key=lambda item: item["id"]),
        "conflicts": _conflicts(study),
        "observations": sorted(study.get("observations", []), key=lambda item: item["id"]),
        "candidate_capabilities": sorted(study.get("candidate_capabilities", []), key=lambda item: item["id"]),
        "admitted": [],
        "executed": ["git rev-parse HEAD", "git status --porcelain=v1", "git rev-parse HEAD:<artifact>"],
        "blocked": blocked,
        "refused": [],
    }
    artifact_digest = digest(core)
    return {
        "core": core,
        "receipt": {
            "schema": RECEIPT_SCHEMA,
            "algorithm": "SHA-256",
            "artifact_digest": artifact_digest,
            "epistemic_class": "OBSERVED",
            "authority": False,
            "parent_digests": [study_digest],
        },
    }


def _verify_observation(report: dict[str, Any]) -> None:
    core = report.get("core", {})
    _require(core.get("schema") == OBSERVATION_SCHEMA, "OBSERVATION_SCHEMA_INVALID", "observation report schema is invalid")
    _require(core.get("authority_state") == "NO_AUTHORITY" and core.get("claim_ceiling") == "OBSERVED", "OBSERVATION_SELF_ADMISSION_REFUSED", "observation core must remain non-authoritative")
    _require(core.get("admitted") == [], "OBSERVATION_SELF_ADMISSION_REFUSED", "observation core cannot admit capabilities")
    _require(all(item.get("disposition") == "UNKNOWN" for item in core.get("candidate_capabilities", [])), "OBSERVATION_SELF_ADMISSION_REFUSED", "observation capability dispositions must remain UNKNOWN")
    study_digest = core.get("study_sha256")
    _require(bool(HEX64.fullmatch(str(study_digest or ""))), "OBSERVATION_RECEIPT_INVALID", "observation study digest is invalid")
    receipt = report.get("receipt", {})
    _require(receipt.get("schema") == RECEIPT_SCHEMA, "OBSERVATION_RECEIPT_INVALID", "observation receipt schema is invalid")
    _require(receipt.get("algorithm") == "SHA-256" and receipt.get("epistemic_class") == "OBSERVED", "OBSERVATION_RECEIPT_INVALID", "observation receipt kind or algorithm is invalid")
    _require(receipt.get("artifact_digest") == digest(core), "OBSERVATION_RECEIPT_INVALID", "observation receipt digest does not match report core")
    _require(receipt.get("authority") is False, "OBSERVATION_SELF_ADMISSION_REFUSED", "observation receipt must not grant authority")
    _require(receipt.get("parent_digests") == [study_digest], "OBSERVATION_RECEIPT_INVALID", "observation receipt must bind exactly the study digest")


def admit(observation: dict[str, Any], contract: dict[str, Any]) -> dict[str, Any]:
    _verify_observation(observation)
    _require(contract.get("schema") == CONTRACT_SCHEMA, "ADMISSION_CONTRACT_INVALID", "admission contract schema is invalid")
    core = observation["core"]
    _require(core.get("authority_state") == "NO_AUTHORITY", "ADMISSION_INPUT_INVALID", "admission must consume a NO_AUTHORITY observation")
    _require(contract.get("study_id") == core.get("study_id"), "ADMISSION_SUBJECT_MISMATCH", "contract study_id differs from observation")
    observation_digest = observation["receipt"]["artifact_digest"]
    _require(contract.get("observation_receipt_digest") == observation_digest, "ADMISSION_RECEIPT_MISMATCH", "contract does not bind the observation receipt")

    scope = contract.get("semantic_scope", {})
    _require(scope.get("mode") == "bounded-observable-surfaces", "RICE_SCOPE_UNBOUNDED", "admission scope must be bounded-observable-surfaces")
    _require(scope.get("universal_equivalence_claimed") is False, "RICE_SCOPE_UNBOUNDED", "universal semantic equivalence cannot be admitted")
    authority = contract.get("authority", {})
    _require(isinstance(authority.get("id"), str) and authority.get("id"), "ADMISSION_AUTHORITY_MISSING", "explicit authority id is required")
    _require(bool(HEX64.fullmatch(str(authority.get("digest", "")))), "ADMISSION_AUTHORITY_MISSING", "explicit authority digest must be 64 lowercase hex")

    observed_ids = {item["id"] for item in core.get("observations", [])}
    candidate_ids = {item["id"] for item in core.get("candidate_capabilities", [])}
    capabilities = contract.get("capabilities")
    _require(isinstance(capabilities, list) and capabilities, "ADMISSION_CAPABILITIES_MISSING", "admission requires capabilities")
    admitted_ids: set[str] = set()
    dispositions: set[str] = set()
    for capability in capabilities:
        cid = capability.get("id")
        _require(cid in candidate_ids and cid not in admitted_ids, "ADMISSION_CAPABILITY_INVALID", f"capability is absent or duplicated: {cid}")
        admitted_ids.add(cid)
        disposition = capability.get("disposition")
        _require(disposition in DISPOSITIONS, "ADMISSION_DISPOSITION_UNKNOWN", f"capability {cid} lacks a final disposition")
        dispositions.add(disposition)
        evidence = capability.get("evidence_ids")
        _require(isinstance(evidence, list) and evidence and set(evidence) <= observed_ids, "ADMISSION_EVIDENCE_INVALID", f"capability {cid} has missing evidence")
        surfaces = capability.get("observable_surfaces")
        _require(isinstance(surfaces, list) and surfaces and set(surfaces) <= SURFACES, "ADMISSION_SCOPE_INVALID", f"capability {cid} has invalid observable surfaces")

    _require(admitted_ids == candidate_ids, "ADMISSION_CLOSURE_INCOMPLETE", "every observed candidate capability requires exactly one final disposition")
    _require(contract.get("require_refusal") is True, "ADMISSION_REFUSAL_REQUIRED", "the OSTAR trial must explicitly require a refusal")
    _require("REFUSED" in dispositions, "SCOPING_FAILURE_NO_REFUSAL", "required-refusal study contains no REFUSED capability")
    required_values = contract.get("required_dispositions")
    _require(isinstance(required_values, list) and len(required_values) == len(DISPOSITIONS), "ADMISSION_DISPOSITION_COVERAGE_INCOMPLETE", "the OSTAR trial must declare all five final dispositions")
    required = set(required_values)
    _require(required == DISPOSITIONS and dispositions == DISPOSITIONS, "ADMISSION_DISPOSITION_COVERAGE_INCOMPLETE", "PRESERVED, SUBSUMED, REPLACED, ARCHIVED, and REFUSED must all be exercised", {"required": sorted(required), "observed": sorted(dispositions)})

    admission_core = {
        "schema": ADMISSION_SCHEMA,
        "study_id": core["study_id"],
        "authority_state": "ADMITTED_CANDIDATE",
        "claim_ceiling": "SCHEMA_VALIDATED",
        "semantic_scope": scope,
        "authority": authority,
        "observation_receipt_digest": observation_digest,
        "capabilities": sorted(capabilities, key=lambda item: item["id"]),
        "disposition_coverage": sorted(dispositions),
        "standing": "PARTIAL_ALIVE",
        "actuation_authority": False,
    }
    admission_digest = digest(admission_core)
    return {
        "core": admission_core,
        "receipt": {
            "schema": RECEIPT_SCHEMA,
            "algorithm": "SHA-256",
            "artifact_digest": admission_digest,
            "epistemic_class": "CONSTRUCTED",
            "authority": False,
            "parent_digests": sorted([observation_digest, authority["digest"]]),
        },
    }


def replay(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    _verify_observation(left)
    _verify_observation(right)
    left_digest = left["receipt"]["artifact_digest"]
    right_digest = right["receipt"]["artifact_digest"]
    match = left_digest == right_digest and left["core"] == right["core"]
    return {
        "schema": "ggen.legacy.authority-vacuum.replay.v1",
        "status": "REPLAY_MATCH" if match else "REPLAY_DIFFERENCE",
        "left_digest": left_digest,
        "right_digest": right_digest,
    }


def parse_roots(values: list[str]) -> dict[str, Path]:
    roots: dict[str, Path] = {}
    for value in values:
        _require("=" in value, "SUBJECT_ROOT_INVALID", "--subject-root must be id=path")
        sid, raw_path = value.split("=", 1)
        _require(sid and raw_path and sid not in roots, "SUBJECT_ROOT_INVALID", "subject root mappings must be unique")
        roots[sid] = Path(raw_path).resolve()
    return roots


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    observe_parser = sub.add_parser("observe")
    observe_parser.add_argument("--study", required=True, type=Path)
    observe_parser.add_argument("--subject-root", action="append", default=[])
    observe_parser.add_argument("--out", required=True, type=Path)
    admit_parser = sub.add_parser("admit")
    admit_parser.add_argument("--observation", required=True, type=Path)
    admit_parser.add_argument("--contract", required=True, type=Path)
    admit_parser.add_argument("--out", required=True, type=Path)
    replay_parser = sub.add_parser("replay")
    replay_parser.add_argument("--left", required=True, type=Path)
    replay_parser.add_argument("--right", required=True, type=Path)
    replay_parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)

    try:
        if args.command == "observe":
            result = observe(load_json(args.study, "STUDY_INVALID"), parse_roots(args.subject_root))
            write_json(args.out, result)
        elif args.command == "admit":
            result = admit(load_json(args.observation, "OBSERVATION_INVALID"), load_json(args.contract, "ADMISSION_CONTRACT_INVALID"))
            write_json(args.out, result)
        else:
            result = replay(load_json(args.left, "REPLAY_INPUT_INVALID"), load_json(args.right, "REPLAY_INPUT_INVALID"))
            if args.out:
                write_json(args.out, result)
        print(json.dumps(result, sort_keys=True))
        return 0 if result.get("status") != "REPLAY_DIFFERENCE" else 1
    except AuthorityVacuumError as exc:
        print(json.dumps(exc.as_json(), sort_keys=True), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
