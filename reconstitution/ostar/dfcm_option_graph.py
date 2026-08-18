#!/usr/bin/env python3
"""DfCM preservation graph for the OSTAR authority-vacuum study.

This module never selects a semantic winner. It enumerates every disposition
vector that satisfies the already-admitted structural closure law, supports
reversible evidence pruning, receipts the resulting graph, and refuses direct
selection without a separate admission authority.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import sys
from pathlib import Path
from typing import Any

GRAPH_SCHEMA = "ggen.legacy.dfcm-option-graph.v1"
CONSTRAINT_SCHEMA = "ggen.legacy.dfcm-constraints.v1"
RECEIPT_SCHEMA = "ggen.legacy.dfcm-option-graph.receipt.v1"
DISPOSITIONS = ("PRESERVED", "SUBSUMED", "REPLACED", "ARCHIVED", "REFUSED")


class DfcmError(RuntimeError):
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


def _require(condition: bool, code: str, message: str, detail: dict[str, Any] | None = None) -> None:
    if not condition:
        raise DfcmError(code, message, detail)


def load_json(path: Path, code: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise DfcmError(code, f"cannot read {path}: {exc}") from exc
    _require(isinstance(value, dict), code, f"{path} must contain a JSON object")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_bytes(value))


def _capability_ids(study: dict[str, Any]) -> list[str]:
    _require(study.get("initial_authority_state") == "NO_AUTHORITY", "DFCM_AUTHORITY_ALREADY_SELECTED", "DfCM preserve begins only from NO_AUTHORITY")
    _require(study.get("direct_actuation") is False, "DFCM_ACTUATION_REFUSED", "DfCM option exploration must disable direct actuation")
    _require("canonical_subject" not in study, "DFCM_CANONICAL_SUBJECT_REFUSED", "DfCM exploration cannot receive a canonical subject")
    candidates = study.get("candidate_capabilities")
    _require(isinstance(candidates, list) and candidates, "DFCM_CAPABILITIES_MISSING", "candidate_capabilities must be a non-empty list")
    ids: list[str] = []
    for candidate in candidates:
        _require(isinstance(candidate, dict), "DFCM_CAPABILITY_INVALID", "candidate capabilities must be objects")
        cid = candidate.get("id")
        _require(isinstance(cid, str) and cid.strip(), "DFCM_CAPABILITY_INVALID", "candidate capability id must be non-empty")
        _require(candidate.get("disposition") == "UNKNOWN", "DFCM_PREMATURE_DISPOSITION_REFUSED", f"{cid} already has a final disposition")
        ids.append(cid)
    _require(len(ids) == len(set(ids)), "DFCM_CAPABILITY_INVALID", "candidate capability ids must be unique")
    return sorted(ids)


def _option(study_digest: str, capability_ids: list[str], values: tuple[str, ...]) -> dict[str, Any]:
    assignments = [{"capability": cid, "disposition": disposition} for cid, disposition in zip(capability_ids, values, strict=True)]
    body = {"study_sha256": study_digest, "assignments": assignments}
    option_digest = digest(body)
    return {
        "option_id": f"dfcm-{option_digest[:20]}",
        "option_sha256": option_digest,
        "assignments": assignments,
        "selection_authority": False,
        "actuation_authority": False,
    }


def construct(study: dict[str, Any]) -> dict[str, Any]:
    capability_ids = _capability_ids(study)
    study_digest = digest(study)
    options = []
    required = set(DISPOSITIONS)
    for values in itertools.product(DISPOSITIONS, repeat=len(capability_ids)):
        if set(values) != required:
            continue
        options.append(_option(study_digest, capability_ids, values))
    options.sort(key=lambda item: item["option_id"])
    core = {
        "schema": GRAPH_SCHEMA,
        "study_id": study.get("study_id"),
        "study_sha256": study_digest,
        "dfcm_phase": "PRESERVE",
        "authority_state": "NO_AUTHORITY",
        "selection_state": "UNSELECTED",
        "claim_ceiling": "SYNTACTIC_CLOSURE_ONLY",
        "capability_order": capability_ids,
        "required_dispositions": list(DISPOSITIONS),
        "option_count": len(options),
        "options": options,
        "constraints": [],
        "pruned_option_count": 0,
        "actuation_authority": False,
    }
    return _wrap(core, [study_digest])


def _wrap(core: dict[str, Any], parents: list[str]) -> dict[str, Any]:
    return {
        "core": core,
        "receipt": {
            "schema": RECEIPT_SCHEMA,
            "algorithm": "SHA-256",
            "artifact_digest": digest(core),
            "epistemic_class": "CONSTRUCTED",
            "authority": False,
            "parent_digests": sorted(parents),
        },
    }


def verify(graph: dict[str, Any]) -> None:
    core = graph.get("core", {})
    receipt = graph.get("receipt", {})
    _require(core.get("schema") == GRAPH_SCHEMA, "DFCM_GRAPH_SCHEMA_INVALID", "option graph schema is invalid")
    _require(core.get("authority_state") == "NO_AUTHORITY", "DFCM_AUTHORITY_ESCALATION", "option graph must remain NO_AUTHORITY")
    _require(core.get("selection_state") == "UNSELECTED", "DFCM_PREMATURE_SELECTION", "option graph may not select a winner")
    _require(core.get("actuation_authority") is False, "DFCM_ACTUATION_REFUSED", "option graph may not actuate")
    _require(receipt.get("schema") == RECEIPT_SCHEMA and receipt.get("algorithm") == "SHA-256", "DFCM_RECEIPT_INVALID", "receipt schema or algorithm is invalid")
    _require(receipt.get("authority") is False, "DFCM_AUTHORITY_ESCALATION", "option-graph receipt cannot grant authority")
    _require(receipt.get("artifact_digest") == digest(core), "DFCM_RECEIPT_INVALID", "receipt does not match graph core")
    capability_ids = core.get("capability_order")
    _require(isinstance(capability_ids, list) and capability_ids == sorted(capability_ids), "DFCM_CAPABILITY_ORDER_INVALID", "capability order must be deterministic")
    options = core.get("options")
    _require(isinstance(options, list) and core.get("option_count") == len(options), "DFCM_OPTION_COUNT_INVALID", "option_count does not match options")
    for option in options:
        assignments = option.get("assignments", [])
        _require([item.get("capability") for item in assignments] == capability_ids, "DFCM_OPTION_INVALID", "option capability order differs")
        dispositions = [item.get("disposition") for item in assignments]
        _require(set(dispositions) == set(DISPOSITIONS), "DFCM_OPTION_INVALID", "option does not exercise all five final dispositions")
        _require(option.get("selection_authority") is False and option.get("actuation_authority") is False, "DFCM_OPTION_AUTHORITY_INVALID", "constructed options remain inert")
        option_body = {"study_sha256": core.get("study_sha256"), "assignments": assignments}
        option_digest = digest(option_body)
        _require(option.get("option_sha256") == option_digest and option.get("option_id") == f"dfcm-{option_digest[:20]}", "DFCM_OPTION_DIGEST_INVALID", "option identity is not deterministic")


def prune(graph: dict[str, Any], constraints: dict[str, Any]) -> dict[str, Any]:
    verify(graph)
    _require(constraints.get("schema") == CONSTRAINT_SCHEMA, "DFCM_CONSTRAINT_SCHEMA_INVALID", "constraint schema is invalid")
    _require(constraints.get("selection_authority") is False, "DFCM_SELECTION_AUTHORITY_REFUSED", "pruning input cannot grant selection authority")
    _require(constraints.get("actuation_authority") is False, "DFCM_ACTUATION_REFUSED", "pruning input cannot grant actuation authority")
    rules = constraints.get("rules")
    _require(isinstance(rules, list), "DFCM_CONSTRAINTS_INVALID", "constraint rules must be a list")
    capability_ids = set(graph["core"]["capability_order"])
    normalized = []
    for rule in rules:
        _require(isinstance(rule, dict), "DFCM_CONSTRAINT_INVALID", "constraint rules must be objects")
        capability = rule.get("capability")
        allowed = rule.get("allowed_dispositions")
        _require(capability in capability_ids, "DFCM_CONSTRAINT_INVALID", f"unknown capability {capability!r}")
        _require(isinstance(allowed, list) and allowed and set(allowed) <= set(DISPOSITIONS), "DFCM_CONSTRAINT_INVALID", f"invalid allowed dispositions for {capability}")
        normalized.append({"capability": capability, "allowed_dispositions": sorted(set(allowed))})
    normalized.sort(key=lambda item: item["capability"])

    def keeps(option: dict[str, Any]) -> bool:
        assignment = {item["capability"]: item["disposition"] for item in option["assignments"]}
        return all(assignment[rule["capability"]] in set(rule["allowed_dispositions"]) for rule in normalized)

    retained = [option for option in graph["core"]["options"] if keeps(option)]
    core = dict(graph["core"])
    core["dfcm_phase"] = "FENCE"
    core["options"] = retained
    core["option_count"] = len(retained)
    core["constraints"] = normalized
    core["pruned_option_count"] = len(graph["core"]["options"]) - len(retained)
    core["selection_state"] = "UNSELECTED"
    core["actuation_authority"] = False
    return _wrap(core, [graph["receipt"]["artifact_digest"], digest(constraints)])


def frontier(graph: dict[str, Any]) -> dict[str, Any]:
    """Rank reversible evidence targets by how much option topology they can split.

    This is a SELECT-free query. It measures the partition induced by learning one
    capability's final disposition, returns every tied maximal target, and grants
    no authority to acquire evidence or choose a disposition.
    """
    verify(graph)
    core = graph["core"]
    options = core["options"]
    total = len(options)
    _require(total > 0, "DFCM_FRONTIER_EMPTY", "no retained options remain to partition")
    records: list[dict[str, Any]] = []
    for capability in core["capability_order"]:
        counts = {disposition: 0 for disposition in DISPOSITIONS}
        for option in options:
            assignment = {item["capability"]: item["disposition"] for item in option["assignments"]}
            counts[assignment[capability]] += 1
        nonzero = [count for count in counts.values() if count]
        probabilities = [count / total for count in nonzero]
        entropy = -sum(probability * math.log2(probability) for probability in probabilities)
        worst_case_remaining = max(nonzero)
        records.append(
            {
                "capability": capability,
                "support_counts": counts,
                "supported_dispositions": len(nonzero),
                "entropy_bits": round(entropy, 12),
                "worst_case_remaining": worst_case_remaining,
                "guaranteed_prunable": total - worst_case_remaining,
                "evidence_authority": False,
                "selection_authority": False,
                "actuation_authority": False,
            }
        )
    # Minimize the largest surviving partition first; entropy breaks any remaining
    # tie. Preserve every equal best target instead of selecting one by name.
    best_worst = min(record["worst_case_remaining"] for record in records)
    candidates = [record for record in records if record["worst_case_remaining"] == best_worst]
    best_entropy = max(record["entropy_bits"] for record in candidates)
    maximal = sorted(
        record["capability"]
        for record in candidates
        if record["entropy_bits"] == best_entropy
    )
    return {
        "schema": "ggen.legacy.dfcm-evidence-frontier.v1",
        "option_graph_digest": graph["receipt"]["artifact_digest"],
        "option_count": total,
        "targets": records,
        "maximal_information_targets": maximal,
        "selection_state": "UNSELECTED",
        "claim_ceiling": "EVIDENCE_PARTITION_ONLY",
        "evidence_authority": False,
        "selection_authority": False,
        "actuation_authority": False,
    }


def select(_: dict[str, Any], option_id: str) -> None:
    raise DfcmError(
        "DFCM_SELECTION_REQUIRES_ADMISSION",
        "DfCM construction preserves options; selecting a semantic winner requires a separate explicit authority contract",
        {"option_id": option_id},
    )


def replay(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    verify(left)
    verify(right)
    match = left["receipt"]["artifact_digest"] == right["receipt"]["artifact_digest"] and left["core"] == right["core"]
    return {
        "schema": "ggen.legacy.dfcm-option-graph.replay.v1",
        "status": "REPLAY_MATCH" if match else "REPLAY_DIFFERENCE",
        "left_digest": left["receipt"]["artifact_digest"],
        "right_digest": right["receipt"]["artifact_digest"],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    construct_parser = sub.add_parser("construct")
    construct_parser.add_argument("--study", required=True, type=Path)
    construct_parser.add_argument("--out", required=True, type=Path)
    prune_parser = sub.add_parser("prune")
    prune_parser.add_argument("--graph", required=True, type=Path)
    prune_parser.add_argument("--constraints", required=True, type=Path)
    prune_parser.add_argument("--out", required=True, type=Path)
    frontier_parser = sub.add_parser("frontier")
    frontier_parser.add_argument("--graph", required=True, type=Path)
    select_parser = sub.add_parser("select")
    select_parser.add_argument("--graph", required=True, type=Path)
    select_parser.add_argument("--option-id", required=True)
    replay_parser = sub.add_parser("replay")
    replay_parser.add_argument("--left", required=True, type=Path)
    replay_parser.add_argument("--right", required=True, type=Path)

    args = parser.parse_args(argv)
    try:
        if args.command == "construct":
            result = construct(load_json(args.study, "DFCM_STUDY_INVALID"))
            write_json(args.out, result)
        elif args.command == "prune":
            result = prune(load_json(args.graph, "DFCM_GRAPH_INVALID"), load_json(args.constraints, "DFCM_CONSTRAINTS_INVALID"))
            write_json(args.out, result)
        elif args.command == "frontier":
            result = frontier(load_json(args.graph, "DFCM_GRAPH_INVALID"))
        elif args.command == "select":
            select(load_json(args.graph, "DFCM_GRAPH_INVALID"), args.option_id)
            raise AssertionError("unreachable")
        else:
            result = replay(load_json(args.left, "DFCM_REPLAY_INPUT_INVALID"), load_json(args.right, "DFCM_REPLAY_INPUT_INVALID"))
        print(json.dumps(result, sort_keys=True))
        return 0 if result.get("status") != "REPLAY_DIFFERENCE" else 1
    except DfcmError as exc:
        print(json.dumps(exc.as_json(), sort_keys=True), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
