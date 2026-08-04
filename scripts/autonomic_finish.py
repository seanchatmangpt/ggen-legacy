#!/usr/bin/env python3
"""Deterministic, non-actuating conversation-to-projection foundry."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any

PROCESS_STATES = {
    "observed", "admitted", "inferred", "proposed", "decided",
    "blocked", "unsupported", "refused",
}
STANDINGS = {
    "UNKNOWN", "PARTIAL_ALIVE", "ALIVE", "BLOCKED",
    "BUILD_BROKEN", "UNSUPPORTED",
}
PROJECTIONS = {
    "architecture", "working_backwards", "claude", "ppddl", "gaps",
}


class Refusal(ValueError):
    """Typed admission refusal."""


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def validate(bundle: dict[str, Any]) -> dict[str, Any]:
    subject = bundle.get("subject")
    if not isinstance(subject, dict) or not subject.get("id"):
        raise Refusal("REFUSED:MISSING_SUBJECT_ID")
    concepts = bundle.get("concepts")
    if not isinstance(concepts, list) or not concepts:
        raise Refusal("REFUSED:MISSING_CONCEPTS")

    seen: set[str] = set()
    normalized = []
    for raw in concepts:
        if not isinstance(raw, dict) or not raw.get("id"):
            raise Refusal("REFUSED:INVALID_CONCEPT")
        cid = str(raw["id"])
        if cid in seen:
            raise Refusal(f"REFUSED:DUPLICATE_CONCEPT:{cid}")
        seen.add(cid)
        state = raw.get("state", "observed")
        if state not in PROCESS_STATES:
            raise Refusal(f"REFUSED:UNKNOWN_PROCESS_STATE:{state}")
        standing = raw.get("standing", "UNKNOWN")
        if standing not in STANDINGS and not str(standing).startswith("REFUSED:"):
            raise Refusal(f"REFUSED:UNKNOWN_STANDING:{standing}")
        deps = sorted({str(x) for x in raw.get("depends_on", [])})
        normalized.append({
            "id": cid,
            "label": str(raw.get("label", cid)),
            "kind": str(raw.get("kind", "concept")),
            "state": state,
            "standing": standing,
            "summary": str(raw.get("summary", "")),
            "evidence": sorted(str(x) for x in raw.get("evidence", [])),
            "depends_on": deps,
            "decision": raw.get("decision"),
            "authority": str(raw.get("authority", "SELECT_ONLY")),
        })

    unknown_deps = sorted({d for c in normalized for d in c["depends_on"] if d not in seen})
    if unknown_deps:
        raise Refusal("REFUSED:UNKNOWN_DEPENDENCY:" + ",".join(unknown_deps))

    requested = bundle.get("projections", sorted(PROJECTIONS))
    if not isinstance(requested, list) or not set(requested).issubset(PROJECTIONS):
        raise Refusal("REFUSED:UNKNOWN_PROJECTION")

    return {
        "schema": "ggen-legacy.autonomic.v1",
        "subject": {
            "id": str(subject["id"]),
            "source": str(subject.get("source", "conversation")),
            "base": str(subject.get("base", "UNKNOWN")),
        },
        "concepts": sorted(normalized, key=lambda c: c["id"]),
        "projections": sorted(set(requested)),
        "constraints": sorted(str(x) for x in bundle.get("constraints", [])),
    }


def gaps(graph: dict[str, Any]) -> list[dict[str, Any]]:
    result = []
    for c in graph["concepts"]:
        if c["state"] in {"proposed", "inferred", "blocked"} or c["decision"] is None:
            result.append({
                "concept": c["id"],
                "state": c["state"],
                "standing": c["standing"],
                "required_decision": c["decision"] or "admit, reject, or refine this concept",
            })
    return result


def architecture(graph: dict[str, Any]) -> str:
    lines = ["# Canonical Architecture", "", f"Subject: `{graph['subject']['id']}`", "", "## Concepts", ""]
    for c in graph["concepts"]:
        deps = ", ".join(f"`{d}`" for d in c["depends_on"]) or "none"
        lines += [f"### {c['label']} (`{c['id']}`)", "", c["summary"] or "No summary admitted.", "",
                  f"- Kind: `{c['kind']}`", f"- State: `{c['state']}`", f"- Standing: `{c['standing']}`",
                  f"- Authority: `{c['authority']}`", f"- Depends on: {deps}", ""]
    return "\n".join(lines)


def working_backwards(graph: dict[str, Any]) -> str:
    decided = [c for c in graph["concepts"] if c["state"] == "decided"]
    return "\n".join([
        "# Working Backwards Brief", "",
        "## Future press release", "",
        "The ggen-legacy autonomic foundry now converts admitted design observations into a canonical graph, bounded Claude operator instructions, a planning problem, deterministic projections, and an explicit gap ledger without executing generated work.", "",
        "## Customer", "", "A solution architect who needs to turn a large design conversation into the smallest executable decision set.", "",
        "## Accepted foundations", "",
        *([f"- **{c['label']}** — {c['summary']}" for c in decided] or ["- No concepts have reached `decided` state."]), "",
        "## FAQ", "",
        "### Does the foundry finish ambiguous decisions?", "No. It exposes them in `GAPS.json`.", "",
        "### Does it run generated commands or edit repositories?", "No. It is a construction-only production cell.", "",
        "### What is completion?", "Byte-stable projections, a complete receipt, and a finite unresolved decision set.", "",
    ])


def claude_contract(graph: dict[str, Any]) -> str:
    return "\n".join([
        "# Claude Reference Operator Contract", "",
        "## Sequence", "", "策 → 標準作業 → 실행 → 証", "",
        "## Authority", "",
        "- `策`: inspect and propose; `SELECT_ONLY`.",
        "- `標準作業`: construct bounded plans and projections.",
        "- `실행`: prohibited in this foundry; emit a BRCE intent only.",
        "- `証`: independently classify evidence without self-certification.", "",
        "## Mandatory states", "",
        "Use only `UNKNOWN`, `PARTIAL_ALIVE`, `ALIVE`, `BLOCKED`, `BUILD_BROKEN`, `UNSUPPORTED`, or `REFUSED:<CODE>`.", "",
        "## Stop conditions", "",
        "Stop on subject drift, missing authority, unknown dependencies, scope expansion, absent verifier, WIP greater than one crown, or a required human/spiritual decision.", "",
        "## Current subject", "", f"`{graph['subject']['id']}`", "",
    ])


def ppddl_problem(graph: dict[str, Any], unresolved: list[dict[str, Any]]) -> str:
    objects = " ".join(c["id"].replace(".", "-") for c in graph["concepts"])
    unresolved_ids = {g["concept"] for g in unresolved}
    init = []
    for c in graph["concepts"]:
        token = c["id"].replace(".", "-")
        init.append(f"    (observed {token})")
        if c["id"] not in unresolved_ids:
            init.append(f"    (resolved {token})")
    return "\n".join([
        "(define (problem conversation-foundry)",
        "  (:domain autonomic-foundry)",
        f"  (:objects {objects} - concept)",
        "  (:init", *init, "    (wip-free)", "  )",
        "  (:goal (and", *[f"    (resolved {c['id'].replace('.', '-')})" for c in graph["concepts"]], "    (wip-free)", "  ))", ")", "",
    ])


def atomic_write(root: Path, relative: str, data: bytes) -> None:
    target = (root / relative).resolve()
    resolved_root = root.resolve()
    if target != resolved_root and resolved_root not in target.parents:
        raise Refusal("REFUSED:OUTPUT_ESCAPE")
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".foundry-", dir=str(target.parent))
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
        os.replace(tmp, target)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def manufacture(bundle: dict[str, Any], output: Path) -> dict[str, Any]:
    graph = validate(bundle)
    unresolved = gaps(graph)
    products: dict[str, bytes] = {"canonical-graph.json": canonical_json(graph)}
    if "architecture" in graph["projections"]:
        products["ARCHITECTURE.md"] = (architecture(graph) + "\n").encode()
    if "working_backwards" in graph["projections"]:
        products["WORKING_BACKWARDS.md"] = (working_backwards(graph) + "\n").encode()
    if "claude" in graph["projections"]:
        products["CLAUDE.md"] = (claude_contract(graph) + "\n").encode()
    if "ppddl" in graph["projections"]:
        products["ppddl/problem.pddl"] = ppddl_problem(graph, unresolved).encode()
    if "gaps" in graph["projections"]:
        products["GAPS.json"] = canonical_json({"gaps": unresolved})

    manifest = {path: digest(data) for path, data in sorted(products.items())}
    receipt = {
        "schema": "ggen-legacy.autonomic.receipt.v1",
        "subject": graph["subject"],
        "claim_ceiling": "DETERMINISTIC_CONVERSATION_PROJECTION_ONLY",
        "input_sha256": digest(canonical_json(bundle)),
        "canonical_graph_sha256": manifest["canonical-graph.json"],
        "outputs": manifest,
        "gap_count": len(unresolved),
        "standing": "PARTIAL_ALIVE",
        "actuation": "OUTPUT_DIRECTORY_ONLY",
    }
    products["RECEIPT.json"] = canonical_json(receipt)

    output.mkdir(parents=True, exist_ok=True)
    for path, data in sorted(products.items()):
        atomic_write(output, path, data)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        bundle = json.loads(args.input.read_text(encoding="utf-8"))
        receipt = manufacture(bundle, args.output)
    except (OSError, json.JSONDecodeError, Refusal) as error:
        print(str(error), file=os.sys.stderr)
        return 2
    print(json.dumps(receipt, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
